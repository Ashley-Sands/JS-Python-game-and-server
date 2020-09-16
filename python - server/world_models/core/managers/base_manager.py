import world_models.core.components.base_sync as base_sync

class BaseManager( base_sync.BaseSync ):

    def __init__( self, obj_id ):

        super().__init__( obj_id )

    def tick( self ):
        pass