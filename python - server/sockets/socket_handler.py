# Handles all socket connections.
import threading
import queue
import socket

class SocketHandler:

    __last_client_id = -1

    HND_ACT_UNBLOCK = "unblock"
    HND_ACT_REMOVE_CLIENT = "remove_client"

    def __init__( self, ip, port, max_connections, base_socket_class ):

        self._BASE_SOCKET_CLASS = base_socket_class

        # connection setup
        self.ip_address = ip
        self.port = port
        self.max_connections = max_connections

        # status
        self.started = False
        self._valid = True

        # socket
        self.socket_inst = None
        self.connections = {}       # key is socket??, value is base socket class

        # threads
        self.thr_lock = threading.Lock()

        self.accept_connection_thread = None
        self.worker_thread = None   # used to safely preform tasks on the connection list ie remove clients/connections

        # Job/Task handling
        self._action_queue = queue.Queue()
        self._accepted_actions = {      # key: action name, value: mapped function
            self.HND_ACT_UNBLOCK: None,
            self.HND_ACT_REMOVE_CLIENT: self.close_client_connection
        }

    def get_connection( self, socket ):

        with self.thr_lock:
            if socket in self.connections:
                return self.connections[ socket ]

        return None

    def get_connection_by_client_id( self, client_id ):

        with self.thr_lock:
            for conn in self.connections:
                if self.connections[ conn ].client_id == client_id:
                    return self.connections[ conn ]

        return None

    def get_connection_count( self ):

        with self.thr_lock:
            return len( self.connections )

    def is_valid( self ):

        with self.thr_lock:
            valid = self._valid

        return valid

    def set_valid( self, valid ):

        with self.thr_lock:
            self._valid = valid

    def queue_action( self, action_name, value ):
        """ Action : value
          - unblock             : [ignored]
          - remove_client       : c_socket

        :param action_name: Name of action
        :param value:       action value
        :return:
        """

        if action_name.lower() not in self._accepted_actions:
            print("Unable to queue socket action. Invalid action")
            return

        task = {
            "action": action_name,
            "value": value
        }

        self._action_queue.put( task )


    def start( self ):

        # setup the server socket instance
        # and accept client and worker threads
        self.socket_inst = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.socket_inst.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )  # alow the socket to be reused onces idled for a long period
        self.socket_inst.bind( (self.ip_address, self.port) )
        self.socket_inst.listen( self.max_connections + 1 )  # allow 1 extra connection to prevent connections queueing

        self.accept_connection_thread = threading.Thread( target=self.accept_connection_thr, args=(self.socket_inst,) )
        self.worker_thread = threading.Thread( target=self.worker_thr )

        self.accept_connection_thread.start()
        self.worker_thread.start()

        with self.thr_lock:
            self.started = True

    @staticmethod
    def _get_new_client_id():

        SocketHandler.__last_client_id += 1
        return SocketHandler.__last_client_id

    def accept_connection_thr( self, s_socket ):

        print("Waiting for connections...")

        while self.is_valid():

            # wait for connections
            # and setup the clients socket
            print("next client")
            c_socket, address = s_socket.accept()

            if self.get_connection_count() >= self.max_connections:
                print("Client rejected. Server if full. Aborting connection")
                try:
                    c_socket.shutdown(socket.SHUT_RDWR)
                    c_socket.close()
                except Exception as e:
                    print("Error closing rejected clients socket", e)

                continue

            client = self._BASE_SOCKET_CLASS(self._get_new_client_id(), c_socket, self.queue_action)
            client.start()

            with self.thr_lock:
                self.connections[c_socket] = client

            print("Client Accepted", address, "Client ID:", client.client_id, "connection", self.get_connection_count(), "of", self.max_connections  )


    def worker_thr( self ):

        while self.is_valid():

            action = self._action_queue.get( block=True )
            action_func = self._accepted_actions[ action["action"] ]

            if action_func is not None:
                action_func( action["value"] )

    def send_to_all_clients( self, message_obj ):

        with self.thr_lock:
            for con in self.connections:
                self.connections[con].send_message( message_obj )

    def close_client_connection( self, c_socket ):
        """ closes the clients connection and removes client for the connection dict """

        with self.thr_lock:
            if c_socket not in self.connections:
                print("Unable to closes the clients connection. client does not exist")
                return
            else:
                client_connection = self.connections[c_socket]

        client_connection.close_connection()

        with self.thr_lock:
            del self.connections[ c_socket ]

        print("client removed!")

    def close_server_socket( self ):
        """Closes the server socket disconnecting all clients"""
        pass
