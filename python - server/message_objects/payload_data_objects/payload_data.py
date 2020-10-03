
# TODO: c
class PayloadData:
    """ Common class to convert data to and from formatted string (ie JSON) """

    def __init__( self, tick_id=0, frame_timestamp=0 ):
        # TODO: when we have the module to sort out client data we can most likely
        #       remove this. Since its only here to move the data from the world
        #       to the send data thread
        self.tick_id = tick_id
        self.frame_timestamp = frame_timestamp

        self._string = None
        self._structure = None

        self._string_len = 0

        self._string_u2d = True
        self._struct_u2d = True

    def _parse_to_string( self ):
        """Parses the data structure to raw data string"""
        raise NotImplementedError

    def _parse_to_structure( self ):
        """Parses the raw data string to structured data"""
        raise NotImplementedError

    def set_string( self, data_string ):
        """Set string or bytes (bytes are decoded to string)"""

        if type(data_string) is bytes:
            data_string = data_string.decode()

        self._string = data_string
        self._string_u2d = True
        self._struct_u2d = False

    def append_string( self, string ):
        """ This is intended for receiving incomplete packets.
            ie. WebSocket fin=0
        """

        if type(string) is bytes:
            string = string.decode()

        if self._string is None:
            self._string = string
        else:
            self._string += string

        self._string_u2d = True
        self._struct_u2d = False

    # NOTE: it doesnt seem logical to have append structure as some structures can not be extended.
    #       If its needed or relevant it can be added on a need be, per subclass.

    def set_structure( self, data_structure ):
        self._structure = data_structure
        self._string_u2d = False
        self._struct_u2d = True

    def get_string( self ):

        if not self._string_u2d:
            self._parse_to_string()

        return self._string

    def get_bytes( self ):
        """ Encodes string to bytes """
        return self.get_string().encode()

    def get_structure( self ):

        if not self._struct_u2d:
            self._parse_to_structure()

        return self._structure

    def string_length( self ):

        if not self._string_u2d:
            self._parse_to_string()

        return self._string_len