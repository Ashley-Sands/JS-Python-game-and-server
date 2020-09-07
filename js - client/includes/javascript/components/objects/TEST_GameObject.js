import {GameObject} from "../objects/baseObject.js"


export class TEST_GameObject extends GameObject{

    constructor(oid)
    {
        super( oid )

        this.rot = 0

    }

    get CanRender()
    {
        return true
    }

    Render( ctx )
    {
        this.rot += 0.1
        var sin = Math.sin( this.rot * Math.PI / 180 )
        var cos = Math.cos( this.rot * Math.PI / 180 )

        // x-scale, x-skew, y-scale, y-skew, x-pos, y-pos
        // use transform for reletive rotation (reletive to last trasform)
        ctx.setTransform( cos, sin, -sin, cos, 150, 150 )

        ctx.fillStyle = "red"
        ctx.fillRect( -50, -50, 100, 100 )

    }

}
