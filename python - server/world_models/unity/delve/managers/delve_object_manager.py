import world_models.core.managers.object_manager as object_manager

class DelveObjectManager( object_manager.ObjectManager ):

    def __init__(self, obj_id, world):
        super().__init__( obj_id, world)

    def collect_data( self ):

        out = {}

        if len( self.spawn_objs ) > 0:
            out["create"] = { self.object_id: self.spawn_objs }
            self.spawn_objs = { }

        if len( self.destroy_objs ) > 0:
            out["destroy"] = { self.object_id: dict( zip( self.destroy_objs, [0]*len(self.destroy_objs) ) ) }  # we need to add array support in the game/unity
            self.destroy_objs = [ ]

        return out
