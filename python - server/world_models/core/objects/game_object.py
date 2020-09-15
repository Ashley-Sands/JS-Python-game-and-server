import world_models.core.components.transform as transform
import world_models.core.components.vector as vector

class GameObject:

    def __init__( self, obj_id ):

        self.transform = transform.Transform( vector.Vector2(), 0.0, vector.Vector2.one() )

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
        pass

    def collect_data( self ):
        """Collects frame data to send to client."""
        # raise NotImplementedError
        return []   # TODO: Return None if no data