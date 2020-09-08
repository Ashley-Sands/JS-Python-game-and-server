import { Vector2 } from "./vector2.js"

export class Transform
{
    constructor()
    {

        this.position = new Vector2(0, 0)     // position in viewport units
        this.rotation = 0                     // rotation in degrees
        this.scale = new Vector2(1, 1)        
        this.zOrder = 0                       // lower = bottom, higher = top

    }

    /** Sets the x and y position of object in viewport units */
    SetPosition( x, y )
    {
        this.position.x = x
        this.position.y = y
    }

    /** Gets the objects position in viewport units */
    GetPosition()
    {
        return this.position
    }

    /** Sets the x and y scale of the object */
    SetScale( x, y )
    {
        this.scale.x = x
        this.scale.y = y
    }

    /** Gets the objects scale */
    GetScale()
    {
        return this.scale
    }

}