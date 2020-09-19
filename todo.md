# TODO.md

## Server

[x] Add own protocol to server
	+ BaseProtocolClass

[ ] unity socket

[x] finish handler send message, by processing it in the socket handler
	- finish both send and receive json data bits.
[ ] make the queues non static 
[ ] time module
[ ] console module (chat ect..)
[ ] input handler 

[x] Designe note. Send Data queue.
	- Need a way to inculde send/ignore sockets
	- Do NOT want to convert to JSON on the game thread
		- Which would mean that we cant put the data into a send message object as it converts on set as a means of caching
	==
	Added a raw data class
	
	
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
	```Fix inputs geting overwiten
	
[ ] Change send data raw payloads, to handle message to multiple client groups.
	- There need to be a method to handle message to indervidule users, or client groups
	  Im thinking that messages should be compiled into users group from a single raw_payload.
	  This way we still only need to send users a single message per update.
	  To achive this rather than adding data to a single dict to be converted into json, the 
	  SendDataRawPayload will have a message to add data and it target target client('s) where 
	  the data will be sorted. Get it becom a generator and yield the target clients and sendMessage object.
	  
	
## JS Client

[ ] 
[ ] Test Game Modle
[ ] Synce Clock Thread Test

[ ] Move main client into a WebWorker and pass the render data back to the main thread for rendering.
	- Rendering is slow so it would be better if its done on its own thread, freeing the client thread
	  for proccessing packets ect.
	- Also if i remember correctly, DOM is only available on the main thread
	- (not sure if this will work because of DOM)
	
[x] - imporve connection handerling.
[x] - Add support to print directly to GameConsole.	

## Both (JS/Server)

[ ] Finish this connection bits.
	- client notfiy server that handshake is OK
	- Server/Client agreement
	
[ ] change Frame Timestamp in protocol to either 48bit or 64bit Or
	A better idear would be to normilize the time to 0 when the game starts.
	32bit = 4,294,967,295ms which is ~49days. So i think that will do.

[ ] finish basic inputs

### Unity (inital)
[ ] Inital Socket
[ ] Message Queue.
