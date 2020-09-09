import { GameObject } from "./baseObject.js"
import { Renderer   } from '../components/renderer.js'

export class TEST_GameObject extends GameObject{

    constructor(oid)
    {
        super( oid )

        this.rot = 0

    }

    get CanRender( )
    {
        return true
    }

    /**
     * 
     * @param {Camera} camera           camera that will renderer the object
     * @param {CanvasContext2D} ctx     canvas context to render onto
     * @returns {Renderer}              renderer. Null if not visable
     */
    GetRenderer( camera )
    {

        var renderer = new Renderer()

        renderer.preRenderFunct = function(ctx){
            this.rot += 1
            var sin = Math.sin( this.rot * Math.PI / 180 )
            var cos = Math.cos( this.rot * Math.PI / 180 )

            // x-scale, x-skew, y-scale, y-skew, x-pos, y-pos
            // use transform for reletive rotation (reletive to last trasform)
            ctx.setTransform( cos, sin, -sin, cos, 150, 150 )

            ctx.fillStyle = "red"
            
        }.bind(this)

        renderer.renderFunct = (ctx) => ctx.fillRect( -50, -50, 100, 100 )

        return renderer

    }

}
