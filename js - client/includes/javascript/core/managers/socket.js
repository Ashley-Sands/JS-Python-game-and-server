import { Packet } from "../packets/Packet.js"
import { GameConsole } from "./gameConsole.js"

export class Socket
{

    static DEBUG = false

    constructor(local, address, port, root="/")
    {
        var protocol = local ? "ws://" : "wss://";
        this.webAddress = `${protocol}${address}:${port}${root}`

        this._hasError = false
        this._connecting = false
        this._isConnected = false

        this._socket = null
        
        this._receivedMessages = []

        this.retryTimeout = 5
        this.attamps = 0

    }

    connect(){

        if ( !this._isConnected || this._hasError )
        {
            this._connecting = true

            GameConsole.instance.AddMessage( "Connecting...", "SYSTEM" )

            if (this._socket != null && this._hasError && (!this._socket.CLOSED && !this._socket.CLOSING))
                this._socket.close()

            this._socket = new WebSocket( this.webAddress )
            this._socket.binaryType = "arraybuffer"

            this._socket.onopen    =    this.__SocketOpen.bind(this)
            this._socket.onclose   =    this.__SocketClose.bind(this)
            this._socket.onmessage =    this.__SocketReceive.bind(this)
            this._socket.onerror   =    this.__SocketError.bind(this)

        }
        else
        {
            console.log("Already Connected!")
        }

    }

    __SocketOpen( e )
    {

        this._isConnected = true;
        this.attamps = 0

        GameConsole.instance.AddMessage( "Connected", "SYSTEM" )

        // notifiy the server that we have accepted the connection.
        var acknowledgedPacket = Packet.SendPacket( Packet.OPCODES.ACCEPTED_CONNECTION )
        acknowledgedPacket.acknowledged = true

        this.SendMessage( acknowledgedPacket )

        console.log("Sent Acknowledged Packet")

    }

    __SocketClose( e )
    {
        GameConsole.instance.AddMessage( "Connection Closed", "SYSTEM" )
        this.RetryConnection()
        this._isConnected = false
    }

    __SocketReceive( e )
    {
        if ( Socket.DEBUG )
            console.log("Message Received");

        this._receivedMessages.push( Packet.ReceivePacket( e.data ) )
    }

    __SocketError( e )
    {

        if ( this._connecting )
        {
            GameConsole.instance.AddMessage( "Unable to connect to server", "SYSTEM", null, GameConsole.MESSAGE_TYPE.ERROR )
        }
        else
        {
            GameConsole.instance.AddMessage( "Connection error", "SYSTEM", null, GameConsole.MESSAGE_TYPE.ERROR )
        }
        

        this._hasError = true
        this._connecting = false
    }

    RetryConnection()
    {
        this._hasError = false
        this.attamps++
        GameConsole.instance.AddMessage( `Retring in ${this.retryTimeout+this.attamps} seconds`, "SYSTEM" )
        setTimeout( this.connect.bind(this), (this.retryTimeout+this.attamps)*1000 )
    }

    /**
     * 
     * @param {Packet} packet 
     */
    SendMessage( packet )
    {
        if ( this._isConnected && !this._hasError )
        {
            var message = packet.GetMessageBuffer()
            this._socket.send( message )
        }
        else
        {
            console.log( `Unable to send message IsConnected: ${this._isConnected} HasError: ${this._hasError}` );
        }
    }

    /**
     * @returns {Packet} received packet or null if not packets to be retrived.
     */
    RetriveMessage()
    {
        if ( this._receivedMessages.length > 0)
            return this._receivedMessages.shift()
        else
            return null
    }


}