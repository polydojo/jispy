# Jispy
Jispy is recursive descent (parser) interpreter for a strict subset of Javascript.  
It is written purely in Python, distributed as a single file and highly extendable.

See [LICENSE.md](https://github.com/sumukhbarve/jispy/blob/master/LICENSE.md) and [DEDICATION.md](https://github.com/sumukhbarve/jispy/blob/master/DEDICATION.md) for project license and dedication.

**Note:** This document and each document linked herein is work in progress.

The subset of JavaScript that Jispy interprets is fondly called [LittleJ](https://github.com/sumukhbarve/jispy/blob/master/LittleJ.md).  
Please at least skim it before reading further.

**Installation:** Simply include jispy.py in your project directory.

Jispy comes armed with a console and an API. While the API provides far greater control, the console is great for getting started.


### The `console()`

Let's jump right in.

```py
 >>> from jispy import console
 >>> console()  # continued...
 jispy> "Hello World!";
 Hello World!
 jispy> var obj = {i: 'am', a: 'object!'}, arr = ['I', 'am', 'an', 'array'];
 jispy> obj.i === arr[1];
 true
 jispy> type(obj) === type(arr);
 false
 jispy> 'Because type() of an array is ' + type(arr);
 Because type() of an array is array
 jispy> var f = function (n) { if (n === 1) { return 1; } return n * f(n-1); };
 jispy> f(6); // Should be 720...
 720
 jispy> var foo = function () { return foo; }; // functions are first class!
 jispy> foo === foo();
 true
 jispy> "Hit Crtl-D to exit."
 SyntaxError: expected ;
 jispy> "Dough.... :P"; // LittleJ is particular about semicolons;
 Dough.... :P
 jispy> "Bye!!";
 Bye!! 
```

Four functions come builtin with (the standard configuration of) Jispy:

+ `write()`, `writeln()`, `type()`, `keys()`, `str()`, `len()`.  
Each accepts a single argument. The last two are like their python-versions.  
`keys()` is equivalent to `Object.keys()` in JS or `dict.keys()` in Python.

To enter multiple lines of code, end each line with a tab.  
Here's an example with `for`:
```python
 >>> jispy.console()
 jispy> var obj = {a: 'apple', b: 'ball', c: 'cat'}, i = 0, k = 0;
 jispy> for (i = 0; i < len(obj); i += 1) {      
 ......     k = keys(obj)[i];    
 ......     writeln(k + ' for ' + obj[k]);       
 ...... }
 a for apple
 c for cat
 b for ball
```

And oh yes! Objects have `len()` in LittleJ.  
`len(obj)` equivalent to `Object.keys(obj).length` in JavaScript.

### The API

Consider the following LittleJ program for computing factorial:
```javascript
var n = 6, factorial = function (n) {
    if (n <= 1) { return 1; }
    return n * factorial(n - 1);
};
writeln(factorial(n)); // prints 720
```

Assuming that the above LittleJ program for computing factorial has been saved as a python-string in the variable `factoProg`, the following python code would execute it.
```python
 # ... define factoProgo ...
from jispy import Runtime
rt = Runtime()
rt.run(factoProgo); # Runtime().run(factoProgo) would have the same effect.
 # 720 will be printed
```

A `Runtime` is a wrapper around a global environment. It allows you to run multiple programs in the same environment. If you don't wish to do so, create a new instance of `Runtime` each time, or simply call `__init__` on the existing one.

`Runtime`'s constructor optionally accepts three arguments (in order):

+ `maxLoopTime`: The maximum time in seconds for which a loop may run.
+ `maxDepth`: The maximum allowable depth of nested environments (scopes).
+ `write`: `write` method of a `file`. It defaults to `sys.stdout.write`.

`maxLoopTime` and `maxDepth` both default to `None`. Unless changed to a positive value, there shall be no checks on infinite-looping and/or infinite-recursion.

if `write` is set to `None`, inbuilts `write` and `writeln` shall not be made available.

#### More about `console()`

Each call to Jispy's `console()` uses a **single** `Runtime`, wherein each input line (or lines) is executed as an independent program. But since the `Runtime` is common, later programs have access to variables defined in earlier programs.


### Adding Natives

Functions such as `writeln` may be added via `Runtime`'s `addNatives` method.
It accepts a single dictionary as input. The key-value pairs are added to the global environment.

For example, let's add a native version of the `factorial` function and set native `inbuilt_num` to `7.0` :
```python
from jispy import Runtime
factorial = lambda n: 1.0 if n <= 1.0 else n * factorial(n-1)
rt = Runtime(maxLoopTime = 13, maxDepth = 100)
rt.addNatives({'factorial' : factorial, 'inbuilt_num' : 7.0})
demoProgo = 'writeln(factorial(inbuilt_num));'
rt.run(demoProgo) # prints 5040
```

Please note that the LittleJ program may redefine all natives. And a native variable may be initialized (as a fresh variable) in any non-global environment.

More will soon be added. As already noted, THIS IS WORK IN PROGRESS.
There are more caveats, but error messages should be helpful enough.
