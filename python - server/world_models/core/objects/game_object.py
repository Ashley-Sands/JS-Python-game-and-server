import world_models.core.components as core

class GameObject:

    def __init__( self, obj_id ):

        self.transform = core.transform.Transform( core.vector.Vector3(), core.vector.Vector3(), core.vector.Vector3.one() )

    def tick( self, delta_time ):
        pass

    # Data must be json. Object Format
    # [   // frame
    #   { },     // snapshot 1...
    #   { }      // snapshot ...n
    # ]
    #

    def apply_data( self, data ):
        """Applies frame data received form client"""
        raise NotImplementedError

    def collect_data( self ):
        """Collects frame data to send to client."""
        raise NotImplementedError
