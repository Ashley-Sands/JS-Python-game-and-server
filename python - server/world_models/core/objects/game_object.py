import world_models.core.components.transform as transform
import world_models.core.components.vector as vector
import world_models.core.components.base_sync as base_sync


class GameObject( base_sync.BaseSync ):

    def __init__( self, obj_id, world, owner=None, client_name=None ):

        super().__init__( obj_id, client_name )

        self.owner = owner
        self.world = world
        self.transform = transform.Transform( vector.Vector2(), 0.0, vector.Vector2.one() )

    def tick( self, delta_time ):
        pass

