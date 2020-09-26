import world_models.core.world.base_world as base_world
# client mangers
import world_models.core.managers.input_manager as input_manager

# TESTING / TEMP
import world_models.core.objects.TEST_server_object as TEST_server_object

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print


class test_world( base_world.BaseWorld ):

    def __init__( self ):

        super().__init__( )

        self.sync_objects["abc123"] = TEST_server_object.TEST_ServerObject( "abc123", self )

    def client_join( self, _world_client ):

        super().client_join( _world_client )

        client_managers = {
            "input": input_manager.InputManager( "input" )
        }

        _world_client.set_managers( client_managers )

        # spawn a new player GameObject...
        client_obj = self.managers["objects"].create( TEST_server_object.TEST_ServerObject )
        client_obj.owner = _world_client    # assign the client to the object. this allows use to access the clients managers.
