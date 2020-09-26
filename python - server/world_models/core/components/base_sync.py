
# parent of all sync objects

class BaseSync:

    def __init__(self, obj_id, client_name=None):

        self.object_id = obj_id

        if client_name is None:
            self.client_name = self.__class__.__name__
        else:
            self.client_name = client_name

    # Data must be json. Object Format
    # [   // frame
    #   { },     // snapshot 1...
    #   { }      // snapshot ...n
    # ]
    #

    def client_instantiate_data( self ):
        return { "class": self.client_name }

    def apply_data( self, data ):
        """Applies frame data received form client"""
        pass

    def collect_data( self ):
        """Collects frame data to send to client."""
        # raise NotImplementedError
        return None