import { ServerGameObject } from "./baseObject.js"
import { Renderer   } from '../components/renderer.js'
import { Vector2 } from "../components/vector2.js"

export class TEST_ServerGameObject extends ServerGameObject{

    constructor(oid, sid)
    {
        super( oid, sid )

        this.fallSpeed = 0
    }

    get CanRender( )
    {
        return true
    }

    Tick( timeDelta )
    {
    }

    /**
     * 
     * @param {Camera} camera           camera that will renderer the object
     * @returns {Renderer}              renderer. Null if not visable
     */
    GetRenderer( camera )       // TODO. Hmmmm. CanRender in BaseObject
    {
        var pos = camera.GetRelevantPosition( this.transform.position )
        var rot = this.transform.rotation
        var scale = this.transform.scale

        var renderer = new Renderer()
        
        if ( !camera.IsVisableRelevant( pos ) )
            return null

        //renderer.renderFunct = (ctx) => ctx.fillRect( -50, -50, 100, 100 )
        renderer.renderFunct = function( ctx ){

            camera.SetTransform( ctx, pos, rot )
            ctx.fillStyle = "red"

            ctx.beginPath();
            ctx.scale( scale.x, scale.y) ;//scale.x, scale.y )

            //ctx.arc(0, 0, 50, 0, 2 * Math.PI);
            ctx.fillRect(-15, -15, 30, 30)
            ctx.fill();

            camera.SetTransform( ctx, new Vector2(0,0), rot )

            ctx.beginPath();
            ctx.fillStyle = "green"


            //ctx.arc(0, 0, 50, 0, 2 * Math.PI);
            ctx.fillRect(-15, -15, 30, 30)
            ctx.fill();
            
        }

        return renderer

    }

    ApplyData( frameData )
    {
        if ( frameData[0]["transform"]["rotation"] )
            this.transform.rotation   = frameData[0]["transform"]["rotation"]

        if ( frameData[0]["transform"]["position"] )
        {   
            this.transform.position.x = frameData[0]["transform"]["position"]["x"]
            this.transform.position.y = frameData[0]["transform"]["position"]["y"]
        }
        
        if ( frameData[0]["transform"]["scale"] )
        {
            this.transform.scale.x    = frameData[0]["transform"]["scale"]["x"] 
            this.transform.scale.y    = frameData[0]["transform"]["scale"]["y"] 
        }
        
    }

    CollectData(){}

}
