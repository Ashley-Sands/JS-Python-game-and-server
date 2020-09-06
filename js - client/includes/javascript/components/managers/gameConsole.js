import { ServerObject } from "../objects/baseObject.js"

export class GameConsole extends ServerObject
{
    constructor( windowId, inputId, buttonId, usernameId )
    {
        super("console", "console")

        this.window = document.getElementById( windowId )
        this.input  = document.getElementById( inputId )
        this.userIn = document.getElementById( usernameId )    // temp
        this.button = document.getElementById( buttonId )

        this.button.onclick = this.SendMessage.bind(this)
        this.bottomScrollPosition = 0

        this.sendMessageQueue = []

    }

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

            this.window.innerHTML += `<br />${frameData[i]["timestamp"]} | ${frameData[i]["user"]} | ${frameData[i]["msg"]}`
            this.bottomScrollPosition += 20  
            this.window.scrollTop = this.bottomScrollPosition
        }

    }

    CollectData( sinceTime=0.0 )
    {
        var data = this.sendMessageQueue
        this.sendMessageQueue = []

        return data
    }

}