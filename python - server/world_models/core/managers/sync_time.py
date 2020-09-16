import world_models.core.managers.base_manager as base_manager


class SyncTimeManager( base_manager.BaseManager ):

    def __init__(self, obj_id):

        super().__init__( obj_id )

    def tick( self ):
        pass