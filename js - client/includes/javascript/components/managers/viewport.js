import { ManagerObject } from "../objects/baseObject.js"

export class Viewport extends ManagerObject
{

    static PIXELS_PER_UNIT = 10
    
    constructor (canvasElement)
    {
        super("viewport-0")

        this.canvasElement = canvasElement
        this.canvasCtx = canvasElement.getContext("2d")

        this.width = 800
        this.height = 600

        this.__activeCamera = null

        this.UpdateSize()

    }

    UpdateSize()
    {
        this.canvasElement.width = this.width
        this.canvasElement.height = this.height
    }

    /** Clear Viewport window */
    Clear()
    {
        this.canvasCtx.clearRect( 0, 0, this.width, this.height )
    }

    /** Draws all objects visable from the active camera */
    Draw()
    {

        if ( this.__activeCamera == null )
        {
            this.canvasCtx.font = "30px Arial";
            this.canvasCtx.textAlign = "center"
            this.canvasCtx.textBaseline = "middle"
            this.canvasCtx.fillText("No Active Camera Set!", this.width/2, this.height/2, this.width)
            return
        }

        // TODO: Render the active cameras visable objects

    }

    SetActiveCamera( camera )
    {
        this.__activeCamera = camera
    }

    

}