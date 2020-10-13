import world_models.core.world.base_world as base_world
#managers
import world_models.unity.delve.managers.delve_object_manager as object_manager
import world_models.core.managers.game_console as game_console

# Objects
import world_models.unity.delve.objects.actors.actor as actor

# Debug.
import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print


class DelveBaseWorld( base_world.BaseWorld ):

    START_WAIT = 40                 # seconds
    WAIT_CLIENT_CHANGE_LEN = 10     # seconds

    def __init__(self, max_clients=4):

        super().__init__( max_clients=max_clients )

        self.passthrought_message = {}  # [action][obj] = {fields} || [global name] = {fields}

    def tick( self, delta_time ):

        super().tick( delta_time )


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
        client_actor = self.managers["objects"].create( actor.Actor, _world_client )
        client_actor.owner = _world_client


    def client_leave( self, _world_client ):

        super().client_leave( _world_client )

        # remove the clients actors
        client_obj_ids = self._get_client_object_ids( _world_client )

        for obj_id in client_obj_ids:
            self.managers["objects"].destroy( obj_id )



    def apply_data( self, from_socket, data ):
        """ Used to authorize and process the users action """

        # We can use the apply data to handle our actions
        # rather than tick as we only need to process data on
        # user actions. Tick can then be use to timeout client ect...

        try:
            client = self._clients[ from_socket ]
        except Exception as e:
            _print( "Unable to find client in world.", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
            return

        for action in data:
            if action == "GLOBAL":
                _print("RECEIVED GLOBAL ACTION")
            else:
                _print( "ACTION:", action )
                for obj in data[ action ]:
                    # Attempt to apply the data to a client manager
                    if client.apply_manager_data( obj, data[ action ][ obj ] ):
                        _print("applied client man")
                        continue

                    # otherwise attempt to apply the data to a world object
                    try:
                        self.sync_objects[ obj ].apply_data( data[ action ][ obj ] )
                    except KeyError as e:
                        _print( f"Unable to apply data to sync object {obj}. Key Error: {e} Does Not exist",
                                message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                    except Exception as e:
                        _print( f"Unable to apply data to sync object {obj}. {e}", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )

                # TODO: for now at least just forwards message on to all clients.
                self.passthrought_message[ action ] = data[ action ]

        self.passthrought_message["SERVER"] = {"ok": True }


    def collect_data( self ):
        """Collects all world data from sync objects"""
        data = self.passthrought_message
        self.passthrought_message = {}

        for obj in self.sync_objects:
            obj_data = self.sync_objects[ obj ].collect_data()
            if obj_data is not None and len( obj_data ) > 0:
                data = obj_data

        return data

    def collect_initial_data( self ):
        """ Gets the initial payload for when a client first joins or falls out of sync"""
        return {
            "GLOBAL": {
                "world": "default",
            },
            "create": {
                "objects": {
                    **self.managers["objects"].init_spwan_objects
                }
            },
            "SERVER": {     # TEMP until the op code is added
                "ok": True,
                "message": "TEMP MESSAGE: Inital payload."
            },
            **self.current_world_snapshot
        }
