import { Vector2 } from "./vector2.js"

export class Transform
{
    constructor()
    {

        this.position = new Vector2(0, 0)
        this.rotation = 0
        this.scale = new Vector2(1, 1)
        this.zOrder = 0                 // lower = bottom, higher = top

    }
    
}