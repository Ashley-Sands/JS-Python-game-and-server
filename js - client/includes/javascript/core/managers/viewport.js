import { ManagerObject } from "../objects/baseObject.js"
import { Vector2 } from "../components/vector2.js"

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

        this.flags = {
            clean: true
        }

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
        this.canvasCtx.setTransform( 1, 0, 0, 1, 0, 0 )
        this.canvasCtx.clearRect( 0, 0, this.width, this.height )
        this.flags.clean = true
    }

    /** Draws all objects visable from the active camera */
    Draw()
    {

        this.Clear()

        if ( this.__activeCamera == null )
        {
            this.canvasCtx.font = "30px Arial";
            this.canvasCtx.textAlign = "center"
            this.canvasCtx.textBaseline = "middle"
            this.canvasCtx.fillText("No Active Camera Set!", this.width/2, this.height/2, this.width)
            return
        }
        this.canvasCtx.fillStyle = "blue"
        this.canvasCtx.arc(0, 0, 75, 0, 2 * Math.PI);
        this.canvasCtx.fill();

        // TODO: Render the active cameras visable objects
        this.flags.clean = false
        var renderers = this.__activeCamera._RenderObjects;

        for ( var i = 0; i < renderers.length; i++ )
            renderers[i].Render( this.canvasCtx )

    }

    /**
     * 
     * @param {Camera} camera 
     */
    SetActiveCamera( camera )
    {

        camera.SetViewSize( new Vector2(this.width, this.height) )
        this.__activeCamera = camera

    }

    /** Clears the active cameras renderer objects */
    ClearCameraRenderer()
    {
        this.__activeCamera.ClearRenderer()
    }
    /** Static Methods */

    /**
     * 
     * @param {float} unit unit to convert to pixels
     */
    static UnitsToPixels( unit )
    {
        return unit * Viewport.PIXELS_PER_UNIT
    }

    /**
     * 
     * @param {int} pixels pixels to convert to units
     */
    static PixelsToUnits( pixels )
    {
        return pixels / Viewport.PIXELS_PER_UNIT
    }
}