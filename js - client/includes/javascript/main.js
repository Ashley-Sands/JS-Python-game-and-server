import { Time   } from "./components/managers/time.js";
import { Socket } from "./components/managers/socket.js";
import { Inputs } from "./components/managers/Inputs.js";
import { Packet } from "./components/packets/Packet.js";
import { GameConsole } from "./components/managers/gameConsole.js";

class Main
{
    constructor( fps, canvasId, consoleId, consoleInputId, consoleButtonId )
    {
        var d = document;
        /* Basic HTML Elemenets */
        this.canvas = d.getElementById( canvasId )
        this.ctx = null

        /* Data */
        var currentFramePacket = Packet.SendPacket(0)   // the next frame to be sent
        var lastFramePacket = null                      // the frame being sent (or just sent)

        /* Managers */
        this.socket  = new Socket(true, "127.0.0.1", 9091)
        this.time    = new Time()
        this.inputs  = new Inputs()
        this.console = new GameConsole( consoleId, consoleInputId, consoleButtonId, "console_user_input")
        
        /* Objects */
        this.renderers = []           /* List of all renderers visable from the viewport */
        this.objectInstances = {}    /* All Objects. Key: instance id, Value: object */
        this.serverObjects   = {}    /* All server objects. Key: server name, Value: object*/

        /* Set up default server objects */
        this.serverObjects[ this.console.serverId ] = this.console
    
        this.socket.connect();

        setInterval( this._Main.bind(this), 1000 / fps )
        
    }

    /** 
     * Main Loop
     * 1 - Apply Frame Data
     * 2 - Tick Frame
     * 3 - Collect Frame Data
     * 4 - Render
     */
    _Main(){

        this.ApplyFrameData()
        this.Tick()
        this.CollectFrameData()
        this.Render()
    }

    /** Receive all packets applying all data to each server object */
    ApplyFrameData()
    {
        var packet = this.socket.RetriveMessage()

        while ( packet != null )
        {
            
            var payload = packet.payload
            var payloadObjects = Object.keys( payload )

            for ( var i = 0; i < payloadObjects.length; i++ )
            {
                var serverObjName = payloadObjects[i]
                try{
                    this.serverObjects[ serverObjName ].ApplyData( payload[serverObjName] )
                }catch(e){
                    console.error(`Server object ${serverObjName} does not exist :(` + e)
                    console.error(this.serverObjects)
                }
            }

            packet = this.socket.RetriveMessage()

        }
    }

    Tick(){}

    /** Collects data from all server objects */
    CollectFrameData()
    {
        
        var serverObjNames = Object.keys( this.serverObjects )

        for ( var i = 0; i < serverObjNames.length; i++ )
        {

            var data = this.serverObjects[ serverObjNames[i] ].CollectData()

            if ( data != null && data.length > 0 )
            {
                this.currentFramePacket.SetPayload( serverObjNames[i], data )
                console.log("data")
            }

        }

        // send the current frame data
        this.lastFramePacket = this.currentFramePacket
        this.currentFramePacket = Packet.SendPacket(0)

        if ( this.lastFramePacket != null && Object.keys(this.lastFramePacket.payload).length > 0 )
        {
            console.log(this.lastFramePacket.payload  )
            this.socket.SendMessage( this.lastFramePacket )
        }

    }

    Render(){}

}

var m = new Main(60, "game_window", "console_win", "console_input", "console_button");

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