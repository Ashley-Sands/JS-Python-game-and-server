# TODO.md

## Server

[x] Add own protocol to server
	+ BaseProtocolClass

[ ] unity socket

[ ] finish handler send message, by processing it in the socket handler
	- finish both send and receive json data bits.
[ ] make the queues non static 
[ ] time module
[ ] console module (chat ect..)

[ ] Note
	Components should have there own get_server_data fuct and maybe set?
	also server vars shoud be in a dict and set/get via properties this will
	make getting the data easier. 	
	Could also add some logic to only get valuse that have changed.
	Maybe 
	```
		//...
		self.var_updated = []
		self.server_var = {x: 0, y: 0}
		
		//...
		
		@property
		def x():
			return self.server_var["x"]
			
		@property.set
		def x(val)
			self.var_updated.append("x")
			self.server_var["x"] = val
			
		@property
		def y():
			return self.server_var["y"]
			
		@property.set
		def y(val)
			self.var_updated.append("y")
			self.server_var["y"] = val
			
		def get_server_data():
			data = {}
			for update in self.var_updated:
				data[update] = self.server_var[update]
			
			return data
	```
	
## JS Client

[ ] Test Game Modle
[ ] Synce Clock Thread Test

[ ] Move main client into a WebWorker and pass the render data back to the main thread for rendering.
	- Rendering is slow so it would be better if its done on its own thread, freeing the client thread
	  for proccessing packets ect.
	- Also if i remember correctly, DOM is only available on the main thread


## Both (JS/Server)

[ ] Finish this connection bits.
	- client notfiy server that handshake is OK
	- Server/Client agreement
	


### Unity (inital)
[ ] Inital Socket
[ ] Message Queue.
