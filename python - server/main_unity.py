import queue
import threading

from sockets.socket_handler import SocketHandler
from world_models.world_handler import WorldHandler

import sockets.unity_socket as unity_socket
import message_objects.unity.unity_message as unity_message

import world_models.unity.delve.worlds.delve_base_world as delve_base_world

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

## TEMP ##
import message_objects.websocket.websocket_message as web_message
import time
import json

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
PORT = 8333
MAX_CONNECTIONS = 200

# Process the send data in main so we can support multiply socket handlers for no good reason, but why not.
# anyway it also helps to keep the socketHandler clean. Ie socket handler deals with connections,
# getting client sockets and sending data via client connections, ect... but should not have to do any extra
# tasks such as convert data ect....
def process_raw_payload_objects():
    """ Process the send_raw_data queue into messages and sends. """

    with thr_lock:
        running = __running

    while running:
        payload_data_object = send_payload_object_queue.get( block=True )

        # Only process the payload if there are elements to send!
        if not payload_data_object.has_elements():
            continue

        target_client_sockets = payload_data_object.target_clients

        # build the send message object.
        send_message_obj_constructor = socket_handler.socket_class.send_message_obj()
        send_message_obj = send_message_obj_constructor( payload_data_object, sent_callback=None )

        send_message_obj.set_protocol_data( opcode=unity_message.UnityOpcodes.OP_CODE_DDATE )
        send_message_obj.set_protocol_stamp( payload_data_object.tick_id, int( payload_data_object.frame_timestamp ) )

        # send the message to the required clients.
        if target_client_sockets is None or len( target_client_sockets ) == 0:
            socket_handler.send_to_all_clients( send_message_obj )
        else:
            for socket in target_client_sockets:
                socket.send_message( send_message_obj )

        with thr_lock:
            running = __running


def set_running( running ):
    global __running    # just so its thread safe.

    with thr_lock:
        __running = running


if "__main__" == __name__:

    print("Starting...")
    __running = True
    thr_lock = threading.RLock()
    DEBUG.LOGS.init()

    # set the receive and send queues also setting it in the required places
    # TODO: atm these are set statically for no reason.
    #       i think it would be better if they where part of an instance.
    receive_queue       = queue.Queue()  # Queue of message objects                        client sockets -> receive queue  -> world handler
    send_payload_object_queue = queue.Queue()  # Queue of data to be packaged into a message     world handler  -> send raw queue -> client socket (via socket handler)

    unity_socket.UnitySocket.set_shared_received_queue( receive_queue )
    WorldHandler.set_shared_queue( receive_queue, send_payload_object_queue)

    # Get ready to process data to be sent.
    send_message_thr = threading.Thread( target=process_raw_payload_objects )

    # set up the world
    world = delve_base_world.DelveBaseWorld( max_clients=4 )

    # set handlers
    world_handler  = WorldHandler( world, target_fps=30 ) # 1.5 )
    socket_handler = SocketHandler(IP_ADDRESS, PORT, MAX_CONNECTIONS, unity_socket.UnitySocket )   # webSocket

    unity_socket.UnitySocket.set_acknowledged_handshake_callback( world_handler.client_join )   # join clients to a world once handshake acknowledged.
    unity_socket.UnitySocket.set_close_connection_callback( world_handler.client_exit )

    # Let's get going
    send_message_thr.start()
    world_handler.start()
    socket_handler.start()

    _print("Setup Complete")

    with thr_lock:
        running = __running

    while running:

        # item = receive_queue.get(block=True)
        # send_raw_data_queue.put( item.convert_to_send() )

        time.sleep(1)  # do nothing once every second! :P

        with thr_lock:
            running = __running

    send_message_thr.join()
    DEBUG.LOGS.close()
    print("Bey!")
