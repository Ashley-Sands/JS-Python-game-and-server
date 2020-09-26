import world_models.core.managers.base_manager as base_manager


class ObjectManager( base_manager.BaseManager ):

    def __init__(self, obj_id):

        super().__init__( obj_id )

        self.last_uid = 0
        self.spawn_objs = {}
        self.destroy_objs = []
        self.world_instantiate_fuct = None

    @property
    def uid( self ):
        self.last_uid += 1
        return "{uid:6}".format( uid=self.last_uid ).replace( " ", "0" )

    def create( self, object_constructor, force_non_sync=False, **constructor_args ):
        """ Instantiates a new object with an unique id """
        uid = self.uid
        created_object = self.world_instantiate_fuct( object_constructor, uid, force_non_sync=force_non_sync, **constructor_args )

        if not force_non_sync:
            self.spawn_objs[ uid ] = created_object.client_instantiate_data()

        return created_object

    def destroy( self, uid ):
        pass

    def collect_data( self ):

        return { "create": self.spawn_objs }
