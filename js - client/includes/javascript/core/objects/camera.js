import { GameObject } from "./baseObject.js"
import { Vector2 } from "../components/vector2.js"
import { Bounds } from "../components/bounds.js"

/**
 * Camera.
 * transform.position is the center of the cam.
 * transform.scale and zOrder are both ignored.
 */
export class Camera extends GameObject
{

    constructor ( oid )
    {
        super( oid )
        
        this.__size = new Vector2()         // size of the cameras view in viewport units.
        this.__sizeBounds = new Bounds()    // the cameras view bounds (pixels)

        this.__renderers = [ ]                 /* List of all renderable objects, visable to the camera */

    }

    /**
     * Gets the cameras view in viewport units
     */
    get Size()
    {
        return this.__size
    }

    GetRelevantPosition( units )
    {
        position.Sub( this.transform.position )
    }

    GetRelevantPositionPixels( units )
    {
        position.Sub( this.transform.position ).ToPixels()
    }

    /**
     * Sets the cameras view in pixels
     * This should only be called by the viewport when the camera is set.
     * If overriding the cameras view size, make sure to set it affter seting 
     * the camera into the viewport.
     * @param {Vector2} pixels 
     */
    SetViewSize( pixels )
    {
        var x = pixels.x / 2
        var y = pixels.y / 2

        this.__size = pixels.ToUnits()
        this.__sizeBounds.SetBounds( -x, x, y, -y )
    }

    /**
     * Gets the cameras view in pixels
     */
    GetViewSize()
    {
        return this.__size.ToPixels()
    }

    /**
     * 
     * @param {BaseObject} renderObject 
     * @returns {boolean} true if successful otherwise false
     */
    AddRenderObject( renderObject )
    {

        if ( !renderObject.CanRender )  // find if the renderer is visable
            return false
        
        var renderer = renderObject.GetRenderer(this)

        if ( renderer != null )
            this.__renderers.push( renderer )

        return true
    }

    get _RenderObjects()
    {
        return this.__renderers
    }

    /**
     * Is the position visable to the camera
     * @param {Vector2} position position in world space (viewport units) 
     */
    IsVisable( position )
    {
        var relevantPosition = position.Sub( this.transform.position ).ToPixels()

        return this.__sizeBounds.Contains( relevantPosition )

    }

    /**
     * 
     * @param {Vector2} relevantPixels, pixel position relevant to the camera 
     */
    IsVisableRelevant( relevantPixels )
    {
        return this.__sizeBounds.Contains( relevantPixels )
    }

}