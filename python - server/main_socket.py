import socket
from http import HTTPStatus
import threading
import hashlib
import base64
import random

class Socket:

    def __init__( self, ip, port, max_connections ):

        self.ip = ip
        self.port = port
        self.max_conn = max_connections

        self.socket = None

        self.thr_connect = None
        self.thr_lock = threading.Lock()
        self.connections = {}   # socket:

        self.__active = False

    def set_active( self, active ):

        self.thr_lock.acquire()
        self.__active = active
        self.thr_lock.release()

    def is_active( self ):

        self.thr_lock.acquire()
        active = self.__active
        self.thr_lock.release()

        return active

    def connection_count( self ):

        self.thr_lock.acquire()
        conn_count = len(self.connections)
        self.thr_lock.release()

        return conn_count

    def start( self ):

        if self.thr_connect is not None and self.thr_connect.is_alive():
            print( "Socket already running" )
            return

        try:
            self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

            self.socket.bind( (self.ip, self.port) )
            self.socket.listen( self.max_conn + 1 )  # allow 1 extra connection to prevent clients queueing
            self.set_active( True )
            print("Socket binded to", (self.ip, self.port))
        except Exception as e:
            print(e)

        self.thr_connect = threading.Thread( target=self.accept_connection, args=(self.socket,) )
        self.thr_connect.start()

    def accept_connection( self, socket_instance ):

        while self.is_active():

            sock, address = socket_instance.accept()
            print("Client Connected", address)

            # Notes, we must complete the hand shake, before we can accept the connection
            # Which is a standard http header.
            # see. https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers
            if self.connection_handshake( sock ):
                self.connections[ sock ] = sock
                byte_offset = 0
                print("connection accepted")
                d_1 = sock.recv(1)
                byte_offset += 1
                fin = (int.from_bytes(d_1, byteorder="big") & 128) != 0
                print("fin: ", fin)
                d_2 = sock.recv(1)
                byte_offset += 1
                mask = (int.from_bytes(d_2, byteorder="big") & 128) != 0
                print(mask)

                opcode = int.from_bytes( d_1, byteorder="big" ) & 15
                print(opcode)         # 1 = text, 2 = binary, ? = ping, ? = pong

                msg_len = int.from_bytes( d_2, byteorder="big" ) - 128
                print( msg_len )        # message length
                # if the msg len is 126, the message len is the next two bytes
                # if the msg len is 127, the message len is the next 8 bytes is the message length
                if msg_len == 126:
                    print("Next 2 Bytes")
                    d_3 = sock.recv( 2 )
                    byte_offset += 2
                    msg_len = int.from_bytes( d_3, byteorder="big" )

                elif msg_len == 127:
                    print("Next 8 Bytes")
                    d_3 = sock.recv( 8 )
                    byte_offset += 8
                    msg_len = int.from_bytes( d_3, byteorder="big" )
                print( "Final Len:", msg_len )  # message length

                if msg_len == 0:
                    print("empty message received")
                elif mask:
                    mask = sock.recv(4)
                    byte_offset += 4
                    message = ""
                    for i in range( msg_len ):
                        byte = int.from_bytes( sock.recv(1), "big")
                        ma = mask[i % 4]
                        message += chr(byte ^ ma)

                    print(message)

                    self.send_message( sock, "Hello Chrome :)" )

                else:
                    print("Error Mask not set, client must be disconnected!")
                    sock.close()
            else:
                print("Client has been rejected!")

    def send_message( self, client_socket, message ):

        # Packet
        # Bytes            |1              |2              |3
        # Bits:            |1|2|3|4|5|6|7|8|1|2|3|4|5|6|7|8|1|2|3|4|5|6|7|8|
        # -----------------|-|-|-|-|-------|-|-------------|---------------|
        #                  |f|r|r|r| OP    |m| message     |
        #                  |i|s|s|s| CODE  |a| length      |
        #                  |n|v|v|v|       |s|             |
        #                  | |0|1|2|       |k|             |
        #                  |---------------|---------------|
        #                  | If msg len == 126 msg len     |
        #                  |-------------------------------|
        #                  | If msg len == 127 msg len      ... 8 bytes
        #                  |-------------------------------|
        #                  | if mask, mask bytes            ... 4 bytes
        #                  |-------------------------------|
        #                  | payload                        ... msg len bytes
        #                  |-------------------------------|
        #
        byteorder = "big"
        message_length = len(message)
        # Bytes             1       2       3       4
        # Bits:             12345678123456781234567812345678  #
        one_full_byte   = 0b11111111                          #
        two_full_bytes  = 0b1111111111111111                  #
        four_full_bytes = 0b11111111111111111111111111111111  #

        message_bytes = []

        # Byte 1
        # fin, rsv1/2/3, opcode

        # Set fin to 1 and op code to
        fin  = True     # one bit (mask 0b10000000)
        rsv1 = False    # one bit (mask 0b01000000)
        rsv2 = False    # one bit (mask 0b00100000)
        rsv3 = False    # one bit (mask 0b00010000)
        opcode = 0X1    # 4 bits  (mask 0b00001111)

        byte = (fin << 7) + (rsv1 << 6) + (rsv2 << 5) + (rsv3 << 4) + opcode
        message_bytes.append( byte.to_bytes(1, byteorder) )
        print("Byte 1", byte)
        # Byte 2
        # use mask, msg len
        use_mask = False
        b2_msg_len = 0

        if message_length < 126:
            b2_msg_len = message_length
        elif message_length <= two_full_bytes:
            b2_msg_len = 126
        else:
            b2_msg_len = 127

        byte = (use_mask << 7) + b2_msg_len
        message_bytes.append( byte.to_bytes(1, byteorder) )
        print("Byte 2", byte)

        # if the message len is < 2 bytes
        if b2_msg_len == 126:
            message_bytes.append( message_length.to_bytes(2, byteorder) )
            print("b2 ml 126 (2 bytes)", message_bytes[-1])
        elif b2_msg_len == 127: # 8 bytes
            message_bytes.append( message_length.to_bytes(8, byteorder) )
            print("b2 ml 127 (8 bytes)", message_bytes[-1])

        # if using mask add the masks 4 bytes
        if use_mask:    # TODO: imporve.
            mask = random.randrange(two_full_bytes, four_full_bytes)
            mask_bytes = mask.to_bytes(4, byteorder)
            message_bytes.append( mask_bytes )
            print("mask (4 bytes)", mask_bytes)

        i = 0
        for m in message:
            if use_mask:
                byte = ord(m) ^ mask_bytes[ i ]
            else:
                byte = ord(m)

            message_bytes.append( byte.to_bytes( 1, byteorder ) )
            i = (i + 1) % 4

        out_message = b''.join(message_bytes)

        print( "All Bytes", out_message )
        client_socket.send( out_message )

    def connection_handshake( self, client_socket ):

        # this is a very crude setup, but is ok for now
        # TODO: improve ^^
        print("processing header")
        status = HTTPStatus.SWITCHING_PROTOCOLS

        try:
            client_socket.settimeout(0.5)           # it should be instance
            ws_header = client_socket.recv(1024)    # receive the header but we'll only process it if theres space on the server.
        except Exception as e:
            print(e)
            return False

        client_socket.settimeout(None)  # set the header back to blocking, as that our default behaviour

        if self.connection_count() >= self.max_conn:
            # reject client max connection reached
            status = HTTPStatus.SERVICE_UNAVAILABLE
            print( "Client Rejected, Server full." )
            return self.complete_handshake( client_socket, status )


        ws_versions = ["13"]
        check_headers = [ "host", "connection", "upgrade", "origin", "sec-websocket-version", "sec-websocket-key" ]
        required_headers = {
                             "connection":              lambda s: s == "upgrade",
                             "upgrade":                 lambda s: s == "websocket",
                             "sec-websocket-version":   lambda s: s in ws_versions,
                             "sec-websocket-key":       lambda s: True
                           }

        required_found_count = 0
        found_headers = {}  # TODO: process the non required headers

        ws_header = ws_header.decode()
        ws_headers = ws_header.split("\r\n")

        accept_client = True

        if len(ws_headers) < 6:
            # reject. not enough headers.
            status = HTTPStatus.NOT_ACCEPTABLE
            print("client Rejected. Not enough headers supplied")
            return self.complete_handshake( client_socket, status )
        elif ws_headers[-1] != "" or ws_headers[-2] != "":
            status = HTTPStatus.NOT_ACCEPTABLE
            print( "client Rejected. Header not end correctly" )
            print(ws_header, ws_headers, ws_headers[:-2], len(ws_headers[:-2]))
            return self.complete_handshake( client_socket, status )

        # check the content od the header.
        # and reject anything funky
        for i in range( len(ws_headers) ):
            if i == 0:  # http GET / Protocol
                data = ws_headers[i].split(" ")
                if len( data ) == 3 and data[0] == "GET" and data[1] == "/" and data[2] == "HTTP/1.1":
                    continue
                else:
                    accept_client = False
                    break
            else:
                data = ws_headers[i].split(": ")

                if len(data) != 2 or data[0].lower() not in check_headers:
                    continue
                else:
                    found_headers[data[0].lower()] = data[1]

        for k in found_headers:

            if k not in required_headers:
                continue
            else:
                # make sure that the headers have not been submitted more than once.
                # by setting the callback to None we know its already been process and accepted
                # So its possible that something funky is going on.
                if required_headers[k] is None or ( required_headers[k] is not None and
                                                    not required_headers[k]( found_headers[k].lower() ) ):
                    accept_client = False
                    print(k, "Failed; Already occurred? ", required_headers[k] is None)
                    break
                else:
                    required_headers[k] = None
                    required_found_count += 1

        if accept_client is False or required_found_count < len( required_headers ):
            status = HTTPStatus.NOT_ACCEPTABLE
            accept_header = ""
            print("Client Rejected")
        else:
            print("Client Accepted")
            key = self.get_client_key( found_headers["sec-websocket-key"] )
            print( found_headers["sec-websocket-key"], key)
            accept_header = "Upgrade: websocket\r\n" \
                            "Connection: Upgrade\r\n" \
                            "Sec-WebSocket-Accept: {key}\r\n".format( key=key )

        return self.complete_handshake( client_socket, status, accept_header )

    def get_client_key( self, key ):

        magic_hand_shake = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        auth_key = key + magic_hand_shake

        sha1 = hashlib.sha1()
        sha1.update( auth_key.encode() )
        auth_key = base64.encodebytes( sha1.digest() ).decode()
        if auth_key[-1] == "\n":
            auth_key = auth_key[:-1]

        return auth_key

    def complete_handshake( self, client_socket, http_status, header_response="" ):

        header_start = "HTTP/1.1 {status_code} {status_name}\r\n"

        header_start = header_start.format( status_code=http_status.value, status_name=http_status.phrase )
        header = "{header_start}{header_response}\r\n".format( header_start=header_start, header_response=header_response )

        reject = http_status != HTTPStatus.SWITCHING_PROTOCOLS
        print("OUT header::", header)
        try:
            client_socket.send( header.encode() )

            if reject:
                client_socket.close()  # A behaving client should close the connection if the header not SWITCHING PROTOCOLS but just encase
            return not reject
        except Exception as e:
            print( e )
            return False
