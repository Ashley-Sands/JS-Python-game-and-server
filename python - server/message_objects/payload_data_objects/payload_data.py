

class PayloadData:
    """ Common class to convert data to and from formatted string (ie JSON) """

    def __init__( self ):

        self._string = None
        self._structure = None

        self._string_u2d = True
        self._struct_u2d = True

    def _parse_to_string( self ):
        """Parses the data structure to raw data string"""
        raise NotImplementedError

    def _parse_to_structure( self ):
        """Parses the raw data string to structured data"""
        raise NotImplementedError

    def set_string( self, data_string ):
        self._string = data_string
        self._struct_u2d = False

    def set_structure( self, data_structure ):
        self._structure = data_structure
        self._string_u2d = False

    def get_data_string( self ):

        if not self._string_u2d:
            self._parse_to_string()

        return self._string

    def get_data_structure( self ):

        if not self._struct_u2d:
            self._parse_to_structure()

        return self._structure
