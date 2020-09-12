import common.const as const
import message_objects.base_message as base_message

import json

# WebSocket Protocol Standards
# https://tools.ietf.org/html/rfc6455

# Mozilla Guide
# https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers


class BaseWebsocketMessage( base_message.Protocol ):

    # Websocket protocol opcodes
    WS_OP_CODE_CONT = 0x0  # continue from the last msg
    WS_OP_CODE_MSG  = 0x1  # string
    WS_OP_CODE_BIN  = 0x2  # binary data
    WS_OP_CODE_CLS  = base_message.Protocol._SH_OP_CODE_CLS   # close socket
    WS_OP_CODE_PING = base_message.Protocol._SH_OP_CODE_PING  # ping
    WS_OP_CODE_PONG = base_message.Protocol._SH_OP_CODE_PONG  # pong response.

    # Websocket Sub-protocol opcodes
    SUB_OP_CODE_ACEPT = base_message.Protocol._PRO_OP_CODE_ACEPT
    SUB_OP_CODE_DDATA = base_message.Protocol._PRO_OP_CODE_DDATA
    SUB_OP_CODE_IDATA = base_message.Protocol._PRO_OP_CODE_IDATA
    SUB_OP_CODE_USER  = base_message.Protocol._PRO_OP_CODE_USER

    def __init__( self ):

        # Websocket Frame Setup
        # First Byte
        self._fin = None                 # Fin bit
        self._rsv1 = None                # rsv 1 bit
        self._rsv2 = None                # rsv 2 bit
        self._rsv3 = None                # rsv 3 bit
        self._opcode = None              # opcode 4 bits
        # Second Byte
        self._use_mask = None            # mask bit
        self._payload_len = None         # payload len 7bits, if 7bit == 126, next 2 bytes, if 7bit == 127, next 8 bytes
        # remaining bytes
        self._mask = None                # mask 4 bytes (only if use_mask == True)
        self._payload = None             # The message payload.


class WebsocketReceiveMessage( BaseWebsocketMessage, base_message.BaseReceiveMessage ):

    def __init__( self ):

        super().__init__()                                      # init BaeWebsocketMessage
        super( BaseWebsocketMessage, self ).__init__( None )    # init BaseReceiveMessage
        print( self._fin )

        self.next_stage_key = "first"

    @property
    def stages( self ):
        return {
            "first":            self.__first_byte,
            "second":           self.__second_byte,
            "payload_length":   self.__payload_length,
            "mask":             self.__mask_key,
            "payload":          self.__payload
        }

    def close_connection( self ):
        return self._opcode == self.WS_OP_CODE_CLS

    def __first_byte( self, byte ):

        byte = int.from_bytes( byte, const.SOCK.BYTE_ORDER )

        # first byte.
        # fin (1) res1/2/3 (1 each) opcode (4)
        self._fin =    (byte & 0b10000000) > 0
        self._rsv1 =   (byte & 0b01000000) > 0
        self._rsv2 =   (byte & 0b00100000) > 0
        self._rsv3 =   (byte & 0b00010000) > 0
        self._opcode = (byte & 0b00001111)

        return "second", 1  # move onto the second byte

    def __second_byte( self, byte ):

        byte = int.from_bytes( byte, const.SOCK.BYTE_ORDER )
        # second byte
        # use mask (1) message len (7)
        self._use_mask =    (byte & 0b10000000) > 0
        self._payload_len = (byte & 0b01111111)

        # if payload len is 126 payload len is next 2 bytes
        # if payload len is 127 payload len is next 8 bytes
        # if payload < 126 move onto mask key if using next 4 bytes
        # else move onto the payload 'payload_len' bytes
        if self._payload_len == 126:
            return "payload_length", 2
        elif self._payload_len == 127:
            return "payload_length", 8
        else:
            if self._use_mask:
                return "mask", 4
            else:
                return "payload", self._payload_len

    def __payload_length( self, length_bytes ):

        self._payload_len = int.from_bytes( length_bytes, const.SOCK.BYTE_ORDER )

        # get mask if using other wise move onto message
        if self._use_mask:
            return "mask", 4
        else:
            return "payload", self._payload_len

    def __mask_key( self, mask_bytes ):

        self._mask = mask_bytes

        return "payload", self._payload_len

    def __payload( self, payload_bytes ):

        payload = ""
        if self._mask is not None:
            # unmask the payload
            for i in range( self._payload_len ):
                byte = payload_bytes[i]
                mask = self._mask[ i % 4 ]
                payload += chr(byte ^ mask)
        else:
            payload = payload_bytes.decode()

        print( "PL BYTES::::", payload_bytes )
        print( "PL::::", payload )
        print( "JS::::", json.loads( payload ) )

        if self._payload is None:
            self._payload = payload
        else:
            self._payload += payload

        # update the status.
        if self._fin:
            self._status = self.RECV_STATUS_SUCCESS
            return None, None
        else:
            self._status = self.RECV_STATUS_WAIT
            return "first", 1

    def convert_to_send( self, sent_callback=None ):

        return WebsocketSendMessage( self._payload, sent_callback=sent_callback )


class WebsocketSendMessage( BaseWebsocketMessage, base_message.BaseSendMessage ):

    def __init__( self, data, sent_callback=None ):

        super().__init__()                                                   # init BaseWebsocketMessage
        super( BaseWebsocketMessage, self ).__init__( data, sent_callback )  # init BaseSEndMessage

        # set our standard send message frame
        self._fin = True  # we will never send a message that needs a second frame
        self._rsv1 = False
        self._rsv2 = False
        self._rsv3 = False
        self._opcode = BaseWebsocketMessage.WS_OP_CODE_BIN
        self._use_mask = False  # Server does not use the mask bit

    def get( self ):

        # Bytes             1       2       3       4
        # Bits:             12345678123456781234567812345678  #
        two_full_bytes  = 0b1111111111111111                  #
        four_full_bytes = 0b11111111111111111111111111111111  #
        byte_order = const.SOCK.BYTE_ORDER

        message_bytes = []
        # first byte
        byte = (self._fin << 7) + \
               (self._rsv1 << 6) + \
               (self._rsv2 << 5) + \
               (self._rsv3 << 4) + \
               self._opcode

        message_bytes.append( byte.to_bytes( 1, byte_order ) )

        # second byte
        # ignore setting the mask as its never set from the server
        msg_len = None
        if self.length() <= 125:
            msg_len = self.length()
        elif self.length() > two_full_bytes:    # largest 8 byte message len
            msg_len = 127
        else: # mid 2 byte message len
            msg_len = 126

        message_bytes.append( msg_len.to_bytes( 1, byte_order ) )

        # add payload len if 126 or 127
        if msg_len == 126:
            message_bytes.append( self.length().to_bytes( 2, byte_order ) )
        elif msg_len == 127:
            message_bytes.append( self.length().to_bytes( 8, byte_order) )

        # mask bit is never set so ignore that
        # append payload :)
        message_bytes.append( self._payload.encode() )

        self._status = self.SND_STATUS_USED

        return b''.join( message_bytes )
