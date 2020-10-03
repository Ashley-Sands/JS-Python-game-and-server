import message_objects.base_message as base_message
import message_objects.protocols as protocols
import message_objects.payload_data_objects.payload_json_data as payload_json_data

class UnityOpcodes:

    OP_CODE_ACEPT = protocols.CommonProtocolOpcodes.PRO_OP_CODE_ACEPT
    OP_CODE_DDATE = protocols.CommonProtocolOpcodes.PRO_OP_CODE_DDATA
    OP_CODE_IDATA = protocols.CommonProtocolOpcodes.PRO_OP_CODE_IDATA
    OP_CODE_USER  = protocols.CommonProtocolOpcodes.PRO_OP_CODE_USER

    OP_CODE_PING  = protocols.CommonProtocolOpcodes.SH_OP_CODE_PING
    OP_CODE_PONG  = protocols.CommonProtocolOpcodes.SH_OP_CODE_PONG
    OP_CODE_CLS   = protocols.CommonProtocolOpcodes.SH_OP_CODE_CLS


class UnityReceiveMessage( base_message.BaseReceiveProtocolMessage, UnityOpcodes ):

    RECV_STAGE_OPT   = "option"
    RECV_STAGE_PLEN  = "payload_len"
    RECV_STAGE_FRAME = "frame_id"
    RECV_STAGE_TIMES = "timestamp"
    RECV_STAGE_PAYL  = "payload"

    def __init__( self, from_socket ):

        super().__init__( None, from_socket)
        self.next_stage_key = self.RECV_STAGE_OPT

    @property
    def stages(self):
        return {
            self.RECV_STAGE_OPT: self._set_opt_byte,
            self.RECV_STAGE_PLEN: self._set_payload_len,
            self.RECV_STAGE_FRAME: self._set_frame_id,
            self.RECV_STAGE_TIMES: self._set_time_stamp,
            self.RECV_STAGE_PAYL: self._set_payload
        }

    def close_connection( self ):
        return self._protocol_data["opcode"] == self.OP_CODE_CLS

    def accept_connection( self ):
        return self.get_protocol_value("opcode") == self.OP_CODE_ACEPT and self.get_protocol_value("acknowledged")

    def is_ping( self ):
        return self._protocol_data["opcode"] == self.OP_CODE_PING

    def is_pong( self ):
        return self._protocol_data["opcode"] == self.OP_CODE_PONG

    def _set_opt_byte( self, byte ):
        super()._set_opt_byte( byte )
        return self.RECV_STAGE_PLEN, 2

    def _set_payload_len( self, bytes ):
        super()._set_payload_len( bytes )
        return self.RECV_STAGE_FRAME, 4

    def _set_frame_id( self, bytes ):
        super()._set_frame_id( bytes )
        return self.RECV_STAGE_TIMES, 4

    def _set_time_stamp( self, bytes ):
        super()._set_time_stamp( bytes )
        return self.RECV_STAGE_PAYL, self._protocol_data["payload_length"]

    def _set_payload( self, bytes ):

        if self._payload == None:
            self._payload = payload_json_data.PayloadJsonData()

        self._payload.set_string( bytes )    # TODO. This is unclear atm how we're going to do data.
        self._status = self.RECV_STATUS_SUCCESS
        return None, None

    def convert_to_send( self, sent_callback=None, copy_sub_header=False ):

        send_message = UnitySendMessage( None, sent_callback=sent_callback )
        send_message.set( self._payload )

        if copy_sub_header:
            send_message._protocol_data = self._protocol_data

        return send_message


    def convert_to_pong( self, sent_callback=None ):
        pass


class UnitySendMessage( base_message.BaseSendProtocolMessage, UnityOpcodes ):

    HEADER_LENGTH = 11

    def __init__( self, data, sent_callback=None ):

        super().__init__( data, sent_callback )

    def get( self ):

        message_bytes  = self._get_opt_byte()
        message_bytes += self._get_payload_len_bytes()
        message_bytes += self._get_frame_id_bytes()
        message_bytes += self._get_timestamp_bytes()

        message_bytes += self._payload.get_bytes()

        self._status = self.SND_STATUS_USED

        return message_bytes
