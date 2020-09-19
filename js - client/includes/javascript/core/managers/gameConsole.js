import { ServerBaseObject } from "../objects/baseObject.js"

export class GameConsole extends ServerBaseObject
{

    __inst = null

    MESSAGE_TYPE = null

    constructor( windowId, inputId, buttonId, usernameId )
    {
        if (GameConsole.inst != null)
            return GameConsole.__inst

        super("console", "console")

        GameConsole.MESSAGE_TYPE = { MSG: "", WARN: "WARNING:", ERROR: "ERROR:", FATAL: "FATAL:" }

        this.window = document.getElementById( windowId )
        this.input  = document.getElementById( inputId )
        this.userIn = document.getElementById( usernameId )    // temp
        this.button = document.getElementById( buttonId )

        this.button.onclick = this.SendMessage.bind(this)
        this.bottomScrollPosition = 0

        this.sendMessageQueue = []
        this._hasMessage = false

        GameConsole.__inst = this

    }

    static get instance()
    {
        if ( GameConsole.__inst != null )
        {
            return GameConsole.__inst
        }
        else
        {
            throw "Unable to get GameConsle instance. Does not exist." 
        }
    }

    /** Adds a message to the console window */
    AddMessage( message, user, timestamp=null, type=GameConsole.MESSAGE_TYPE.MSG )
    {
        var msg = ""

        if ( this._hasMessage )
            msg = "<br />" 

        if ( timestamp == null )
            timestamp = new Date().toLocaleString()

        message = message.replace(/\\n/g, "<br />")   // convert new lines to html
            
        msg += `${timestamp} | ${user} | ${type} ${message}`
        
        this.window.innerHTML += msg
        this.bottomScrollPosition += 20  
        this.window.scrollTop = this.bottomScrollPosition

        this._hasMessage = true

    }

    /** Send a console message to the server. */
    SendMessage( e )
    {
        var message = this.input.value 
        if ( message.trim() != "")
        {
            var message_object = {
                user: this.userIn.value,
                msg: message,
                timestamp: "00:00:00.000"
            }


            this.input.value = ""
            //if ( !local )
            this.sendMessageQueue.push(message_object)

        }

    }

    ApplyData( frameData )
    {

        for ( var i = 0; i < frameData.length; i++ )
        {
            this.AddMessage( message, frameData[i]["user"], frameData[i]["timestamp"] )
        }

    }

    CollectData( sinceTime=0.0 )
    {
        var data = this.sendMessageQueue
        this.sendMessageQueue = []

        return data
    }

}