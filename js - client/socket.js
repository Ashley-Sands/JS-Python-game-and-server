// TEST web socket

socket = new WebSocket("ws://127.0.0.1:9091/")

chat_win = document.getElementById("chat_win")
chat_input = document.getElementById("chat_input")

console.log( chat_input )

socket.onopen = function( e ){
    console.log("Socket Opened")
}

socket.onclose = function( e ){
    console.log("Socket Closed")
}

socket.onmessage = function( e ){
    console.log( "Server Says: " + e.data )
    chat_win.innerHTML += `<br />${e.data}`
}

socket.onerror = function( e ){
    console.log( "An Error Occored" )
}

send_message = function( ){

    console.log("sending message")
    msg = chat_input.value
    chat_input.value = ""

    socket.send(msg);

}
