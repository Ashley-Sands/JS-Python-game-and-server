import world_models.core.components.base_sync as base_sync


class BaseManager( base_sync.BaseSync ):

    def __init__( self, obj_id ):

        super().__init__( obj_id )

    def tick( self ):
        pass


class WorldManager( BaseManager ):

    def __init__(self, obj_id, world):
        super().__init__( obj_id )
        self.world = world                  # ref to world that owns the manager.


class WorldClientManager( BaseManager ):

    def __init__(self, obj_id, world_client):
        super().__init__( obj_id )
        self.world_client = world_client    # ref to world client that owns the manager.
