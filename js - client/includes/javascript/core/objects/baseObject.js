import { Transform } from "../components/transform.js"

export class BaseObject
{
    
    constructor( oid )
    {
        this.objectId = oid;     // Object id (local id)
    }

    /** Include CanRender and Render in the base object
     *  so we dont need a list for render and non render objects
     *  rather we can just update all objects in one pass and 
     *  collect the objects that need rendering.
     */

    /** Can the object be renderer.
     *  This should only return true if object is able to render.
     *  ie. render has been implermented and object is visable.
     *  @return {boolean} True the object is collected for rendering
     *                    False the objecy will not be collected for rendering
     */
    get CanRender()
    {
        return false
    }

    Render()
    {
        throw "'Render' Not Implermented Exeception"
    }

    // ...
    get IsServerObject()
    {
        return false
    }

}

export class ManagerObject extends BaseObject
{
    constructor( oid )
    {
        super( oid )
    }

}

export class GameObject extends BaseObject
{

    constructor( oid )
    {
        super( oid )

        this.transform = new Transform()

    }

}

// use a mix-in class for server objects so we dont have to have multiply server defs.
// Server Objects must only extend BaseObject, ManagerObject or GameObjects
export const ServerObject = (obj) => class extends obj
{
    constructor(oid, sid)
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

    get IsServerObject()
    {
        return true;
    }
    
}