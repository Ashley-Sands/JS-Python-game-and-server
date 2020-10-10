import world_models.core.world.base_world as base_world
#managers
import world_models.unity.delve.managers.delve_object_manager as object_manager
import world_models.core.managers.game_console as game_console

# Objects
import world_models.unity.delve.objects.actors.actor as actor


class DelveBaseWorld( base_world.BaseWorld ):

    def create_world_managers( self ):
        """ defines and creates managers for world
            Note: The time manager should never be created in the world.
                  The time manager is handled by the world handler as its a requirement.
        """

        # standard managers.
        return {
            "console": game_console.GameConsole( "console" ),
            "objects": object_manager.DelveObjectManager( "objects", self )
        }

    def client_join( self, _world_client ):

        super().client_join( _world_client )

        # Spawn the clients actor
        client_actor = self.managers["objects"].create( actor.Actor )
        client_actor.owner = _world_client

    def client_leave( self, _world_client ):

        super().client_leave( _world_client )

        # remove the clients actors
        client_obj_ids = self._get_client_object_ids( _world_client )

        for obj_id in client_obj_ids:
            self.managers["objects"].destroy( obj_id )