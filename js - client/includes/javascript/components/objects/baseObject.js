
export class BaseObject{
    
    constructor( oid )
    {
        this.objectId = oid;     // Object id (local id)
    }

}

export class ServerObject extends BaseObject
{
    constructor(ois, sid)
    {
        super(oid)
        this.serverId = sid     // Server id (remote id)
    }

    /**
     * Applies data received from server
     * @param {Array} frameData  data Array Object received from server
     *                           This sould be all frame data recevied for this server object
     *                           ie. [   // frame
     *                                  { },     // snapshot 1...
     *                                  { }      // snapshot ...n
     *                               ]
     *            
     */
    ApplyData( frameData ){}

    /**
     * @param {Float} sinceTime time since to collect data for, any data befor this time is discarded
     * @returns {Array} frame data snapshoots since last collection
     */
    CollectData( sinceTime=0.0 ){}
    
}