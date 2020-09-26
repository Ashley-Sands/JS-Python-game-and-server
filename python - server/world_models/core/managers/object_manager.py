import world_models.core.managers.base_manager as base_manager

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class ObjectManager( base_manager.WorldManager ):

    def __init__(self, obj_id, world):

        super().__init__( obj_id, world )

        self.last_uid = 0
        self.spawn_objs   = {}  # list of dicts
        self.destroy_objs = []  # list of server ids

    @property
    def uid( self ):
        self.last_uid += 1
        return "{uid:6}".format( uid=self.last_uid ).replace( " ", "0" )

    def create( self, object_constructor, force_non_sync=False, **constructor_args ):
        """ Instantiates a new object with an unique id, assigned to world"""
        uid = self.uid
        created_object = self.world.instantiate_object( object_constructor, uid, force_non_sync=force_non_sync, **constructor_args )
        _print("Add Object", uid)
        if created_object is None:
            return None

        if not force_non_sync:
            self.spawn_objs[ uid ] = created_object.client_instantiate_data()

        return created_object

    def destroy( self, uid ):
        pass

    def collect_data( self ):

        out = []

        if len( self.spawn_objs ) > 0:
            out.append( { "create": self.spawn_objs } )
            self.spawn_objs = {}

        if len( self.destroy_objs ) > 0:
            out.append( { "destroy": self.destroy_objs } )
            self.destroy_objs = []

        return out
