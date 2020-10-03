import common.const as const
import message_objects.base_message as base_message
from message_objects.protocols import BaseWebsocketProtocol
import message_objects.payload_data_objects.payload_json_data as payload_json_data


import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

# WebSocket Protocol Standards
# https://tools.ietf.org/html/rfc6455

# Mozilla Guide
# https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers


class WebsocketReceiveMessage( BaseWebsocketProtocol, base_message.BaseReceiveProtocolMessage ):

    WS_RECV_STAGE_OPT  = "first"
    WS_RECV_STAGE_OPT2 = "second"
    WS_RECV_STAGE_PLEN = "payload_length"
    WS_RECV_STAGE_MASK = "mask"
    WS_RECV_STAGE_PAYL = "payload"

    def __init__( self, from_socket ):

        super().__init__()                                                    # init BaeWebsocketProtocol
        super( BaseWebsocketProtocol, self ).__init__( None, from_socket )    # init BaseReceiveProtocolMessage

        self.next_stage_key = self.WS_RECV_STAGE_OPT

    @property
    def stages( self ):
        return {
            self.WS_RECV_STAGE_OPT:     self.__ws_option_byte_1,
            self.WS_RECV_STAGE_OPT2:    self.__ws_option_byte_2,
            self.WS_RECV_STAGE_PLEN:    self.__ws_payload_length,
            self.WS_RECV_STAGE_MASK:    self.__ws_mask_key,
            self.WS_RECV_STAGE_PAYL:    self.__ws_payload
        }

    def close_connection( self ):
        return self._ws_protocol[ "opcode" ] == self.WS_OP_CODE_CLS

    def accept_connection( self ):
        return self.get_protocol_value("opcode") == self.SUB_OP_CODE_ACEPT and self.get_protocol_value("acknowledged")

    def is_ping( self ):
        return self._ws_protocol["opcode"] == BaseWebsocketProtocol.WS_OP_CODE_PING

    def is_pong( self ):
        return self._ws_protocol["opcode"] == BaseWebsocketProtocol.WS_OP_CODE_PONG

    def __ws_option_byte_1( self, byte ):

        byte = int.from_bytes( byte, const.SOCK.BYTE_ORDER )

        # first byte.
        # fin (1) res1/2/3 (1 each) opcode (4)
        self._ws_protocol[ "fin" ] = (byte & 0b10000000) > 0
        self._ws_protocol[ "rsv1" ] = (byte & 0b01000000) > 0
        self._ws_protocol[ "rsv2" ] = (byte & 0b00100000) > 0
        self._ws_protocol[ "rsv3" ] = (byte & 0b00010000) > 0
        self._ws_protocol[ "opcode" ] = (byte & 0b00001111)

        return self.WS_RECV_STAGE_OPT2, 1  # move onto the second byte

    def __ws_option_byte_2( self, byte ):

        byte = int.from_bytes( byte, const.SOCK.BYTE_ORDER )
        # second byte
        # use mask (1) message len (7)
        self._ws_protocol[ "use_mask" ] = (byte & 0b10000000) > 0
        self._ws_protocol[ "payload_length" ] = (byte & 0b01111111)

        # if payload len is 126 payload len is next 2 bytes
        # if payload len is 127 payload len is next 8 bytes
        # if payload < 126 move onto mask key if using next 4 bytes
        # else move onto the payload 'payload_len' bytes
        if self._ws_protocol[ "payload_length" ] == 126:
            return self.WS_RECV_STAGE_PLEN, 2
        elif self._ws_protocol[ "payload_length" ] == 127:
            return self.WS_RECV_STAGE_PLEN, 8
        else:
            if self._ws_protocol[ "use_mask" ]:
                return self.WS_RECV_STAGE_MASK, 4
            else:
                return self.WS_RECV_STAGE_PAYL, self._ws_protocol[ "payload_length" ]

    def __ws_payload_length( self, length_bytes ):

        self._ws_protocol[ "payload_length" ] = int.from_bytes( length_bytes, const.SOCK.BYTE_ORDER )

        # get mask if using other wise move onto message
        if self._ws_protocol[ "use_mask" ]:
            return self.WS_RECV_STAGE_MASK, 4
        else:
            return self.WS_RECV_STAGE_PAYL, self._ws_protocol[ "payload_length" ]

    def __ws_mask_key( self, mask_bytes ):

        self._ws_protocol[ "mask" ] = mask_bytes

        return self.WS_RECV_STAGE_PAYL, self._ws_protocol[ "payload_length" ]

    def __ws_payload( self, payload_bytes ):

        payload = b""
        if self._ws_protocol[ "mask" ] is not None:
            # unmask the payload
            for i in range( self._ws_protocol[ "payload_length" ] ):
                byte = payload_bytes[i]
                mask = self._ws_protocol[ "mask" ][ i % 4 ]
                payload += (byte ^ mask).to_bytes(1, byteorder=const.SOCK.BYTE_ORDER)
        else:
            payload = payload_bytes

        if self._ws_protocol["payload"] is None:
            self._ws_protocol["payload"] = payload
        else:
            self._ws_protocol["payload"] += payload

        # update the status.
        if self._ws_protocol[ "fin" ]:
            self.handle_sub_protocol( self._ws_protocol["payload"] )
            self._status = self.RECV_STATUS_SUCCESS
            return None, None
        else:
            self._status = self.RECV_STATUS_WAIT
            return self.WS_RECV_STAGE_OPT, 1

    def handle_sub_protocol( self, payload ):

        if self.is_protocol_message():
            self._set_payload_len( self._ws_protocol["payload_length"].to_bytes(2, const.SOCK.BYTE_ORDER) )
            # self._set_payload( payload )
        else:
            self._set_opt_byte( [payload[0]] )
            # the sub protocol does not contain a payload length as it 'WS payload length' - 'Sub protocol header length'
            self._set_payload_len( (self._ws_protocol["payload_length"] - self.SUB_HEADER_LENGTH).to_bytes(2, const.SOCK.BYTE_ORDER) )
            self._set_frame_id( payload[1:5] )
            self._set_time_stamp( payload[5:9] )
            self._set_payload( payload[9:] )

    def _set_payload( self, bytes ): # BaseProtocol

        if self._payload is None:
            self._payload = payload_json_data.PayloadJsonData()

        self._payload.set_string( bytes )

    def convert_to_send( self, sent_callback=None, copy_sub_header=False ):
        # TODO: this self.payload needs parsing to json string.
        #       Theres a miner inconsisty
        send_message = WebsocketSendMessage( None, sent_callback=sent_callback )
        send_message._payload = self._payload

        if copy_sub_header:
            send_message._protocol_data = self._protocol_data

        return send_message

    def convert_to_pong( self, sent_callback=None ):
        return None  # TODO: ...

class WebsocketSendMessage( BaseWebsocketProtocol, base_message.BaseSendProtocolMessage ):

    def __init__( self, data, sent_callback=None ):

        super().__init__()                                                    # init BaseWebsocketProtocol
        super( BaseWebsocketProtocol, self ).__init__( data, sent_callback )  # init BaseSendProtocolMessage

        # set our standard send message frame
        self._ws_protocol[ "fin" ] = True  # we will never send a message that needs a second frame
        self._ws_protocol[ "rsv1" ] = False
        self._ws_protocol[ "rsv2" ] = False
        self._ws_protocol[ "rsv3" ] = False
        self._ws_protocol[ "opcode" ] = BaseWebsocketProtocol.WS_OP_CODE_BIN
        self._ws_protocol[ "use_mask" ] = False  # Server does not use the mask bit

    def get( self ):

        # Bytes             1       2       3       4
        # Bits:             12345678123456781234567812345678  #
        two_full_bytes  = 0b1111111111111111                  #
        four_full_bytes = 0b11111111111111111111111111111111  #
        byte_order = const.SOCK.BYTE_ORDER

        message_bytes = []
        # first byte
        byte = (self._ws_protocol[ "fin" ] << 7) + \
               (self._ws_protocol[ "rsv1" ] << 6) + \
               (self._ws_protocol[ "rsv2" ] << 5) + \
               (self._ws_protocol[ "rsv3" ] << 4) + \
               self._ws_protocol[ "opcode" ]

        message_bytes.append( byte.to_bytes( 1, byte_order ) )

        # second byte
        # ignore setting the mask as its never set from the server
        msg_len = None
        if self.length() <= 125:
            msg_len = self.length()
        elif self.length() > two_full_bytes:    # largest 8 byte message len
            msg_len = 127
        else: # mid 2 byte message len
            msg_len = 126

        message_bytes.append( msg_len.to_bytes( 1, byte_order ) )

        # add payload len if 126 or 127
        if msg_len == 126:
            message_bytes.append( self.length().to_bytes( 2, byte_order ) )
        elif msg_len == 127:
            message_bytes.append( self.length().to_bytes( 8, byte_order) )

        # mask bit is never set on server so ignore that
        # Add the Sub protocol.
        message_bytes.append( self._get_opt_byte() )
        message_bytes.append( self._get_frame_id_bytes() )
        message_bytes.append( self._get_timestamp_bytes() )

        # append payload :)
        message_bytes.append( self._payload.get_bytes() )

        self._status = self.SND_STATUS_USED

        return b''.join( message_bytes )

    def length( self ):

        # we must add the subProtocol length
        return self._payload_len + self.SUB_HEADER_LENGTH
