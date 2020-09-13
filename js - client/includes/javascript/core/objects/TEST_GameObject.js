import { GameObject } from "./baseObject.js"
import { Renderer   } from '../components/renderer.js'
import { Vector2 } from "../components/vector2.js"

export class TEST_GameObject extends GameObject{

    constructor(oid)
    {
        super( oid )

        this.fallSpeed = 0

    }

    get CanRender( )
    {
        return true
    }

    Tick( timeDelta )
    {
        //this.transform.rotation += 90.0 * timeDelta
        this.fallSpeed += 9.77 * timeDelta
        this.transform.position.y += this.fallSpeed
        this.transform.position.x += 55 * timeDelta
        if ( this.transform.position.y > 250 )
        {
            this.transform.position.y = 250

            var bounce = -this.fallSpeed * 0.9

            if ( bounce < -0.05)
                this.fallSpeed = bounce

        }
    }

    /**
     * 
     * @param {Camera} camera           camera that will renderer the object
     * @returns {Renderer}              renderer. Null if not visable
     */
    GetRenderer( camera )
    {
        var pos = this.transform.position
        var rot = this.transform.rotation
        var renderer = new Renderer()
        
        renderer.preRenderFunct = function(ctx){
            
            camera.SetTransform( ctx, new Vector2(0, 0), 0 )

            ctx.fillStyle = "red"
            
        }

        //renderer.renderFunct = (ctx) => ctx.fillRect( -50, -50, 100, 100 )
        renderer.renderFunct = function( ctx ){
            ctx.beginPath();
            ctx.arc(0, 0, 50, 0, 2 * Math.PI);
            ctx.fill();
        }

        return renderer

    }

}
