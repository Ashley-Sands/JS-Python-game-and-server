import world_models.core.managers.base_manager as base_manager
import world_models.core.components.vector as vector

import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print

class InputManager( base_manager.BaseManager ):

    def __init__(self, obj_id):

        super().__init__( obj_id )

        self.inputs = { "mouse": {}, "keys": {} }

    def key_down( self, key_name ):
        try:
            return self.inputs["keys"][key_name] == 1
        except:
            return False

    def key_up( self, key_name ):
        try:
            return self.inputs["keys"][key_name] == 0
        except:
            return False

    def mouse_down( self, button_idx ):  #1=left, 2=right, 3=middle ...
        try:
            return self.inputs["mouse"][button_idx] == 1
        except:
            return False

    def mouse_up( self, button_idx ):
        try:
            return self.inputs["mouse"][button_idx] == 0
        except:
            return False

    def mouse_position( self ):
        try:
            x = self.inputs["mouse"]["position"]["x"]
            y = self.inputs["mouse"]["position"]["y"]
            return vector.Vector2( x, y )
        except:
            return vector.Vector2()

    def apply_data( self, data ):
        """Applies frame data received form client"""
        for d in data:
            _print("pApply:", self.inputs, d )
            if "mouse" in d:
                self.inputs["mouse"] = { **self.inputs["mouse"], **d["mouse"] }

            if "keys" in d:
                self.inputs["keys"] = { **self.inputs["keys"], **d["keys"]}

            _print("INPUTS:", d)
            _print( "POST", self.inputs )

