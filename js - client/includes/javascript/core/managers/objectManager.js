import { ServerBaseObject } from "../objects/baseObject.js"
import { TEST_ServerGameObject } from "../objects/TEST_GameObject.js"

export class ObjecetManager extends ServerBaseObject
{

    static objects = { "TEST_ServerObject": ( oid, sid ) => new TEST_ServerGameObject( oid, sid ) }
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

        console.log( "CreateObject DATA: ", data )

        if ( data["class"] )
        {
            var object = ObjecetManager.objects[ data["class"] ]
            if ( object )
            {
                var oid = this.OID
                var createdObj = object( oid, server_id )
                this.addServerObj( oid, server_id, createdObj )
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
            var data = frameData[ frame ]

            if ( data["create"] )
            {
                for ( var sid in data["create"] )
                    this.CreateObject( sid, data["create"][sid]  )
            }

            if ( data[ "destroy" ] )
            {
                console.log(" DESTROY: ", data["destroy"] )
                for ( var i in data["destroy"] )
                    this.removeServerObj( data["destroy"][i] )
            }

        }        
    }

    CollectData( sinceTime=0.0 )   
    {
        // never spwan or destroy objects from the client...
        return null
    }

}