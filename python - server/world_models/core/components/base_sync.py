
# parent of all sync objects

class BaseSync:

    # Data must be json. Object Format
    # [   // frame
    #   { },     // snapshot 1...
    #   { }      // snapshot ...n
    # ]
    #

    def apply_data( self, data ):
        """Applies frame data received form client"""
        pass

    def collect_data( self ):
        """Collects frame data to send to client."""
        # raise NotImplementedError
        return None