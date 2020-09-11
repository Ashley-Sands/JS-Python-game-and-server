# Processes and validates the websockets handshake
# and gets the responce message
from common.const import SOCK
from http import HTTPStatus
import hashlib
import base64
import message_objects.base_handshake_message as base_handshake_message


class HandshakeMessage( base_handshake_message.BaseHandshakeMessage ):

    HTTP_VERSION = "HTTP/1.1"

    def __init__( self, data, completed_handshake_callback ):
        super().__init__( data, completed_handshake_callback )

    def set( self, handshake_str ):
        """

        :param handshake_str:   The handshake that the client sent to the server
        :return:                None
        """

        # to complete the handshake we must agree with the client to
        # switch the protocol from http to websocket, Along with ensuring that
        # all the required headers have been set and finally we must return the
        # handshake key.

        client_headers = { }  # a dict with the clients accepted headers

        # set defaults
        root_path = "/"
        accepted_http_version = self.HTTP_VERSION   # Websockets require http/1.1 or greater
        accepted_http_method = "GET"                # Websockets require that the method is GET

        accepted_socket_versions = [ ]

        # websockets don't require the user agent or origin headers,
        # but its good practices to check there at least set anyway.
        blocked_user_agents = [ ]
        accepted_origins = [ ]

        validate_required_headers = {
            "user-agent":               lambda s: len( accepted_socket_versions ) == 0 or s not in blocked_user_agents,
            "origin":                   lambda s: len( accepted_origins ) == 0 or s in accepted_origins,
            # chromium based browsers only use 'upgrade' while FF base browsers are 'keep-alive, upgrade'
            "connection":               lambda s: s == "upgrade" or s == "keep-alive, upgrade",  # TODO: should make this more robust really
            "upgrade":                  lambda s: s == "websocket",  # ws required
            "sec-websocket-version":    lambda s: len( accepted_socket_versions ) == 0 or s in accepted_socket_versions,  # ws required
            "sec-websocket-key":        lambda s: True  # we just require that this has been set, to start with.            # ws required
        }

        required_header_line_count = len( validate_required_headers ) + 2  # there should be to empty lines at the end, which defines the header ending

        headers = handshake_str.split( "\r\n" )
        header_count = len( headers )

        if header_count < required_header_line_count:
            # Reject the client, not enough heads supplied.
            print("Warning: Client Rejected: Not enough headers supplied")
            self.set_response_status( HTTPStatus.NOT_ACCEPTABLE )
            return
        elif headers[ -1 ] != "" and headers[ -2 ] != "":
            # Reject the client, header section is not ended correctly
            print( "Waring: Client Rejected: Header incorrectly ended" )
            self.set_response_status( HTTPStatus.NOT_ACCEPTABLE )
            return

        # check the content of the headers.
        for i in range( header_count ):
            # Check that the first line is the `METHOD PATH PROTOCOL` line
            if i == 0:
                data = headers[ i ].split( " " )
                if len( data ) == 3 and data[ 0 ] == accepted_http_method and data[ 1 ] == root_path and data[ 2 ] == accepted_http_version:
                    continue
                else:
                    # reject the client. Client sent a bad `METHOD PATH PROTOCOL` line
                    print( "Error: Client Rejected: Bad request line" )
                    print( HTTPStatus.BAD_REQUEST.value, "(", HTTPStatus.BAD_REQUEST.phrase, ")" )
                    self.set_response_status( HTTPStatus.BAD_REQUEST )
                    return
            else:  # verify headers
                data = headers[ i ].split( ": " )  # header key: header value
                data_parts = len( data )

                if data_parts == 2 and data[ 0 ].lower() in validate_required_headers:  # ignore non required headers
                    if validate_required_headers[ data[ 0 ].lower() ]( data[ 1 ].lower() ):
                        client_headers[ data[ 0 ].lower() ] = data[ 1 ]
                    # we wont reject if a header fails, as it could be set again and be valid.
                    # This would be bad practice but we'll allow it for now at least.

        # verify that all the required headers have found found
        if len( client_headers ) != len( validate_required_headers ):
            # reject the client, Client failed to supply all required headers
            print( "Waring: Client Rejected: Client failed to supply all required headers" )
            self.set_response_status( HTTPStatus.NOT_ACCEPTABLE )
            return

        # accept the client
        print("Accepting Client")
        self.set_response_status( HTTPStatus.SWITCHING_PROTOCOLS )
        self.add_header( "Upgrade", "websocket" )
        self.add_header( "Connection", "Upgrade" )
        self.add_header( "Sec-WebSocket-Accept", self.get_response_key( client_headers["sec-websocket-key"] ) )

    def set_response_status( self, http_status ):
        """ sets the status line
        :param http_status:     HTTPStatus
        """
        self.accepted = HTTPStatus.SWITCHING_PROTOCOLS == http_status  # reject the client if not switching protocol
        header_status = f"{self.HTTP_VERSION} {http_status.value} {http_status.phrase}"

        if len(self.__response) == 0:
            self.__response.append(header_status)
        else:
            self.__response[0] = header_status

    def add_header( self, header_key, header_value ):

        header = f"{header_key}: {header_value}"

        if len(self.__response) == 0:
            print("Warning: Dont forget to set the status")
            self.__response.append("")    # add an empty line for the status so no headers get over writen

        self.__response.append( header )

    def get_response_key( self, client_key ):
        """Gets the servers handshake response key"""
        magic_hand_shake = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        auth_key = client_key + magic_hand_shake

        sha1 = hashlib.sha1()
        sha1.update( auth_key.encode() )
        auth_key = base64.encodebytes( sha1.digest() ).decode()
        if auth_key[-1] == "\n":
            auth_key = auth_key[:-1]

        return auth_key
