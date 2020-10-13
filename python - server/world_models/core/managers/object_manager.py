import world_models.core.managers.base_manager as base_manager

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class ObjectManager( base_manager.WorldManager ):

    def __init__(self, obj_id, world):

        super().__init__( obj_id, world )

        self.last_uid = 0

        # Rather than adding a method to get the initial snapshot from managers
        # this should be assigned in collect initial data
        self.init_spwan_objects = {}    # dist of all objects
        self.spawn_objs   = {}          # dict of objects to be spawned this frame
        self.destroy_objs = []          # list of server ids

    @property
    def uid( self ):
        self.last_uid += 1
        return "{uid:6}".format( uid=self.last_uid ).replace( " ", "0" )

    def create( self, object_constructor, wc_owner=None, fixed_uid=None, force_non_sync=False, **constructor_args ):
        """ Instantiates a new object with an unique id, assigned to world"""

        if fixed_uid is None:
            uid = self.uid
        elif fixed_uid in self.init_spwan_objects:
            _print( "Unable to use fixed id, object already with uid already exist. Using generated uid instead." )
            uid = self.uid
        else:
            uid = fixed_uid

        created_object = self.world.instantiate_object( object_constructor, uid, wc_owner=wc_owner, force_non_sync=force_non_sync, **constructor_args )
        _print("Add Object", uid)
        if created_object is None:
            return None

        if not force_non_sync:
            self.spawn_objs[ uid ] = created_object.client_instantiate_data()
            self.init_spwan_objects[ uid ] = self.spawn_objs[ uid ]

        return created_object

    def destroy( self, uid ):

        if self.world.destroy_object( uid )[1]:
            self.destroy_objs.append( uid )
            try:
                del self.init_spwan_objects[uid]
            except:
                pass

        _print("Remove Object", uid)

    def collect_data( self ):

        out = []

        if len( self.spawn_objs ) > 0:
            out.append( { "create": self.spawn_objs } )
            self.spawn_objs = {}

        if len( self.destroy_objs ) > 0:
            out.append( { "destroy": self.destroy_objs } )
            self.destroy_objs = []

        return out
