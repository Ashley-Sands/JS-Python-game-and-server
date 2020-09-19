import world_models.core.world.base_world as base_world

import world_models.core.objects.TEST_server_object as TEST_server_object

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class test_world( base_world.BaseWorld ):

    def __init__( self, sync_managers ):

        super().__init__( sync_managers )

        self.sync_objects["abc123"] = TEST_server_object.TEST_ServerObject( "abc123", self )

