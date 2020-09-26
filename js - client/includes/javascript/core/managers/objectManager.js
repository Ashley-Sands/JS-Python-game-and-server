import { ServerBaseObject } from "../objects/baseObject.js"
import { TEST_ServerGameObject } from "../objects/TEST_GameObject.js"

export class ObjecetManager extends ServerBaseObject
{

    static objects = { "test_go": ( oid, sid ) => new TEST_ServerGameObject( oid, sid ) }
    constructor( add_func, remove_func )
    {

        super( "objects", "objects" )

        this._last_oid = 0
        this.addServerObj = add_func
        this.removeServerObj = remove_func

    }

    get OID()
    {
        this._last_oid++
        return this._last_oid
    }

    CreateObject( server_id, data )
    {
        if ( data["class"] )
        {
            if ( objects[ data["class"] ] )
            {
                var createdObj = objects[ data["class"] ]( this.OID, server_id )
                this.addServerObj( server_id, createdObj )
            }
            else
            {
                console.warn("Unable to create objects. Class not found (class: ", data["class"], ")")
            }
        }
        else
        {
            console.warn("Unable to create objects. Class not supplied.")
        }

    }

    ApplyData( frameData )
    {
        for ( var frame in frameData )
        {

            if ( frame["create"] )
            {
                for ( var sId in frame["create"] )
                    this.CreateObject( sid, frame["create"][sid]  )
            }

            if ( frame[ "destroy" ] )
            {
                for ( var obj in frame["destroy"] )
                    this.removeServerObj( obj["id"] )
            }

        }        
    }

    CollectData( sinceTime=0.0 )   
    {
        // never spwan or destroy objects from the client...
        return null
    }

}