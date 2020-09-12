import sockets.base_socket as base_socket


class UnitySocket( base_socket.BaseSocket ):

    def __init__( self, client_id, client_socket, handler_action_func ):
        super().__init__(client_id, client_socket, handler_action_func)

    @property
    def handshake_message_obj( self ):
        raise NotImplementedError   # TODO

    @property
    def send_message_obj( self ):
        raise NotImplementedError

    @property
    def receive_message_obj( self ):
        raise NotImplementedError
