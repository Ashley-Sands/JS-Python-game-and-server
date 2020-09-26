import { Time   } from "./core/managers/time.js";
import { Socket } from "./core/managers/socket.js";
import { Inputs } from "./core/managers/Inputs.js";
import { Packet } from "./core/packets/Packet.js";
import { ObjecetManager } from "./core/managers/objectManager.js";
import { GameConsole } from "./core/managers/gameConsole.js";
import { Viewport } from "./core/managers/viewport.js"
import { Camera } from "./core/objects/camera.js";

import { TEST_ServerGameObject } from "./core/objects/TEST_GameObject.js"
import { Imports } from './imports.js'

class Main
{
    constructor( canvasId, consoleId, consoleInputId, consoleButtonId )
    {
        document.getElementById("tick").onclick = this._Main.bind(this)

        /* Data */
        this.currentFramePacket = Packet.SendPacket(0)   // the next frame to be sent
        this.lastFramePacket = null                      // the frame being sent (or just sent)

        /* Managers */
        this.socket         = new Socket(true, "127.0.0.1", 9091)

        this.time           = new Time()
        this.inputs         = new Inputs()

        this.console        = new GameConsole( consoleId, consoleInputId, consoleButtonId, "console_user_input")
        this.objectManager  = new ObjecetManager( this.AddGameObject.bind(this), this.RemoveServerObject.bind(this) )
        this.mainCamera     = new Camera("Main-Camera")
        this.viewport       = new Viewport( document.getElementById( canvasId ) )

        /* Objects */
        this.objectInstances  = {}    /* All Game Objects. Key: instance id, Value: object */
        this.serverObjects    = {}    /* All server objects/Managers. Key: server name, Value: object*/

        /** A list of server objects for data to be applied in order. 
         *  Data is applied to theses objects first.
         *  While any unlised objects are applied in the order that the data is received.
         */
        this.objectApplyOrder = [ this.objectManager.serverId ]   

        /* Set up default server objects */
        this.serverObjects[ this.objectManager.serverId ]   = this.objectManager
        this.serverObjects[ this.inputs.serverId ]          = this.inputs
        this.serverObjects[ this.console.serverId ]         = this.console
        
        this.console.AddMessage("Initialized successfully!", "SYSTEM")

        this.socket.connect();

        this.TEST_go = new TEST_ServerGameObject("test_serverID", "abc123")
        this.serverObjects[ this.TEST_go.serverId ] = this.TEST_go

    }

    async Start( fps )
    {

        await Imports.Load()

        this.viewport.SetActiveCamera( this.mainCamera )
        this.time.SetFPS( fps )

        this._Main()
        //setTimeout( this._Main.bind(this), 1000 / fps ) 

    }

    AddGameObject( objectId, serverId, object )
    {
        this.objectInstances[ objectId ] = object;
        this.serverObjects[ serverId ]   = object;
        console.log("Adding object o", objectId, "s", serverId, " @@ ", object)
    }

    RemoveServerObject( serverId )
    {
        //Todo: So aparently it doent care if it exist or not when deleting
        console.log("REMOVE SCERVER")
        var obj_id = null;
        try{
            obj_id = this.serverObjects[serverId].objectId;
            delete this.serverObjects[ serverId ];
        }catch(e){
            console.log("Unable to remove server object.")
            return;
        }

        try{
            console.log("##PRE##", obj_id, this.objectInstances )
            delete this.objectInstances[ obj_id ]
            console.log("##GONE##", obj_id, this.objectInstances )
        }catch(e){
            console.log("Nop", e)
        }

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
        // I dont think its going to end up like this.
        // but for now.
        this.time.PreTick() 
        this.viewport.ClearCameraRenderer()

        this.ApplyFrameData()
        this.Tick()
        this.CollectFrameData()
        this.viewport.Draw()

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
            // console.log(payload)
            for ( var objName in this.objectApplyOrder )
            {
                var serverObjName = this.objectApplyOrder[objName]

                if ( payload[ serverObjName ] )
                {
                    this.ApplyData( serverObjName, payload[ serverObjName ] )
                    delete payload[ serverObjName ]   // TODO: find out if this is quicker then checking if the key exist in next for loop.
                }

            }

            for ( var serverObjName in payload )
            {
                this.ApplyData( serverObjName, payload[ serverObjName ] )
            }

            packet = this.socket.RetriveMessage()

        }
    }

    ApplyData( serverObjName, data )
    {

        try{
            this.serverObjects[ serverObjName ].ApplyData( data )
        }catch(e){
            console.error(`Server object ${serverObjName} does not exist :(` + e)
            console.log( this.serverObjects )
        }
    }

    Tick()
    {

        this.time.Tick()

        for ( var objName in this.objectInstances )
        {
            this.objectInstances[ objName ].Tick( this.time.delta )
            this.mainCamera.AddRenderObject( this.objectInstances[ objName ] ) 
        }

        document.getElementById("DEBUG0").innerHTML = `FPS: ${this.time.FPS} | RAW FPS: ${this.time.rawFPS}` 
        document.getElementById("DEBUG1").innerHTML = `FPS Min ${this.time.minFPS} | Max ${this.time.maxFPS} ${this.time.timeTillNextUpdate}` 
    
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
            }

        }

        // send the current frame data
        this.lastFramePacket = this.currentFramePacket
        this.currentFramePacket = Packet.SendPacket(0)

        if ( this.lastFramePacket != null && Object.keys(this.lastFramePacket.payload).length > 0 )
        {
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