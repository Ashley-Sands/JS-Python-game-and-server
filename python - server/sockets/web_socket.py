# See https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers
# for information on WebSockets packets and see WebSocket.md for notes

import sockets.base_socket as base_socket
import message_objects.websocket.handshake_message as handshake_message
import message_objects.websocket.websocket_message as websocket_message


class WebSocket( base_socket.BaseSocket ):

    def __init__( self, client_id, client_socket, handler_action_func ):
        super().__init__(client_id, client_socket, handler_action_func)

    @property
    def handshake_message_obj( self ):
        return handshake_message.HandshakeMessage

    @property
    def send_message_obj( self ):
        return websocket_message.WebsocketSendMessage

    @property
    def receive_message_obj( self ):
        return websocket_message.WebsocketReceiveMessage
