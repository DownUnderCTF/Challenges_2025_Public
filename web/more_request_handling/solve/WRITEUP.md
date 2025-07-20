# Request Handling

The goal of the exploit is to get arbitrary JavaScript eval. The way this is achieved is through calling the JavaScript `Function()` constructor, which creates a function with the specified body (interpreting the string as JavaScript). Calling the function will execute the string.
Normally, Handlebars templating prevents you from accessing hidden internal methods of objects, such as the function's `constructor` parameter. However, by carefully using some functions provided through the `req` supplied variable, we can craft a payload.

Firstly, we need a function that can access an attribute from a Javascript object. This will allow us to get a reference to a function constructor without Handlebars noticing. The function we will use for this is `req.socket.server._events.request.request.app.set`.

The function looks like this:

```js
function set(setting, val) {
  if (arguments.length === 1) {
    // app.get(setting)
    return this.settings[setting];
  }

  debug('set "%s" to %o', setting, val);

  // set value
  this.settings[setting] = val;

  // Some other stuff that isn't really important
  // ...
}
```

So, if we use the function with one argument, it acts as a get. However, Handlebars actually adds an extra argument to all function calls by default, which we can't control. To fix this, we will use another function that calls a function with only one argument:

`req.socket.server._events.request.constructor.listenerCount`
```js
function(emitter, type) {
  if (typeof emitter.listenerCount === 'function') {
    return emitter.listenerCount(type);
  }
  // Some other stuff that isn't really important
  // ...
}
```

If the first arguement's `listenerCount` attribute is a function, we call it with the second argument.

So, our exploit looks like this:

1. Find an object we can use that has a `settings` parameter so we can use `app.set` on it. (An object that works is `req.socket.server._events.request.request.app.locals`)
2. Set the `listenerCount` attribute to `app.set`, so we can call `app.set` with a single argument.
3. Use `listenerCount` to call `app.set` with a single argument, and use that to get a reference to the `Function` constructor.
4. Put the `Function` constructor inside `listenerCount` again, so we can...
5. Call the `Function` constructor with a single argument, which is the code we want to eval.
6. Call the resulting function.

Refer to [solve.py](./solve.py) for the solution script.
