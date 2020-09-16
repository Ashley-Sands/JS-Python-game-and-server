import world_models.core.objects.game_object as game_object

class TEST_ServerObject( game_object.GameObject ):

    def __init__(self, object_name, world):

        super( ).__init__( object_name, world )

    def tick( self, delta_time ):

        rot_speed = 180

        self.transform.rotation += rot_speed * delta_time

        if self.transform.rotation >= 360:
            self.transform.rotation -= 360
        elif self.transform.rotation < 0:
            self.transform.rotation += 360


    def collect_data( self ):

        return [
            {"transform": {"rotation":  self.transform.rotation } }
        ]