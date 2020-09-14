import world_models.core.world.base_world as base_world
import world_models.core.objects as objects

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class test_world( base_world.BaseWorld ):

    def __init__( self ):

        super().__init__()

        self.sync_objects["abc123"] = objects.game_object.GameObject( "abc123" )
        self.objects = { **self.objects, **self.sync_objects }

    def tick( self, delta_time ):

        for obj in self.objects:
            self.objects[obj].tick( delta_time )

    def apply_data( self, data ):

        for obj in data:
            try:
                self.sync_objects[obj].apply_data( data[ obj ] )
            except Exception as e:
                _print( f"Unable to apply data to sync object {obj} | {e}", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )


    def collect_data( self ):

        data = {}

        for obj in self.sync_objects:
            data[ obj ] = self.sync_objects[obj].collect_data()

        return data