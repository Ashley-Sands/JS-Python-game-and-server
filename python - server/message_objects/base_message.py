class Protocol:
    # Shared Op-codes (Theses should no be used directly)
    # Rather use the opcodes defined in the appropriate socket type (ie Unity or WS)
    _SH_OP_CODE_CLS  = 0x8  # Close Socket
    _SH_OP_CODE_PING = 0x9  # Ping
    _SH_OP_CODE_PONG = 0xA  # Pong (Ping response)

    # Protocol Standared Opcodes (Sub protocol for WS or Primary for Unity)
    # (These should be be used directly) rather use the opcodes defined in the
    # appropriate socket type (ie Unity or WS)
    _PRO_OP_CODE_ACEPT = 0x0    # Connection accepted
    _PRO_OP_CODE_IDATA = 0x1    # Initial Data  (Initial Game Data or agreement)
    _PRO_OP_CODE_DDATA = 0x2    # Delta Data    (Game Delta Data)
    _PRO_OP_CODE_USER  = 0x3    # User Update


class BaseMessage:

    ENDPOINT_SEND = 0
    ENDPOINT_RECEIVE = 1

    def __init__( self, data, endpoint, sent_callback=None ):
        """

        :param msg_type:        SEND/RECEIVE type
        :param data:            Data to be sent
        :param sent_callback:   callback to be triggered when sent
        """
        # When overriding make sure that the super() is at the end

        self._payload = None                    # payload cache
        self._payload_len = -1                  # payload length cache

        self.endpoint = endpoint

        self._sent_callback = sent_callback
        if data is not None:
            self.set( data )

    def set( self, data ):
        """Sets the message"""
        raise NotImplementedError

    def get( self ):
        """
            returns the message ready to be sent/received
            if the message endpoint is send this should return bytes
            if the message endpoint is receive this should return a dict or string
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


class BaseProtocolMessage( BaseMessage ):
    pass # ...


class BaseReceiveMessage( BaseMessage ):

    RECV_STATUS_ERROR   = -1
    RECV_STATUS_ACTIVE  = 0
    RECV_STATUS_SUCCESS = 1
    RECV_STATUS_WAIT    = 2     # waiting for next frame (fin = false on last packet)

    def __init__( self, data ):

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
            print("Unable to set message. Message no longer Active (Status Code:", self._status, ")")
            return None
        elif self._status == self.RECV_STATUS_WAIT:
            # return to an active state
            self._status = self.RECV_STATUS_ACTIVE

        self.next_stage_key, next_bytes = self.stages[ self.next_stage_key ]( pack_bytes )

        return next_bytes

    def status( self ):
        return self._status

    def close_connection( self ):
        raise NotImplementedError   # TODO: ATM im not to sure how the opcode are between the JSWS and Unity sockets

    def set_error( self ):
        self._status = self.RECV_STATUS_ERROR

    def get( self ):

        return self._payload

    def convert_to_send( self, sent_callback=None ):
        """Converts the message to a send message."""
        raise NotImplementedError


class BaseSendMessage( BaseMessage ):

    SND_STATUS_PEND = 0
    SND_STATUS_USED = 1

    def __init__(self, data, sent_callback):

        self._status = self.SND_STATUS_PEND

        super().__init__(data, BaseMessage.ENDPOINT_SEND, sent_callback=sent_callback)

    def set( self, payload_str ):

        self._payload = payload_str
        self._payload_len = len( payload_str )

    def append( self, payload_str ):

        self._payload += f" {payload_str}"
        self._payload_len += len(payload_str) + 1  # 1 to account for the space

    def get( self ):
        raise NotImplementedError
