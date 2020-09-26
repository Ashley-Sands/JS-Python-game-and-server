
import world_models.world_client as world_client
import world_models.core.objects.game_object as game_object
# managers
import world_models.core.managers.game_console as game_console
import world_models.core.managers.object_manager as object_manager

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print


class BaseWorld:

    def __init__(self, max_clients=6):
        """

        :param sync_managers: dict of sync managers (key: server/sync name : Value: manager)
        """
        self.started = False

        self.max_clients = max_clients
        self._clients = {}                          # all clients active in this world.               (Key: Socket,    Value: WorldClient)

        self.objects  = {}                          # all world objects                               (Key: server_id, Value: Object)
        self.managers = {}                          # all world managers.                             (Key: server_id, value: manager)
        self.sync_objects = {}  # All objects to be kept in sync with the client. (Key: server_id, Value: Object)(excluding client managers)

        self.current_world_snapshot = {}    # the entire world snapshot
        self.delta_world_snapshot   = {}    # Delta snapshot from last frame
        self.world_snapshot_history = []    # last 10 delta snapshots ??

    def create_world_managers( self ):
        """ defines and creates managers for world
            Note: The time manager should never be created in the world.
                  The time manager is handled by the world handler as its a requirement.
        """

        # standard managers.
        return {
            "console": game_console.GameConsole( "console" ),
            "objects":  object_manager.ObjectManager( "objects", self )
        }


    def start( self ):

        self.objects = { **self.objects, **self.sync_objects }
        self.sync_objects = { **self.sync_objects, **self.create_world_managers() }  # make sure managers are added to sync objects lasts as tick has no delta
        self.started = True

    def tick( self, delta_time ):

        if not self.started:
            _print("Unable to tick world. Not Started", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return

        # update world managers
        for man in self.managers:
            self.managers[ man ].tick()

        # update client managers
        for cli in self._clients:
            self._clients[ cli ].tick_managers()

        # update all world objects
        for obj in self.objects:
            self.objects[ obj ].tick( delta_time )

    def instantiate_object( self, object_constructor, object_uid, force_non_sync=False, **constructor_args ):
        """ Instantiates an object into the scene, adding it to the relevant dictionaries (lower level)
            Use 'instantiate object manager' to instantiate new objects and notify the client accordingly

        :param object_constructor:  constructor of object to instantiate
        :param object_uid:          objects unique id
        :param force_non_sync:      forces the objects to not be synced with the client (only if server object)
        :param constructor_args:    Args to be passed into the objects constructor
        :return:                    New object instance
        """

        if not issubclass( object_constructor, game_object.GameObject ):
            _print("Unable to instantiate object. Object must be a type of game object", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return None

        obj_inst = object_constructor( object_uid, self, **constructor_args )
        # TODO: objects need a method/property for syncing

        if not force_non_sync:
            self.sync_objects[ object_uid ] = obj_inst

        self.objects[ object_uid ] = obj_inst

        return obj_inst

    def destroy_object( self, object_uid ):
        """ Removes the object from the simulation. """

        # attemp to remove the objects from all objects list.
        try:
            del self.objects[ object_uid ]
        except Exception as e:
            _print("Unable to remove object from simulation. Object not found (", e, ")", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return  # if its no in objects in wont be in sync objects

        try:
            del self.sync_objects[ object_uid ]
        except Exception as e:
            _print( "Unable to remove sync object. Object not found (", e, ")", message_type=DEBUG.LOGS.MSG_TYPE_WARNING )

    def get_world_client( self, socket ):
        """ Get a world client from the clients socket """
        try:
            return self._clients[ socket ]
        except Exception as e:
            _print("Client not found in world")
            return None

    def client_join( self, _world_client ):
        """Add client to the world """
        self._clients[ _world_client.socket ] = _world_client
        _print( f"Client added to world ({len(self._clients)} of {self.max_clients})" )

        # assign required client managers. ie. inputs.
        # ...

    def client_leave( self, _world_client ):
        """Remove a client from the world"""
        try:
            del self._clients[ _world_client.socket ]
        except Exception as e:
            _print( f"Unable to remove client from world. ({e})", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)

        _print( f"client removed from world. ({len(self._clients)} of {self.max_clients})")

    def apply_data( self, from_socket, data ):
        """Applies all world data to sync objects"""

        try:
            client = self._clients[ from_socket ]
        except Exception as e:
            _print( "Unable to find client in world.", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
            return

        for obj in data:
            # Attempt to apply the data to a client manager
            if client.apply_manager_data( obj, data[obj] ):
                _print("aplied client man")
                continue

            # otherwise attempt to apply the data to a world object
            try:
                self.sync_objects[ obj ].apply_data( data[ obj ] )
            except KeyError as e:
                _print( f"Unable to apply data to sync object {obj}. Key Error: {e} Does Not exist",
                        message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
            except Exception as e:
                _print( f"Unable to apply data to sync object {obj}. {e}", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )

    def collect_data( self ):
        """Collects all world data from sync objects"""
        data = {}

        for obj in self.sync_objects:
            d = self.sync_objects[ obj ].collect_data()
            if d is not None and len( d ) > 0:
                data[ obj ] = d

        return data


