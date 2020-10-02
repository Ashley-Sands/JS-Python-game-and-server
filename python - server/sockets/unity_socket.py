import sockets.base_socket as base_socket
import message_objects.unity.unity_handshake_message as unity_handshake
import message_objects.unity.unity_message as unity_message


class UnitySocket( base_socket.BaseSocket ):

    def __init__( self, client_id, client_socket, handler_action_func ):
        super().__init__(client_id, client_socket, handler_action_func)

    @staticmethod
    def handshake_message_obj():
        return unity_handshake.UnityHandshakeMessage

    @staticmethod
    def send_message_obj():
        return unity_message.UnitySendMessage

    @staticmethod
    def receive_message_obj():
        return unity_message.UnityReceiveMessage
