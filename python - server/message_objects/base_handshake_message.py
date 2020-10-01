import message_objects.base_message as base_message
import hashlib
import base64

class BaseHandshakeMessage( base_message.BaseMessage ):

    @property
    def HEADER_TERMINATOR( self ):
        raise NotImplementedError

    @property
    def HEADER_JOIN( self ):
        raise NotImplementedError

    def __init__( self, data, completed_handshake_callback ):

        self._response = []
        self.accepted = False

        super().__init__( data, self.ENDPOINT_SEND, completed_handshake_callback )

    def get( self ):

        return ( self.HEADER_JOIN.join( self._response ) + self.HEADER_TERMINATOR ).encode()

    def length( self ):
        return len( self.HEADER_JOIN.join( self._response ) ) + len(self.HEADER_TERMINATOR)

    def get_callback_data( self ):
        return{
            "accepted": self.accepted
        }

    def magic_hand_shake( self ):
        raise NotImplementedError

    def get_response_key( self, client_key ):
        """Gets the servers handshake response key"""
        magic_hand_shake = self.magic_hand_shake()
        auth_key = client_key + magic_hand_shake

        sha1 = hashlib.sha1()
        sha1.update( auth_key.encode() )
        auth_key = base64.encodebytes( sha1.digest() ).decode()
        if auth_key[-1] == "\n":
            auth_key = auth_key[:-1]

        return auth_key
