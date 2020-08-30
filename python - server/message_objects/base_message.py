
class BaseMessage:

    ENDPOINT_SEND = 0
    ENDPOINT_RECEIVE = 1

    def __init__( self, data, endpoint, sent_callback=None ):
        """

        :param msg_type:        SEND/RECEIVE type
        :param data:            Data to be sent
        :param sent_callback:   callback to be triggered when sent
        """
        # When overriding make sure that the super() is at the end

        self.endpoint = endpoint
        self._sent_callback = sent_callback
        if data is not None:
            self.set( data )

    def set( self, data ):
        """Sets the message"""
        raise NotImplementedError

    def get( self ):
        """
            returns the message ready to be sent/received
            if the message endpoint is send this should return bytes
            if the message endpoint is receive this should return a dict or string
        """
        raise NotImplementedError

    def length( self ):
        """get the length of the message"""
        raise NotImplementedError

    def message_sent( self ):
        """trigger the sent callback"""
        if self.endpoint == self.ENDPOINT_SEND and self._sent_callback is not None:
            self._sent_callback( **self.get_callback_data() )

    def get_callback_data( self ):
        """Returns a dict of all params for the sent callback"""
        return {}