# Note Web Socket Protocol

See see: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers 
for more info 

```
# Packet layout (both inbound and outbound)

         Packet
         Bytes            |1              |2              |3
         Bits:            |1|2|3|4|5|6|7|8|1|2|3|4|5|6|7|8|1|2|3|4|5|6|7|8|
         -----------------|-|-|-|-|-------|-|-------------|---------------|
                          |f|r|r|r| OP    |m| message     |
                          |i|s|s|s| CODE  |a| length      |
                          |n|v|v|v|       |s|             |
                          | |0|1|2|       |k|             |
                          |---------------|---------------|
                          | If msg len == 126 msg len     |
                          |-------------------------------|
                          | If msg len == 127 msg len      ... 8 bytes
                          |-------------------------------|
                          | if mask, mask bytes            ... 4 bytes
                          |-------------------------------|
                          | payload                        ... msg len bytes
                          |-------------------------------|
        
```
```
Byte order BIG
        (0b) masks
byte |1|
fin      0b10000000           (message finished)
rsv1     0b01000000
rsv2     ob00100000
rsv3     ob00010000
opcode   0b00001111

byte |2|
use mask 0b10000000
msg len  0b01111111

if byte |2| msg len < 126:
use byte |2| msg len

if byte |2| msg len == 126
use bytes |3| & |4|           # No mask

if byte |2| msg len == 127:
use bytes |3|4|5|6|7|8|9|10|
mask greatest byte only 0b01111111
(the most significant bit must be 0.)
see: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers
'Decoding Payload Length'

at this point it very important that we know what byte we are at (byteOffset)

if use mask was true (or 1)
bytes ...byteOffset |1|2|3|4|

bytes ...byteOffset |1|n...meg length
are xor-ed with the mask bytes which decode message.
message_byte[n] ^ mask[n % 4]
```

Note.
Server should not respond with the 'use mask' bit set to 1
