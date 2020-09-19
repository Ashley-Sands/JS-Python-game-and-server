import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class WorldClient:

    def __init__( self, socket, client_id, display_name, client_managers={} ):
        """

        :param socket:          Raw socket that belongs to client
        :param display_name:    Client display name
        :param client_managers: Dict of managers to be defined to user.
        """

        self.socket = socket
        self.client_id = client_id
        self.display_name = display_name
        self.managers = client_managers
        self._world = None

    def set_world( self, world ):

        if self._world == world:
            _print( f"Client {self.client_id} already assigned to world" )
            return

        if self._world is not None:
            self._world.client_leave( self )

        self._world.client_join( self )

    def get_world( self ):
        return self._world

    def contains_manager( self, manager_name ):
        return manager_name in self.managers

    def set_managers( self, managers ):
        """

        :param managers:    Dict of managers {Key: manager server name, Value: manager}
        :return:            None
        """
        # TODO: i think this should only add new managers.
        #       If a manager of name is already set it and of the same type
        #       it should just be ignored.
        self.managers = { **self.managers, **managers }

    def get_manager( self, manager_name ):
        """ Get manager of name assigned to client. returns None if no manager is found. """

        try:
            return self.managers[ manager_name ]
        except:
            return None

    def tick_manager( self ):

        for man in self.managers:
            self.managers[ man ].tick( )

    def apply_manager_data( self, manager_name, data ):
        """ Attempts to apply data to a client manager.
            :return:    True if successful otherwise False
        """
        try:
            self.managers[ manager_name ].apply_data( data )
            return True
        except KeyError as e:
            _print( f"Unable to apply data to client manager. Manager {e} does not exist ", message_type=DEBUG.LOGS.MSG_TYPE_WARNING )
        except Exception as e:
            _print( f"Unable to apply data to client manager. ({e})", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )

        return False

    def collect_manager_data( self ):   # not sure if we need this.
        return None
