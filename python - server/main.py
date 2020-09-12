import sockets.socket_handler as socket_handler
import sockets.web_socket as web_socket
import queue

#################
# TODO: NOTE:
# Main is the testing interface for both JS and Unity Sockets.
# See.  (TODO. Maybe??, Maybe use args instead??)
# main_js for Javascript socket handling and
# main_unity for Unity socket handling.
#################
# if args
# [0] = mode (required),
# [1] = max-connections (default: 20?),
# [2] = port (default: 9091),
# [3] = host (default: 0.0.0.0)
#################

IP_ADDRESS = "0.0.0.0"
PORT = 9091
MAX_CONNECTIONS = 200

if "__main__" == __name__:

    print("Starting...")

    # set the receive queue and set it in the required places
    receive_queue = queue.Queue()
    web_socket.WebSocket.set_shared_received_queue( receive_queue )

    socket_handler = socket_handler.SocketHandler(IP_ADDRESS, PORT, MAX_CONNECTIONS, web_socket.WebSocket )   # webSocket
    socket_handler.start()

    while True:

        message_object = receive_queue.get( block=True )
        socket_handler.send_to_all_clients( message_object )
