# Base Socket for each connected client
import message_objects.base_message as base_message
import sockets.socket_handler as socket_handler
import threading
import queue
import socket
from common.const import SOCK
import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print


class BaseSocket:

    __shared_received_queue = None            # servers received message process queue
    __acknowledged_handshake_callback = None  # param: BaseSocket
    __close_connection_callback = None        # param: BaseSocket

    SEND_Q_ACT_CLOSE = "CLOSE-SOCKET"

    SOCK_STATE_HANDSHAKE = 0
    SOCK_STATE_ACTIVE    = 1

    def __init__( self, client_id, client_socket, handler_action_func ):
        """

        :param client_id:
        :param client_socket:
        :param handler_action_func:     Socket Handler Queue Action Function
        """

        self.client_id = client_id
        self.client_socket = client_socket

        self.__send_queue = queue.Queue()
        self.__handler_action_func = handler_action_func    # params action (action name, value)

        self.thr_lock = threading.Lock()
        self.receive_thread = None
        self.send_thread = None

        self._state = BaseSocket.SOCK_STATE_HANDSHAKE
        self.__handshake_completed = False
        self.__started = False
        self.__valid = True

        # TODO: Add close State Enum kinda fingy
        self.__closing = False
        self.__closing_prepared = False

    @staticmethod
    def set_acknowledged_handshake_callback( func ):
        """

        :param func:    Callback method with param: BaseSocket
        """
        if BaseSocket.__acknowledged_handshake_callback is None:
            BaseSocket.__acknowledged_handshake_callback = func
        else:
            _print( "unable to acknowledged handshake callback, already set!", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

    @staticmethod
    def set_close_connection_callback( func ):
        """

        :param func:    Callback method with param: BaseSocket
        """
        if BaseSocket.__close_connection_callback is None:
            BaseSocket.__close_connection_callback = func
        else:
            _print( "unable to set close connection callback, already set!", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

    def _trigger_acknowledged_connection( self ):
        if BaseSocket.__acknowledged_handshake_callback is not None:
            BaseSocket.__acknowledged_handshake_callback( self )

    @staticmethod
    def set_shared_received_queue( msg_queue ):
        """Set the shared received message queue"""
        if BaseSocket.__shared_received_queue is None:
            BaseSocket.__shared_received_queue = msg_queue
        else:
            _print( "unable to set queue, already set!", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

    def is_valid( self ):
        with self.thr_lock:
            valid = self.__valid
        return valid

    def set_valid( self, valid ):
        with self.thr_lock:
            self.__valid = valid

    @staticmethod   # it would be nice for theses to be a static property, but that's not a thing without a lot of work
    def handshake_message_obj():
        """ Gets the constructor for the handshake message"""
        raise NotImplementedError

    @staticmethod
    def send_message_obj():
        """ Gets the constructor for the send message """
        raise  NotImplementedError

    @staticmethod
    def receive_message_obj():
        """ Gets the constructor for the receive message """
        raise NotImplementedError

    def handshake_completed( self ):

        with self.thr_lock:
            return self.__handshake_completed

    def start( self ):

        _print("Starting client", self.client_id)

        with self.thr_lock:
            started = self.__started

        if not started:
            self.receive_thread = threading.Thread( target=self.receive_message_thr, args=(self.client_socket,) )
            self.send_thread = threading.Thread( target=self.send_message_thr, args=(self.client_socket,) )

            self.receive_thread.start()
            self.send_thread.start()

        with self.thr_lock:
            self.__started = True

        _print("client Started :)", self.client_id)

    def send_message( self, message_obj ):
        """queues message to send to client."""

        is_handshake_message = isinstance( message_obj, self.handshake_message_obj() )

        # if the handshake is not complete only accept the handshake message
        if not self.handshake_completed() and not is_handshake_message:
            _print("Unable to send message to client, handshake not complete", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return
        elif self._state != self.SOCK_STATE_ACTIVE and not is_handshake_message:
            _print("Unable to send message to client, waiting for connection acknowledgment", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return
        elif not isinstance( message_obj, base_message.BaseMessage ):
            _print("Unable to queue message. Message is not a message object", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return
        elif message_obj.endpoint != base_message.BaseMessage.ENDPOINT_SEND:
            _print("Unable to queue message. Incorrect endpoint", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return

        self.__send_queue.put( message_obj )

    def _queue_received_message( self, message_object ):
        """Queue received messages ready for processing"""

        if self._state != self.SOCK_STATE_ACTIVE:
            _print("Unable to queue received message, wait for connection acknowledgment", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return

        if BaseSocket.__shared_received_queue is not None:
            BaseSocket.__shared_received_queue.put( message_object )
        else:
            _print("Unable to queue message no queue has been set.", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)

    def complete_handshake( self, accepted ):   # message sent callback

        _print("HAND SHAKE COMPLETE. Accepted", accepted)

        if not accepted:
            _print("Disconnecting client: Client rejected")
            self._close_connection( True )
            return

        with self.thr_lock:
            self.__handshake_completed = True

    def connection_acknowledgment( self, message_object ):
        raise NotImplementedError

    def receive_message_thr( self, c_socket ):

        waiting_for_handshake = not self.handshake_completed()

        _print( "Client", self.client_id, "received message started", "waiting for handshake:", waiting_for_handshake )
        while self.is_valid():
            bytes_to_receive = 1

            if waiting_for_handshake:
                # set a max wait time for the handshake to be received.
                # and set the amount of bytes to receive to the max limit, so the whole handshake can
                # be received. if no handshake comes in within the timeout, the client must be disconnected
                c_socket.settimeout( SOCK.HANDSHAKE_TIMEOUT )
                bytes_to_receive = SOCK.MAX_MESSAGE_SIZE

            # Complete the handshake if we havent already
            # otherwise wait to receive a message to be processed.

            try:
                received_bytes = c_socket.recv( bytes_to_receive )
            except TimeoutError as e:
                if waiting_for_handshake:
                    self._close_connection( False )
                    _print("Disconnecting client, handshake has timeout.")
                    break
                else:
                    _print("Socket Receive has timed out, while not waiting for handshake", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
                    continue
            except Exception as e:
                _print("Error on client socket,", e )
                self._close_connection( False )
                break

            if len(received_bytes) == 0:    # 0 bytes means that we have been disconnected
                break

            if waiting_for_handshake:   # complete the handshake
                handshake_constructor = self.handshake_message_obj()
                handshake = handshake_constructor(received_bytes.decode(), completed_handshake_callback=self.complete_handshake)

                self.send_message( handshake )
                c_socket.settimeout( None )     # set the socket back to blocking now the handshake has started
                waiting_for_handshake = False
                continue
            elif not waiting_for_handshake and not self.handshake_completed():
                # Discard any message that are received before the handshake is complete.
                BaseSocket.clear_receive_buffer( c_socket )
                continue

            # Continue to process standard message packets (ie not handshakes)
            # TODO: rename from Websocket to ...
            websocket_msg_constructor = self.receive_message_obj()
            websocket_msg = websocket_msg_constructor( c_socket )


            bytes_to_receive = websocket_msg.set( received_bytes ) # process the first byte that we received at the start

            while bytes_to_receive is not None:
                try:
                    received_bytes = c_socket.recv( bytes_to_receive )
                except Exception as e:
                    _print( "Error on client socket,", e )
                    websocket_msg.set_error()   # reject the message
                    self._close_connection( False )
                    break

                bytes_to_receive = websocket_msg.set( received_bytes )

            _print("RECEIVED")
            _print( "ack", websocket_msg._protocol_data )
            # queue the message and move onto the next.
            if websocket_msg.accept_connection():
                self._state = self.SOCK_STATE_ACTIVE
                self._trigger_acknowledged_connection()
                _print("Connection Complete :P")
            elif websocket_msg.close_connection():
                _print(f"Client {self.client_id} Requested to close session. Bey Bey...")
                self._close_connection( False )
                break
            elif websocket_msg.is_ping():
                pass    # TODO: PING
            elif websocket_msg.is_pong():
                pass    # TODO: PONG
            elif websocket_msg.status() == base_message.BaseReceiveMessage.RECV_STATUS_SUCCESS:
                _print( "rec received message queued;", websocket_msg.get())
                self._queue_received_message( websocket_msg )

        self.set_valid(False)

    def send_message_thr( self, c_socket ):

        _print("Client", self.client_id, "send message started")

        while self.is_valid():

            message_obj = self.__send_queue.get( block=True )

            if message_obj is self.SEND_Q_ACT_CLOSE:
                break   # closing connection

            # TODO. if the connection is not valid anymore we should return
            #       unless the message op code is close (0x8)

            try:
                c_socket.send( message_obj.get() )
                message_obj.message_sent()
            except Exception as e:
                _print("Unable to send message", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
                # Don't notify the client as its most likely a dead connection
                # Also we don't want a loop of closing connection messages.
                self._close_connection( False )

        self.set_valid( False )

    @staticmethod
    def clear_receive_buffer( socket ):
        """ Clears all incoming bytes on the socket """

        clearing_buffer = True

        # set the socket to non blocking
        org_timeout = socket.gettimeout()
        socket.settimeout(0)

        while clearing_buffer:
            try:
                socket.recv( SOCK.MAX_MESSAGE_SIZE )
            except:
                clearing_buffer = False

        # restore the socket back to its original timeout
        socket.settimeout(org_timeout)

    def __prepare_close_connection( self, notify_client=False ):

        if self.__closing_prepared:
            return

        _print( "Preparing to close clients connection" )

        self.__closing_prepared = True
        self.set_valid( False )

        if notify_client:   # this will unblock the queue by default.
            pass
        else:
            self.__send_queue.put( self.SEND_Q_ACT_CLOSE )  # unblock the queue so the thread can close.

        try:
            self.client_socket.shutdown( socket.SHUT_RDWR )   # prevent further read/writes to the socket
        except Exception as e:
            _print("Error shutting down clients socket.", e)

        if self.__close_connection_callback is not None:
            self.__close_connection_callback( self )

    def _close_connection( self, notify_client ):
        """ Prepares the connection to close and threads to be stopped and
            Queues the connection to be completely closed by the socket handler
        """
        if self.__closing:
            return

        _print( "Queuing connection to be closed" )
        self.__closing = True
        self.__prepare_close_connection( notify_client=notify_client )
        self.__handler_action_func( socket_handler.SocketHandler.HND_ACT_REMOVE_CLIENT, self.client_socket )

    def close_connection( self ):
        """ Closes the clients ensuing all threads are stopped
            This should not be called from self. use _close_connection instead for internal use
        """

        _print( "Closing client connection" )

        self.__prepare_close_connection()

        try:
            self.client_socket.close()
        except Exception as e:
            _print("Error closing clients socket.", e)

        # wait for threads to join
        if self.receive_thread is not None and self.receive_thread.is_alive():
            self.receive_thread.join()

        if self.send_thread is not None and self.send_thread.is_alive():
            self.send_thread.join()

        _print( "Client connection has been stopped successfully" )
