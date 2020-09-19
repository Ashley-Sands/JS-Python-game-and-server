import world_models.world_client as world_client
import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class BaseWorld:

    def __init__(self, sync_managers):
        """

        :param sync_managers: dict of sync managers (key: server/sync name : Value: manager)
        """
        self.started = False

        self._clients = {}                          # all clients active in this world.               (Key: Socket,    Value: WorldClient)

        self.objects = {}                           # all world objects                               (Key: server_id, Value: Object)
        self.managers = sync_managers               # all world managers.                             (Key: server_id, value: manager)
        self.sync_objects = {}  # All objects to be kept in sync with the client. (Key: server_id, Value: Object)(excluding client managers)

        self.current_world_snapshot = {}    # ?? do we really need this?
        self.delta_world_snapshot   = {}    # Delta snapshot from last frame
        self.world_snapshot_history = []    # last 10 delta snapshots ??

    def start( self ):

        self.objects = { **self.objects, **self.sync_objects }
        self.sync_objects = { **self.sync_objects, **self.managers }  # make sure managers are added to sync objects lasts as tick has no delta
        self.started = True

    def tick( self, delta_time ):

        if not self.started:
            _print("Unable to tick world. Not Started", message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return

        for man in self.managers:
            self.managers[ man ].tick( )

        for obj in self.objects:
            self.objects[ obj ].tick( delta_time )

    def client_join( self, _world_client ):

        self._clients[ _world_client.socket ] = _world_client
        # assign required client managers. ie. inputs.
        # ...

    def client_leave( self, _world_client ):

        try:
            del self._clients[ _world_client.socket ]
        except Exception as e:
            _print( f"Unable to remove client from world. ({e})", )

    def apply_data( self, from_socket, data ):
        """Applies all world data to sync objects"""

        try:
            client = self._clients[ from_socket ]
        except Exception as e:
            _print( "Unable to find client in world.", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
            return

        for obj in data:
            # Attempt to apply the data to a client manager
            if client.apply_manager_data( obj, data ):
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


