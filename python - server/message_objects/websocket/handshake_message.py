# Processes and validates the websockets handshake
# and gets the responce message
from common.const import SOCK
from http import HTTPStatus
import message_objects.base_handshake_message as base_handshake_message
import common.DEBUG as DEBUG

_print = DEBUG.LOGS.print
# TODO: rename to WebsocketHandshakeMessage
class HandshakeMessage( base_handshake_message.BaseHandshakeMessage ):

    HTTP_VERSION = "HTTP/1.1"

    @property
    def HEADER_TERMINATOR( self ):
        return "\r\n\r\n"

    @property
    def HEADER_JOIN( self ):
        return "\r\n"

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

        headers = handshake_str.split( self.HEADER_JOIN )
        header_count = len( headers )

        if header_count < required_header_line_count:
            # Reject the client, not enough heads supplied.
            _print("Client Rejected: Not enough headers supplied", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            self.set_response_status( HTTPStatus.NOT_ACCEPTABLE )
            return
        elif headers[ -1 ] != "" and headers[ -2 ] != "":
            # Reject the client, header section is not ended correctly
            _print( "Waring: Client Rejected: Header incorrectly ended", message_type=DEBUG.LOGS.MSG_TYPE_WARNING )
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
                    _print( "Client Rejected: Bad request line", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                    _print( HTTPStatus.BAD_REQUEST.value, "(", HTTPStatus.BAD_REQUEST.phrase, ")", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
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
            _print( "Client Rejected: Client failed to supply all required headers", message_type=DEBUG.LOGS.MSG_TYPE_WARNING )
            _print( "Supplied Header:", headers )
            self.set_response_status( HTTPStatus.NOT_ACCEPTABLE )
            return

        # accept the client
        _print("Accepting Client")
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

        if len(self._response) == 0:
            self._response.append(header_status)
        else:
            self._response[0] = header_status

    def add_header( self, header_key, header_value ):

        header = f"{header_key}: {header_value}"

        if len(self._response) == 0:
            _print("Dont forget to set the status", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            self._response.append("")    # add an empty line for the status so no headers get over writen

        self._response.append( header )

    def magic_hand_shake( self ):
        return "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
