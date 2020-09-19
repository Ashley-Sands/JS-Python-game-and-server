import world_models.core.world.base_world as base_world
# client mangers
import world_models.core.managers.input_manager as input_manager

# TESTING / TEMP
import world_models.core.objects.TEST_server_object as TEST_server_object

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class test_world( base_world.BaseWorld ):

    def __init__( self, sync_managers ):

        super().__init__( sync_managers )

        self.sync_objects["abc123"] = TEST_server_object.TEST_ServerObject( "abc123", self )

    def client_join( self, _world_client ):

        super().client_join( _world_client )

        managers = {
            "input": input_manager.InputManager( "input" )
        }

        _world_client.set_managers( managers )
        self.sync_objects["abs123"].owner = _world_client
