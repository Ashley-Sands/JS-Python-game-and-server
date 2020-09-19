import world_models.core.objects.game_object as game_object

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class TEST_ServerObject( game_object.GameObject ):

    def __init__(self, object_name, world):

        super( ).__init__( object_name, world )

        self.scale_dir = 1
        self.scale_speed = 5
        self.max_scale = 5
        self.min_scale = 1

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

        self.transform.scale.x += self.scale_dir * self.scale_speed * delta_time
        self.transform.scale.y += self.scale_dir * self.scale_speed * delta_time

        if self.transform.scale.x <= self.min_scale:
            self.scale_dir = 1
        elif self.transform.scale.x >= self.max_scale:
            self.scale_dir = -1

    def collect_data( self ):

        return [
            {"transform": {"position": {"x": self.transform.position.x, "y": self.transform.position.y},
                           "scale":    { "x": self.transform.scale.x,   "y": self.transform.scale.y },
                           "rotation":  self.transform.rotation
                           } }
        ]