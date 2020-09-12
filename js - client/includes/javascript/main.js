import { Time   } from "./core/managers/time.js";
import { Socket } from "./core/managers/socket.js";
import { Inputs } from "./core/managers/Inputs.js";
import { Packet } from "./core/packets/Packet.js";
import { GameConsole } from "./core/managers/gameConsole.js";
import { Viewport } from "./core/managers/viewport.js"
import { Camera } from "./core/objects/camera.js";

import { TEST_GameObject } from "./core/objects/TEST_GameObject.js"
import { Imports } from './imports.js'

class Main
{
    constructor( canvasId, consoleId, consoleInputId, consoleButtonId )
    {
        document.getElementById("tick").onclick = this._Main.bind(this)

        /* Data */
        var currentFramePacket = Packet.SendPacket(0)   // the next frame to be sent
        var lastFramePacket = null                      // the frame being sent (or just sent)

        /* Managers */
        this.socket  = new Socket(true, "127.0.0.1", 9091)

        this.time       = new Time()
        this.inputs     = new Inputs()

        this.console    = new GameConsole( consoleId, consoleInputId, consoleButtonId, "console_user_input")
        this.mainCamera = new Camera("Main-Camera")
        this.viewport   = new Viewport( document.getElementById( canvasId ) )

        /* Objects */
        this.objectInstances = {}    /* All Objects. Key: instance id, Value: object */
        this.serverObjects   = {}    /* All server objects. Key: server name, Value: object*/

        /* Set up default server objects */
        this.serverObjects[ this.console.serverId ] = this.console
    
        this.socket.connect();

        this.TEST_go = new TEST_GameObject("204tgf")
    }

    async Start( fps )
    {

        await Imports.Load()

        this.viewport.SetActiveCamera( this.mainCamera )
        this.time.SetFPS( fps )

        //setInterval(this._Main.bind(this), 1000 / fps )
        this._Main()
        //setTimeout( this._Main.bind(this), 1000 / fps ) 

    }

    /** 
     * Main Loop
     * 1 - Apply Frame Data
     * 2 - Tick Frame
     * 3 - Collect Frame Data
     * 4 - Render
     */
    _Main(){
/*
        var nextFrame = new Promise( (resolve, reject) => {
            setTimeout( () => resolve(1), this.time.timeTillNextUpdate + (1000 / 60))
        } )
        nextFrame.then( this._Main.bind(this) )
*/
        var n = Date.now()
        // I dont think its going to end up like this.
        // but for now.
        this.time.PreTick() 
        this.viewport.ClearCameraRenderer()

        this.ApplyFrameData()
        this.Tick()
        this.CollectFrameData()
        this.viewport.Draw()

        var n1 = Date.now()

        // Using SetTimeout gives a more constant frameRate over setInterval
        // at lower frame rates < 150 anythink more and it strugles, in which 
        // setInterval is better for upto 250fps
        setTimeout( this._Main.bind(this), this.time.timeTillNextUpdate ) 

        
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

    Tick()
    {
        this.time.Tick()
        document.getElementById("DEBUG0").innerHTML = `FPS: ${this.time.FPS} | RAW FPS: ${this.time.rawFPS}` 
        document.getElementById("DEBUG1").innerHTML = `FPS Min ${this.time.minFPS} | Max ${this.time.maxFPS} ${this.time.timeTillNextUpdate}` 
    
        this.TEST_go.Tick( this.time.delta )
        this.mainCamera.AddRenderObject( this.TEST_go )

    }

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

}

var m = new Main("game_window", "console_win", "console_input", "console_button");
m.Start(30)
/**
 * Object Instances.
 * { "object_id": baseObject }
 * 
 * Server objects.
 * { "server_id": serverObject }  
 *
 */