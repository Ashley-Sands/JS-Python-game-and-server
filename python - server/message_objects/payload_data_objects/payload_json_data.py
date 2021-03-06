import message_objects.payload_data_objects.payload_data as payload_data
import json
import common.DEBUG as DEBUG
_print = DEBUG.LOGS.print


class PayloadJsonData( payload_data.PayloadData ):

    def __init__( self, tick_id=0, frame_timestamp=0, target_client_sockets=None ):
        super().__init__( tick_id, frame_timestamp, target_client_sockets )

    def _parse_to_string( self ):

        try:
            string = json.dumps( self._structure )
            self._string_u2d = True
            self._string = string
            self._string_len = len( string )
        except Exception as e:
            _print( "Unable to parse to string", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR )

    def _parse_to_structure( self ):

        try:
            struct = json.loads( self._string )
            self._struct_u2d = True
            self._structure = struct
        except Exception as e:
            _print( "Unable to parse to structure", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR )