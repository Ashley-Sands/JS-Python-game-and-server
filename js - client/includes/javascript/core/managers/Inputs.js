import { ServerBaseObject } from "../objects/baseObject.js"

export class Inputs extends ServerBaseObject
{
    
    constructor( canvasElement )
    {
        super( "input", "input")

        this.canvasElement = canvasElement

        this.keys  = {}
        this.mouse = {}

        window.onkeydown = this.OnKeyDown.bind(this)
        window.onkeyup   = this.OnKeyUp.bind(this)
        window.onmousemove = this.OnMouseMove.bind(this)
        window.onmousedown = this.OnMouseDown.bind(this)
        window.onmouseup = this.OnMouseUp.bind(this)
        //canvasElement.onmousedown = this.OnMouseDown
        //canvasElement.onmousemove = this.OnMouseMove
        //canvasElement.onmouseup   = this.OnMouseUp

    }

    OnKeyDown( event )
    {
        console.log( event.key, event.keyCode )
        this.keys[ event.keycode ] = 1
    }

    OnKeyUp( event )
    {

        this.keys[ event.keycode ] = 0

    }

    OnMouseDown( event )
    {
        console.log( event.button, event.pageX, event.pageY )
        this.mouse[ event.button ] = 1
    }

    OnMouseMove( event )
    {
        console.log("moved")
        this.mouse["position"] = { x: event.pageX, y: event.pageY }
    }

    OnMouseUp( event )
    {
        this.mouse[ event.button ] = 0
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
