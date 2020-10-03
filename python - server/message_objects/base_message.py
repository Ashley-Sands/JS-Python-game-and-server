import common.const as const
from message_objects.protocols import BaseProtocol

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class BaseMessage:

    ENDPOINT_SEND = 0
    ENDPOINT_RECEIVE = 1

    def __init__( self, data, endpoint, sent_callback=None ):
        """

        :param data:            Data to be sent
        :param sent_callback:   callback to be triggered when sent
        """
        # When overriding make sure that the super() is at the end

        # payload cache, (This should be the actual payload excluding any headers and sub protocol headers)
        self._payload = None
        self._payload_len = -1  # cached payload length

        self.endpoint = endpoint

        self._sent_callback = sent_callback
        if data is not None:
            self.set( data )

    def set( self, data ):
        """ Sets the message payload """
        raise NotImplementedError

    def get( self ):
        """
            returns the message ready to be sent/received
            if the message endpoint is send this should return bytes
            if the message endpoint is receive this should return data structure
        """
        raise NotImplementedError

    def length( self ):
        """ Gets the cached payload length.
            Payload length needs implementing in a child class
        """
        return self._payload_len

    def message_sent( self ):
        """trigger the sent callback"""
        if self.endpoint == self.ENDPOINT_SEND and self._sent_callback is not None:
            self._sent_callback( **self.get_callback_data() )

    def get_callback_data( self ):
        """Returns a dict of all params for the sent callback"""
        return {}


class BaseReceiveMessage( BaseMessage ):

    RECV_STATUS_ERROR   = -1
    RECV_STATUS_ACTIVE  = 0
    RECV_STATUS_SUCCESS = 1
    RECV_STATUS_WAIT    = 2     # waiting for next frame (fin = false on last packet)

    def __init__( self, data, from_socket ):

        self.from_socket = from_socket
        self.next_stage_key = None
        self._status = self.RECV_STATUS_ACTIVE

        super().__init__( data, BaseMessage.ENDPOINT_RECEIVE)

    @property
    def stages(self):
        """Gets a dict of stages : stage method"""
        return {}

    def set( self, pack_bytes ):
        """ Recives the messages chunk at a time,
            when None has been returned, we have finished receiving the message.
            Use status to check if the message completed successfully or not
        :param pack_bytes:
        :return: next amount of bytes to receive, or None when finished receiving message or an error has occurred
        """

        if self._status != self.RECV_STATUS_ACTIVE and self._status != self.RECV_STATUS_WAIT:
            _print("Unable to set message. Message no longer Active (Status Code:", self._status, ")")
            return None
        elif self._status == self.RECV_STATUS_WAIT:
            # return to an active state
            self._status = self.RECV_STATUS_ACTIVE

        self.next_stage_key, next_bytes = self.stages[ self.next_stage_key ]( pack_bytes )

        return next_bytes

    def status( self ):
        return self._status

    def close_connection( self ):
        raise NotImplementedError

    def accept_connection( self ):
        raise NotImplementedError

    def is_ping( self ):
        raise NotImplementedError

    def is_pong( self ):
        raise NotImplementedError

    def is_protocol_message( self ):
        return self.is_ping() or self.close_connection() or self.is_pong()

    def set_error( self ):
        self._status = self.RECV_STATUS_ERROR

    def get( self ):
        """ Get payload data structure"""
        if self._payload is None:
            return {}

        return self._payload.get_structure()

    def convert_to_send( self, sent_callback=None ):
        """Converts the message to a send message."""
        raise NotImplementedError

    def convert_to_pong( self, sent_callback=None ):
        """Gets the response pong message"""
        raise NotImplementedError


class BaseReceiveProtocolMessage( BaseProtocol, BaseReceiveMessage ):

    # Note if '_set_*' are used as stages they need overriding to return the next stage
    # and the amount of expected bytes.

    def __init__( self, data, from_socket ):

        super().__init__()
        super( BaseProtocol, self ).__init__( data, from_socket )

    def _set_opt_byte( self, byte ):

        byte = int.from_bytes( byte, byteorder=const.SOCK.BYTE_ORDER)

        self._protocol_data["acknowledgment"]   = ( byte & 0b10000000 ) > 0
        self._protocol_data["resync"]           = ( byte & 0b01000000 ) > 0
        self._protocol_data["agreement"]        = ( byte & 0b00100000 ) > 0
        self._protocol_data["acknowledged"]     = ( byte & 0b00010000 ) > 0
        self._protocol_data["opcode"]           = ( byte & 0b00001111 )

    def _set_payload_len( self, bytes ):
        self._protocol_data["payload_length"] = int.from_bytes( bytes, const.SOCK.BYTE_ORDER )

    def _set_frame_id( self, bytes ):
        self._protocol_data["frame_id"] = int.from_bytes( bytes, const.SOCK.BYTE_ORDER )

    def _set_time_stamp( self, bytes ):
        self._protocol_data[ "timestamp" ] = int.from_bytes( bytes, const.SOCK.BYTE_ORDER )

    def _set_payload( self, bytes ):
        raise NotImplementedError

class BaseSendMessage( BaseMessage ):

    SND_STATUS_PEND = 0
    SND_STATUS_USED = 1

    def __init__(self, data, sent_callback=None):

        self._status = self.SND_STATUS_PEND

        super().__init__(data, BaseMessage.ENDPOINT_SEND, sent_callback=sent_callback)

    def set( self, payload_data ):
        """ Set the payload data object"""
        self._payload = payload_data
        self._payload_len = payload_data.string_length()


class BaseSendProtocolMessage( BaseProtocol, BaseSendMessage ):

    def __init__( self, data, sent_callback=None ):

        super().__init__()
        super( BaseProtocol, self ).__init__( data, sent_callback=sent_callback )

    def set_protocol_data( self, ack=False, sync=False, agree=False, opcode=15 ):  # send only??
        self._protocol_data = { **self._protocol_data, **locals() }

    def set_protocol_stamp( self, frame_id, timestamp ):                           # send only??

        self._protocol_data[ "frame_id" ]  = frame_id
        self._protocol_data[ "timestamp" ] = timestamp

    def _get_opt_byte( self ):

        byte = ( self._protocol_data["acknowledgment"] << 7) + ( self._protocol_data["resync"]       << 6) +\
               ( self._protocol_data["agreement"]      << 5) + ( self._protocol_data["acknowledged"] << 4) + self._protocol_data["opcode"]

        return byte.to_bytes( 1, const.SOCK.BYTE_ORDER )

    def _get_payload_len_bytes( self ):
        return self.length().to_bytes(2, const.SOCK.BYTE_ORDER)

    def _get_frame_id_bytes( self ):
        return self._protocol_data["frame_id"].to_bytes( 4, const.SOCK.BYTE_ORDER)

    def _get_timestamp_bytes( self ):
        return self._protocol_data[ "timestamp" ].to_bytes( 4, const.SOCK.BYTE_ORDER )