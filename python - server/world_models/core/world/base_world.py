
class BaseWorld:

    def __init__(self):

        self.objects = {}           # all scene objects                               (Key: server_id, Value: Object)
        self.sync_objects = {}      # All objects to be kept in sync with the client. (Key: server_id, Value: Object)

        self.current_world_snapshot = {}    # ?? do we really need this?
        self.delta_world_snapshot   = {}    # Delta snapshot from last frame
        self.world_snapshot_history = []    # last 10 delta snapshots ??

    def tick( self, delta_time ):
        pass

    def apply_data( self, data ):
        """Applies all world data to sync objects"""
        raise NotImplementedError

    def collect_data( self ):
        """Collects all world data from sync objects"""
        raise NotImplementedError
