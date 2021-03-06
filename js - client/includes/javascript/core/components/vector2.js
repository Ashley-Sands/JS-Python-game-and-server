import { Imports } from '../../imports.js'

export class Vector2
{

    constructor(x, y)
    {
        this.x = x
        this.y = y

    }


    ToUnits()
    {
        
        var x = Imports.Viewport.PixelsToUnits(this.x)
        var y = Imports.Viewport.PixelsToUnits(this.y)
        return new Vector2( x, y )
    }

    ToPixels()
    {

        var x = Imports.Viewport.UnitsToPixels(this.x)
        var y = Imports.Viewport.UnitsToPixels(this.y)
        return new Vector2( x, y )
    }

    Add( vect2 )
    {
        var x = vect2.x + this.x
        var y = vect2.y + this.y
        return new Vector2( x, y )
    }

    Sub( vect2 )
    {
        var x = this.x - vect2.x
        var y = this.y - vect2.y
        return new Vector2( x, y )
    }

}
