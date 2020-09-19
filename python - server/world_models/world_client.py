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
