
class BaseWorld:

    def __init__(self, sync_managers):
        """

        :param sync_managers: dict of sync managers (key: server/sync name : Value: manager)
        """

        self.objects = {}                           # all scene objects                               (Key: server_id, Value: Object)
        self.managers = sync_managers               # all managers.                                   (Key: server_id, value: manager)
        self.sync_objects = { **sync_managers }     # All objects to be kept in sync with the client. (Key: server_id, Value: Object)

        self.current_world_snapshot = {}    # ?? do we really need this?
        self.delta_world_snapshot   = {}    # Delta snapshot from last frame
        self.world_snapshot_history = []    # last 10 delta snapshots ??

    def tick( self, delta_time ):

        for man in self.managers:
            self.managers[ man ].tick( delta_time )

        for obj in self.objects:
            self.objects[ obj ].tick( delta_time )

    def apply_data( self, data ):
        """Applies all world data to sync objects"""
        raise NotImplementedError

    def collect_data( self ):
        """Collects all world data from sync objects"""
        raise NotImplementedError
