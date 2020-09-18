import { ServerBaseObject } from "../objects/baseObject.js"

export class Inputs extends ServerBaseObject
{
    
    constructor( canvasElement )
    {
        super( "input", "input")

        this.canvasElement = canvasElement

        this._key_values  = {}
        this._mouse_values = {}

        // changed values.
        this.keys  = {}     
        this.mouse = {}

        window.onkeydown = this.OnKeyDown.bind(this)
        window.onkeyup   = this.OnKeyUp.bind(this)
        window.onmousedown = this.OnMouseDown.bind(this)
        window.onmouseup = this.OnMouseUp.bind(this)
        //canvasElement.onmousedown = this.OnMouseDown
        //canvasElement.onmousemove = this.OnMouseMove
        //canvasElement.onmouseup   = this.OnMouseUp

    }

    // for keys i would perfer to use keycodes.
    // but theres a bit of work to be done.
    // ie del is 46 but we can determin the correct code, using event.location
    // see https://keycode.info/
    // TODO: Only update inputs if changed.
    __OnKey( event, value )
    {
        try
        {
            if (this._key_values[event.key] == value)
                return
        }
        finally
        {
            this._key_values[ event.key ] = value
        }

        this.keys[ event.key ] = value
    }

    OnKeyDown( event )
    {
        console.log( event.key, ":::", event.keyCode )
        
        this.__OnKey( event, 1)
        
    }

    OnKeyUp( event )
    {
        this.__OnKey( event, 0)
    }

    __OnMouse( event, value )
    {
        try
        {
            if (this._mouse_values[event.button] == value)
                return
        }
        finally
        {
            this._mouse_values[ event.button ] = value
        }

        this.mouse[ event.button ] = value
        this.mouse["position"] = { x: event.pageX, y: event.pageY }

    }

    OnMouseDown( event )
    {
        console.log( event.button, event.pageX, event.pageY )
        this.__OnMouse( event, 1 )
    }

    OnMouseUp( event )
    {
        this.__OnMouse( event, 0 )
    }

    CollectData( sinceTime=0.0 )
    {
        var keys = this.keys
        var mouse = this.mouse

        this.keys = {}
        this.mouse = {}

        var inputs = {}
        var hasInput = false

        if ( Object.keys( keys ).length > 0 )
        {
            inputs["keys"] = keys
            hasInput = true
        }

        if ( Object.keys( mouse ).length > 0 )
        {
            inputs["mouse"] = mouse
            hasInput = true
        }

        if (hasInput)
            return [inputs]
        else
            return null
    }

}
