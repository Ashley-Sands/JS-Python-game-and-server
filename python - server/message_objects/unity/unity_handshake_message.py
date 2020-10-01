import message_objects.base_handshake_message as base_handshake_message

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print


class UnityHandshake( base_handshake_message.BaseHandshakeMessage ):

    @property
    def HEADER_TERMINATOR( self ):
        return ""

    @property
    def HEADER_JOIN( self ):
        return ";"

    def __init__( self, data, completed_handshake_callback ):
        super().__init__( data, completed_handshake_callback )

    def set( self, handshake_str ):

        accepted_clients = ["delve:0.1"]
        handshake = handshake_str.split( self.HEADER_JOIN )

        if len( handshake ) < 2:
            _print( "Invalid Handshake" )
            return
        elif handshake[0] not in accepted_clients:
            _print( "Invalid Client" )
            return

        response_key = self.get_response_key( handshake[1] )
        self._response.append("1")
        self._response.append( response_key )
        self.accepted = True

    def magic_hand_shake( self ):
        return "5FOI0S-38FUDO-D31V3-PR830DJE9GKW"
