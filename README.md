# Bulding an HTTP Server from Scratch in Python

Following along with boot.dev's & Primeagen's course but in Python:
- <p><a href="https://www.boot.dev/courses/learn-http-protocol-golang" target="_blank">🔗 From TCP to HTTP</a></p>
- <a href="https://youtu.be/FknTw9bJsXM?si=SwGlCVEvCBdqHfvc" target="_blank">🔗 YouTube Video</a>


Why does HTTP/1.1 uses TCP as transport layer protocol?
TCP is reliable, in-order packets

User Datagram Protocol (UDP) is often compared to TCP, as they are both transport layer protocols. Here are the high-level differences between the two:

|                | TCP | UDP |
| -------------- | --- | --- |
| Connection     | Yes | No  |
| Handshake      | Yes | No  |
| In Order       | Yes | No  |
| Blazingly Fast | No  | Yes |

TCP establishes a connection between sender and receiver with a handshake, and ensures that all the data is sent in order. UDP yeets the data to the receiver and hopes they can make sense of it.
