# See https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers
# for information on WebSockets packets and see WebSocket.md for notes

import sockets.base_socket as base_socket
import message_objects.websocket.websocket_handshake_message as handshake_message
import message_objects.websocket.websocket_message as websocket_message


class WebSocket( base_socket.BaseSocket ):

    def __init__( self, client_id, client_socket, handler_action_func ):
        super().__init__(client_id, client_socket, handler_action_func)

    @staticmethod
    def handshake_message_obj( ):
        """ Gets the constructor for the handshake message"""
        return handshake_message.WebsocketHandshakeMessage

    @staticmethod
    def send_message_obj( ):
        """ Gets the constructor for the send message """
        return websocket_message.WebsocketSendMessage

    @staticmethod
    def receive_message_obj( ):
        """ Gets the constructor for the receive message """
        return websocket_message.WebsocketReceiveMessage

    def _queue_received_message( self, message_object ):

        # handle sub protocol opcodes
        if message_object.get_protocol_value("opcode") == message_object.SUB_OP_CODE_ACEPT and \
           message_object.get_protocol_value("acknowledged") :
            self._state = self.SOCK_STATE_ACTIVE
            self._trigger_acknowledged_connection()

        super()._queue_received_message( message_object )