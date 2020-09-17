import world_models.core.world.base_world as base_world

import world_models.core.objects.TEST_server_object as TEST_server_object

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class test_world( base_world.BaseWorld ):

    def __init__( self, sync_managers ):

        super().__init__( sync_managers )

        self.sync_objects["abc123"] = TEST_server_object.TEST_ServerObject( "abc123", self )

    def apply_data( self, data ):

        for obj in data:
            try:
                self.sync_objects[obj].apply_data( data[ obj ] )
            except KeyError as e:
                _print( f"Unable to apply data to sync object {obj}. Key Error: {e} Does Not exist", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
            except Exception as e:
                _print( f"Unable to apply data to sync object {obj}. {e}", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )


    def collect_data( self ):

        data = {}

        for obj in self.sync_objects:
            d = self.sync_objects[obj].collect_data()
            if d is not None and len(d) > 0:
                data[ obj ] = d

        return data