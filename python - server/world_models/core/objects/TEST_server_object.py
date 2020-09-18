import world_models.core.objects.game_object as game_object

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class TEST_ServerObject( game_object.GameObject ):

    def __init__(self, object_name, world):

        super( ).__init__( object_name, world )

    def tick( self, delta_time ):

        rot_speed = 180

        if self.world.managers["input"].key_down( "w" ):
            self.transform.position.y -= 10 * delta_time
        elif self.world.managers["input"].key_down( "s" ):
            self.transform.position.y += 10 * delta_time

        if self.world.managers["input"].key_down( "a" ):
            self.transform.position.x -= 10 * delta_time
        elif self.world.managers["input"].key_down( "d" ):
            self.transform.position.x += 10 * delta_time

        self.transform.rotation += rot_speed * delta_time

        if self.transform.rotation >= 360:
            self.transform.rotation -= 360
        elif self.transform.rotation < 0:
            self.transform.rotation += 360

    def collect_data( self ):

        return [
            {"transform": {"position": {"x": self.transform.position.x, "y": self.transform.position.y}, "rotation":  self.transform.rotation } }
        ]