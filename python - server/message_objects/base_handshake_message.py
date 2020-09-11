import message_objects.base_message as base_message


class BaseHandshakeMessage( base_message.BaseMessage ):

    HEADER_TERMINATOR = "\r\n\r\n"

    def __init__( self, data, completed_handshake_callback ):

        self._response = []
        self.accepted = False

        super().__init__( data, self.ENDPOINT_SEND, completed_handshake_callback )

    def get( self ):

        return ( "\r\n".join( self._response ) + self.HEADER_TERMINATOR ).encode()

    def length( self ):
        return len( "\r\n".join( self._response ) ) + len(self.HEADER_TERMINATOR)

    def get_callback_data( self ):
        return{
            "accepted": self.accepted
        }