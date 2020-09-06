
export class Packet
{
    
    static OPCODES = {

    }

    static ENDPOINT = {
        "SEND":     0,
        "RECEIVED": 1
    }

    /** It is preferfed to use the static Send and Receive Packet methods to construct a packet.
     *  As it deals with all the heavy lifing accordingly.
     * 
     * @param {bool} acknowledgment (1 bit)
     *              Server requested acknowlegment
     * @param {bool} resync         (1 bit)
     *              Server requests that the client and server resync
     * @param {bool} agreement      (1 bit)
     *              Server requests that a new agreement is required
     * @param {bool} acknowledged    (1 bit)     
     *              Must be true when responding to acknowledgment, resync or agreement.
     *              False will resault in a rejected request.
     * @param {int} opcode          (4 bits)
     *              The operation code 
     * @param {int} frameId         (1 octet (8 bit))   / i think this needs to ~3 octets
     *              The id of the frame that generated the message  
     * @param {int} timestamp       (4 octets (32 bit)) (the left most bit must be 0 as in js its the signed bit)
     *              The timestamp of the message. 
     *                   
     */

    constructor( acknowledgment, resync, agreement, acknowledged, opcode, frameId, timestamp, endpoint)
    {
        this.__endpoint = endpoint

        this.acknowledgment = acknowledgment
        this.resync = resync
        this.agreement = agreement
        this.acknowledged = acknowledged

        this.opcode = opcode
        this.frameId = frameId
        this.timestamp = timestamp

        this.payload = {}
        
    }

    /**
     * Creates a new send packet for opcode
     */
    static SendPacket( opcode )
    {
        return new Packet( false, false, false, false,
                           opcode, this.frameId, this.timestamp, Packet.ENDPOINT.SEND )   // TODO Time module
    }

    /** 
     * Decodes a received mess buffer into a new Received packet. 
     * @param {ArrayBuffer} messageBufferArray 
     */
    static ReceivePacket( messageBufferArray )
    {

        var head = new Int8Array( messageBufferArray, 0, 6)     //
        var body = new Int8Array( messageBufferArray, 6 )       // json body

        // option byte (first byte)
        var optionByte = head[0]
        
        var acknowledgment = (optionByte & 0b10000000) != 0
        var resync         = (optionByte & 0b01000000) != 0
        var agreement      = (optionByte & 0b00100000) != 0
        var acknowledged   = false                              // the Acknowledged bit is only set to true by the client when acknowledging a message.
        var opcode         = (optionByte & 0b00001111)

        // frame id and timestamp
        var frameId = head[1]
        var frameTimeStamp = (head[2] << 24) + (head[3] << 16) + (head[4] << 8) + head[5]

        // Decode and convert the json body
        var jsonStr = new TextDecoder( 'utf-8' ).decode( body )

        var payload = JSON.parse( jsonStr )

        console.log( "packet decoded" )

        var packet = new Packet( acknowledgment, resync, agreement, acknowledged, opcode, frameId, frameTimeStamp, Packet.ENDPOINT.RECEIVED )
        packet.payload = payload

        return packet

    }

    /** Returns the acknowledge message if requested by the server
     *  otherwise null
     */
    GetAcknowledgeMessage()
    {

        if ( this.__endpoint != Packet.ENDPOINT.RECEIVED )
            throw "Unable to get Acknowledge Message for packets that are marked with endpoint 'send' "

        // acknowledgment message return same packet minus the payload
        if ( this.acknowledgment )
        {
            return new Packet( this.acknowledgment, this.resync, this.agreement, true,
                               this.opcode, this.frameId, this.timestamp, Packet.ENDPOINT.SEND )
        }

        return null
    }

    /** 
     * Adds an payload body to the messages packet.
     * @param {string} server_name 
     *                 name of object on the server.
     * @param {object} object 
     *                 the object to be added to the payload
     */
    AddPayload( server_name, object )
    {
        /**
         *  Payload Format.
         *  payload = {
         *      "server_name_1": [
         *              {   // snapshot 1...
         *              },
         *              {   // snapshot ...n
         *              }
         *          ],
         *      "server_name_2": [
         *              {   // snapshot 1...
         *              },
         *              {   // snapshot ...n
         *              }
         *          ]
         *  }
         */
        if ( this.__endpoint != Packet.ENDPOINT.SEND )
            throw "Unable to add payload data to packets that are marked with endpoint 'Received' "

        if ( server_name in this.payload )
        {
            this.payload[ server_name ].push( object )
        }
        else
        {
            this.payload[ server_name ] = [ object ]
        }

        
        console.log( `Payload added for server object '${server_name}'` )

    }

    /** 
     * Gets message ready for send to the server.
     */
    GetMessageBuffer()
    {

        if ( this.__endpoint != Packet.ENDPOINT.SEND )
            throw "Unable to send packets that are marked with endpoint 'Received' "

        var head = new Int8Array(6)
        var timestampBuffer = new Int8Array( new Int32Array( this.timestamp ) )


        var optionByte = (this.acknowledgment << 7) + (this.resync << 6) + (this.acknowledgment << 5) + (this.acknowledged << 4) + this.opcode
        
        head[0] = optionByte
        head[1] = this.frameId

        head[2] = timestampBuffer[0]
        head[3] = timestampBuffer[1]
        head[4] = timestampBuffer[2]
        head[5] = timestampBuffer[3]
        
        var jsonStr = JSON.stringify( this.payload )
        console.log("jstr: " + jsonStr )
        var payload = new TextEncoder( ).encode( jsonStr )

        var messageBuffer = new Int8Array( head.length + payload.length )
        messageBuffer.set( head )
        messageBuffer.set( payload, head.length)

        return messageBuffer
        
    }

}