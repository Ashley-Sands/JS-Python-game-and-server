import world_models.core.objects.game_object as game_object

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print


class Actor( game_object.GameObject ):

    def __init__( self, object_name, world, owner=None ):

        super().__init__( object_name, world, owner=owner )
