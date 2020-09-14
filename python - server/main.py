from sockets.socket_handler import SocketHandler
from world_models.world_handler import WorldHandler
import sockets.web_socket as web_socket
import queue
import common.DEBUG as DEBUG


import world_models.core.world.test_world as test_world
import message_objects.websocket.websocket_message as web_message   # temp.

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
    DEBUG.LOGS.init()

    # set the receive and send queues also setting it in the required places
    # TODO: atm these are set statically for no reason.
    #       i think it would be better if they where part of the instance.
    receive_queue   = queue.Queue()     # Queue of message objects                        client sockets -> world handler
    send_data_queue = queue.Queue()     # Queue of data to be packaged into a message     world handler  -> socket handler -> client socket

    web_socket.WebSocket.set_shared_received_queue( receive_queue )
    WorldHandler.set_shared_queue( receive_queue, send_data_queue)

    world_handler  = WorldHandler( test_world.test_world() )
    socket_handler = SocketHandler(IP_ADDRESS, PORT, MAX_CONNECTIONS, web_socket.WebSocket )   # webSocket

    world_handler.start()
    socket_handler.start()

    while True:
        # TODO: this needs to be in socket handler.
        message_data = send_data_queue.get( block=True )
        socket_handler.package_data_and_send( message_data )

    DEBUG.LOGS.close()
    print("Bey!")