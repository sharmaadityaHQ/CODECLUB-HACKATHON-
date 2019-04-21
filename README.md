Description

A simple browser chat app utilizing WebSockets made with Django and JavaScript.

A standard Django application handles http requests using a request-response lifecycle. A request is sent from the user’s browser, Django calls the relevant view which then returns a response to the user. The request-response lifecycle has certain limitations though : it’s not great for realtime applications which usually require communicating with the backend server frequently. New standards such as websockets and HTTP2 address some of these shortcomings. WebSockets is a recent communications protocol which provides full-duplex communication channels over a single TCP connection and is well suited for realtime applications.
