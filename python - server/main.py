import sockets.socket_handler as socket_handler
import sockets.base_socket as base_socket
import message_objects.websocket_message as websocket_message
import time
import queue

IP_ADDRESS = "0.0.0.0"
PORT = 9091
MAX_CONNECTIONS = 20

if "__main__" == __name__:

    print("Starting...")

    # set the receive queue and set it in the required places
    receive_queue = queue.Queue()
    base_socket.BaseSocket.set_process_received_queue( receive_queue )

    socket_handler = socket_handler.SocketHandler(IP_ADDRESS, PORT, MAX_CONNECTIONS, base_socket.BaseSocket )
    socket_handler.start()

    while True:

        message_object = receive_queue.get( block=True )
        socket_handler.send_to_all_clients( websocket_message.WebsocketSendMessage( message_object.get() ) )
