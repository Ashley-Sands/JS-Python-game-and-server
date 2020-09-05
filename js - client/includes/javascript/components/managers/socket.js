
export class Socket
{
    constructor(local, address, port, root="/")
    {
        var protocol = local ? "ws://" : "wss://";
        this.webAddress = `${protocol}${address}:${port}${root}`

        this._hasError = false;
        this._isConnected = false;

        this._socket = null;
        
        this._receivedMessages = []

    }

    connect(){

        if ( !this._isConnected || this._hasError )
        {

            if (this._socket != null && this._hasError && (!this._socket.CLOSED || this._socket.CLOSING))
                this._socket.close()

            this._socket = new WebSocket( this.webAddress );

            this._socket.onopen    =    this.__SocketOpen.bind(this);
            this._socket.onclose   =    this.__SocketClose.bind(this);
            this._socket.onmessage =    this.__SocketReceive.bind(this);
            this._socket.onerror   =    this.__SocketError.bind(this);

        }
        else
        {
            console.log("Already Connected!")
        }

    }

    __SocketOpen( e )
    {
        console.log("Socket Opened");
        this._isConnected = true;
    }

    __SocketClose( e )
    {
        console.log("Socket Closed");
        this._isConnected = false
    }

    __SocketReceive( e )
    {
        console.log("Message Received");
        this._receivedMessages.push( e.data )
    }

    __SocketError( e )
    {
        console.log("Socket Error");
        this._hasError = true;
    }

    SendMessage( message )
    {
        if ( this._isConnected && !this._hasError )
            this._socket.send( message )
        else
            console.log( `Unable to send message IsConnected: ${this._isConnected} HasError: ${this._hasError}` );
    
    }

    RetriveMessage()
    {
        if ( this._receivedMessages.length > 0)
            return this._receivedMessages.shift()
        else
            return null
    }


}