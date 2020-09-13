
class ProtocolOpcodes:
    """ Common Opcodes
        Common Opcodes should not be accessed directly,
        rather use the opcodes defined in the appropriate message type
    """
    # See 'python - server/../protocol.md' for op-code and Packet descriptions.
    # Shared Op-codes
    _SH_OP_CODE_CLS  = 0x8  # Close Socket
    _SH_OP_CODE_PING = 0x9  # Ping
    _SH_OP_CODE_PONG = 0xA  # Pong (Ping response)

    # Protocol Standared Opcodes (Sub protocol for WS or Primary for Unity)
    _PRO_OP_CODE_ACEPT = 0x0    # Connection accepted
    _PRO_OP_CODE_IDATA = 0x1    # Initial Data  (Initial Game Data or agreement)
    _PRO_OP_CODE_DDATA = 0x2    # Delta Data    (Game Delta Data)
    _PRO_OP_CODE_USER  = 0x3    # User Update


class BaseProtocol:

    def __init__( self ):

        self._protocol_data = {
            "acknowledgment":   False,
            "resync":           False,
            "agreement":        False,
            "acknowledged":     False,
            "opcode":           15,
            "payload_length":   0,     # including sub protocol headers, but should match self._payload_length as is the most inner protocol
            "frame_id":         0,
            "timestamp":        0
        }


class BaseWebsocketProtocol( ProtocolOpcodes ):

    # Websocket protocol opcodes
    WS_OP_CODE_CONT = 0x0  # continue from the last msg
    WS_OP_CODE_MSG  = 0x1  # string
    WS_OP_CODE_BIN  = 0x2  # binary data
    WS_OP_CODE_CLS  = ProtocolOpcodes._SH_OP_CODE_CLS   # close socket
    WS_OP_CODE_PING = ProtocolOpcodes._SH_OP_CODE_PING  # ping
    WS_OP_CODE_PONG = ProtocolOpcodes._SH_OP_CODE_PONG  # pong response.

    # Websocket Sub-protocol opcodes
    SUB_OP_CODE_ACEPT = ProtocolOpcodes._PRO_OP_CODE_ACEPT
    SUB_OP_CODE_DDATA = ProtocolOpcodes._PRO_OP_CODE_DDATA
    SUB_OP_CODE_IDATA = ProtocolOpcodes._PRO_OP_CODE_IDATA
    SUB_OP_CODE_USER  = ProtocolOpcodes._PRO_OP_CODE_USER

    SUB_HEADER_LENGTH = 9

    def __init__( self ):

        # Websocket Frame Setup
        self._ws_protocol = {
            # First Byte
            "fin": True,
            "rsv1": False,
            "rsv2": False,
            "rsv3": False,
            "opcode": self.WS_OP_CODE_BIN,
            # Second byte
            "use_mask": False,
            "payload_length": 0,  # (or Bytes 3-4 or 3-11)  # including sub protocol headers
            # Remaining bytes
            "mask": b'',
        }
