import { Time   } from "./components/managers/time.js";
import { Socket } from "./components/managers/socket.js";
import { Inputs } from "./components/managers/Inputs.js";


class Main
{
    constructor( fps, canvasId, consoleId, consoleInputId, consoleButtonId )
    {
        var d = document;
        /* Basic HTML Elemenets */
        this.canvas = d.getElementById( canvasId )
        this.ctx = null
        this.console = {
            window: d.getElementById( consoleId ),
            input:  d.getElementById( consoleInputId ),
            button: d.getElementById( consoleButtonId )
        }

        this.console.button.onclick = this.SendConsoleMessage.bind(this)    // temp method

        /* Managers */
        this.socket = new Socket(true, "127.0.0.1", 9091)
        this.time   = new Time()
        this.inputs = new Inputs()

        /* Objects */
        this.object_instances = {}    /* All Objects. Key: instance id, Value: object */
        this.server_objects   = {}    /* All server objects. Key: server name, Value: object*/

        this.renderers = []           /* List of all renderers visable from the viewport */
    
        this.socket.connect();

        setInterval( this.ReceiveConsoleMessage.bind(this), 1000 / fps )
        
    }

    Tick(){}
    Render(){}

    SendConsoleMessage()    // temp method
    {
        
        var message = this.console.input.value 
        if ( message.trim() != "" )
        {
            this.socket.SendMessage( message )
            this.console.input.value = ""
        }
    }

    ReceiveConsoleMessage() // temp method
    {
        
        var message = this.socket.RetriveMessage()

        while ( message != null )
        {

            this.console.window.innerHTML += `<br />00:00:00.000 | User | ${message}`
            this.console.window.scrollTop += 20 
            message = this.socket.RetriveMessage()

        }

    }

}

var m = new Main(10, "game_window", "console_win", "console_input", "console_button");

console.log( m["time"] )
m["dog"] = "cat";
console.log( m["dog"] )

/**
 * Object Instances.
 * { "object_id": object }
 * 
 * Server objects.
 * { "server_id": {obj: object, sync_vars: [] } }   // Do we even need the sync vars??
 *
 */