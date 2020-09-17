import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class BaseWorld:

    def __init__(self, sync_managers):
        """

        :param sync_managers: dict of sync managers (key: server/sync name : Value: manager)
        """
        self.started = False

        self.objects = {}                           # all scene objects                               (Key: server_id, Value: Object)
        self.managers = sync_managers               # all managers.                                   (Key: server_id, value: manager)
        self.sync_objects = { }                     # All objects to be kept in sync with the client. (Key: server_id, Value: Object)

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

    def apply_data( self, data ):
        """Applies all world data to sync objects"""
        raise NotImplementedError

    def collect_data( self ):
        """Collects all world data from sync objects"""
        raise NotImplementedError
