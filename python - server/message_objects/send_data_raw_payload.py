
class SendDataRawPayload:
    """ Wrapper class to move raw payload data away for the current thread so it can be convert on another thread (freeing the current)
        ready to be set into a send message
    """

    def __init__( self, raw_payload_data, to_message_func, frame_id, frame_timestamp, to_sockets=None, ignore_sockets=None ):
        """

        :param raw_payload_data:    the raw payload data
        :param to_message_func:     the function to convert payload data to string or bytes (param: payload_data)
        :param to_sockets:          (optional) (raw py) sockets to send message to (all if none or empty list)
        :param ignore_sockets:      (optional) (raw py) sockets to ignore (not send to) takes priority over to_sockets
        """
        self.__raw_payload = raw_payload_data
        self.__to_message_function = to_message_func

        self.__to_sockets = to_sockets
        self.__ignore_sockets = ignore_sockets

        self.__frame_id = frame_id
        self.__frame_timestamp = frame_timestamp

        if self.__to_sockets is None:
            self.__ignore_sockets = []

        if self.__ignore_sockets is None:
            self.__ignore_sockets = []

    def get( self ):
        """ Gets the payload in a sendable format
            (to_message_func wrapper)
        """
        return self.__to_message_function( self.__raw_payload )

    def get_raw( self ):
        return self.__raw_payload

    @property
    def frame_info( self ):
        """ Gets the frame id and frame timestamp (tuple. id, timestamp)"""
        return self.__frame_id, self.__frame_timestamp

    def can_send_to( self, socket ):
        return socket not in self.__ignore_sockets and (len( self.__to_sockets ) == 0 or socket in self.__to_sockets)