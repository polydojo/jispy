# Jispy

#### A JavaScript Interpreter In Python

Jispy is an interpreter for a strict subset of JavaScript, fondly called [LittleJ (LJ)](https://github.com/sumukhbarve/jispy/blob/master/LittleJ.md). It employs recursive descent for parsing and is very easily extendable.

#### Built for embedding JavaScript

Jispy's original vision was to seamlessly allow embedding JavaScript programs in Python projects. By default, it doesn't expose the host's file system or any other sensitive element. Some checks on infinite looping and infinite recursion are provided to tackle possibly malicious code.

See [LICENSE.md](https://github.com/sumukhbarve/jispy/blob/master/LICENSE.md) and [DEDICATION.md](https://github.com/sumukhbarve/jispy/blob/master/DEDICATION.md) for project license and dedication respectively.

#### Installation
Simply include **jispy.py** in your project directory. For convenience, you may wish to also include stdlib.l.js, which provides multiple utilities and manipulators.

**Jispy comes armed with a console and an API.** While the API provides far greater control, the console is great for getting started.


### The `console()`

You could start the console in two ways:

1) Run `jispy.py` in a terminal:
```bash
 $ python jispy.py
```
2) From Python's interactive interpreter:
```py
 >>> import jispy
 >>> jispy.console()
```
In either case, you'll unleash a LittleJ REPL (Read-Evaluate-Print Loop).

```js
LJ> "Hello World!";
"Hello World!"
LJ> var obj = {i: 'am', an: 'object'}, arr = ['i', 'am', 'an', 'array'];
LJ> obj.i === arr[1];
true
LJ> type(obj) === type(arr);
false
LJ> "Because type() of an array is " + type(arr);
"Because type() of an array is array"
LJ> // A function to compute factorial:
LJ> var f = function (n) { if (n <= 1) { return 1; } return n * f(n-1); };
LJ> f(6);
720
LJ> // Functions are first class!!
LJ> var foo = function () { return foo; };
LJ> foo === foo() && foo === foo()();
true
LJ> // Hit Crtl-D to exit
LJ> 
```
To enter multiple lines of code, end lines with tabs.  
Here's an example with `for`:
```js
LJ> var obj = {a: 'apple', b: 'ball', c: 'cat', d: 'dog'}, // tab..       
...     i = null, keyz = keys(obj);
LJ> for (i = 0; i < len(obj); i += 1) {                    // tab.. 
...     keyz[i] + ' for ' + obj[keyz[i]];                  // tab..       
... }
"a for apple"
"c for cat"
"b for ball"
"d for dog"
LJ> 
```

The above example uses the inbuilt `len()` and `keys()` functions. These, along with other inbuilts have been described in [LittleJ's specification](https://github.com/sumukhbarve/jispy/blob/master/LittleJ.md).

### The API

Consider the following LittleJ program for checking if a number is prime:
```js
var isPrime = function (n) {
        var countF = 0, i = null; // countF counts the number of factors
        for (i = 1; i <= n; i += 1) { if (n % i === 0) { countF += 1; } }
        return countF === 2;
    };
print(isPrime(7)); // true
print(isPrime(8)); // false
```

If the above program has been stored as a Python-string in the variable `lj_isPrime`, the following python code would execute it.
```py
 # ... set lj_isPrime ...
from jispy import Runtime
rt = Runtime()
rt.runX(lj_isPrime);
```

#### `Runtime`s

A `Runtime` provides a wrapper around a single global environment or scope. It allows you to run multiple programs in the same environment; at the same time allowing you to run a programs in foreign environments.

`Runtime`'s constructor optionally accepts three arguments (in order):

+ `maxLoopTime`: The maximum time in seconds for which a loop may run.
+ `maxDepth`: The maximum allowable depth of nested environments (scopes).
+ `writer`: `write` method of a file (opened for writing). It defaults to `sys.stdout.write`.

`maxLoopTime` and `maxDepth` both default to `None`. Unless set to a positive value, there shall be no checks on infinite looping and/or infinite recursion. If `writer` is set to `None`, the inbuilt `print()` shall not be made available.

Here's an example involving `maxLoopTime` and `maxDepth`:
```py
 >>> from jispy import Runtime
 >>> prog1 = """var i = 1; while (true) { i += 0; }"""
 >>> prog2 = """var foo = function () { return foo(); }; foo();"""
 >>> rt = Runtime(maxLoopTime=13, maxDepth=100);
 >>> rt.runX(prog1);
 RuntimeError: looping for to long
 >>> rt.runX(prog2);
 RuntimeError: maximum call depth exceeded
 >>> 
```

#### Running programs in the right `Runtime`:

An instance of `Runtime` (say `rt`) provides 3 ways in which you may run a program. There's a method corresponding to each:

- `rt.runG()` runs programs in `rt`'s global environment.
- `rt.runC()` runs programs in a first-level child of `rt`'s global environment.
- `rt.runX()` runs programs in a completely different (foreign) environment.

***In LittleJ, once a variable is defined, it may not be redefined in the same environment.*** Thus, the method used to run a program is significant.

Additionally, there's an `rt.run()` method, which accepts the environment in which a program should be run. Each of the above listed method internally calls `rt.run()`. However, calling `rt.run()` explicitly is not advised.

####  Input to `rt.runG()`, `rt.runC()` & `rt.runX()`:

Each of these methods accept at least 1 and at most 2 inputs (in order):

- `prog`: A LittleJ program. It must be supplied.
- `console`: A boolean. (Optional, defaults to `False`.)

`prog` may be any one of:

- A Python string in which a LittleJ program is stored. (Like `lj_isPrime` above.)
- The **name** of an LittleJ program file. LittleJ program files have the `.l.js` extension. Any string ending in `.l.js` is treated as a file name.
- A parse tree generated by Jispy's (`lex()` and) `yacc()`. This option is explored in later sections.

**Consider:**

```py
 >>> import jispy
 >>> rt = jispy.Runtime();
 >>> mappy = """
 ... var map = function (arr, func) {
 ...     var ans = [], i = null;
 ...     for (i = 0; i < len(arr); i += 1) {
 ...             append(ans, func(arr[i]));
 ...     }
 ...     return ans;
 ... };"""
 >>> rt.runG(mappy);
 >>> rt.runG('print(map([1, 2, 3], function (x) { return x*x; }));');
 [1, 4, 9]
 >>> rt.runC('print(map([1, 2, 3], function (x) { return x/2; }));');
 [0.5, 1, 1.5]
 >>> rt.runX('print(map([1, 2, 3], function (x) { return x+2; }));');
 ReferenceError: map is not defined
 >>> 
```

In the above example, since `mappy` is run in `rt`'s global environment, the variable `map` it is available to not only the global environment but also all child environments. However, it is not available in any foreign environment.

#### Including `stdlib.l.js`:

`stdlib.l.js` contains many useful string, array and object related utilities. To use them in your programs, run `stdlib.l.js` using `runG()`

#### More about `console()`

Each call to Jispy's `console()` uses a **single** `Runtime`. Each input line (or lines) is executed as an independent program in the global environment (using the `runG()` method). Thus, each line has access to variables defined in earlier an earlier line.

##### Input to `console()`

The console accepts three optional arguments (in order):

- `rt`: The `Runtime` in which each line (or lines) should be run. Defaults to `None`, in which case a fresh `Runtime` is created.
- `semify`: A boolean, defaults to `False`. If `True` (or truthy), the console *tries* to add semicolons to the end of lines as required.
- `prompt`: The input prompt. Defaults to `"LittleJ> "`

Originally, the `console()` was not a REPL. It now is. (But the name has stuck.)

#### `console()` and `stdlib.l.js`:

```py
 >>> import jispy
 >>> rt = jispy.Runtime(13, 100);
 >>> rt.runG('stdlib.l.js');
 >>> jispy.console(rt);
```
`stdlib.l.js` includes `array.map()` and `array.filter()`. As the library was run in the global environment, we may freely use those functions in our LittleJ programs:
```js
 LJ> var a = [5, 8, 3, 4, 6, 7, 1];
 LJ> array.map(array.filter(a, function (x) { return x % 2 === 0; }),    
 ...             function (x) { return x * x * x; });
 [512, 64, 216]
 LJ> // [8^3, 4^3, 6^3]
 LJ> 
```

### Adding Natives

Functions such as `print()` may be added via `Runtime`'s `addNatives` method.
It accepts a single dictionary as input. The key-value pairs are added to the global environment.

For example, let's add a native version of the `factorial` function and set native `inbuilt_num` to `7.0`:
```python
 >>> from jispy import Runtime
 >>> factorial = lambda n: 1.0 if n <= 1.0 else n * factorial(n-1)
 >>> rt = Runtime(maxLoopTime = 13, maxDepth = 100)
 >>> rt.addNatives({'factorial' : factorial, 'inbuilt_num' : 7.0})
 >>> demoProgo = 'print(factorial(inbuilt_num));'
 >>> rt.runC(demoProgo)
 5040
 >>> 
```

Please note that the LittleJ program may reassign all natives; and a native variable may be initialized (as a fresh variable) in a new environment.

#### Adding a native `input()` function:

```py
 >>> import jispy as j
 >>> rt = j.Runtime();
 >>> rt.addNatives({'input': lambda prompt: raw_input(prompt)});
 >>> j.console(rt); # use input() on Python 3+
```
```js
 LJ> var name = input('Please enter your name: ');
 Please enter your name: Awesome Person
 LJ> print('Dear ' + name + ', THANK YOU FOR READING THIS FAR!');
 Dear Awesome Person, THANK YOU FOR READING THIS FAR!
 LJ> 
```

---------------------------------------------------------------------

If you find Jispy interesting, **PLEASE FEEL FREE TO CONTRIBUTE.**

If you use Jispy in any of your projects, **PLEASE LET ME KNOW.**

---------------------------------------------------------------------

Above documentation is incomplete. More shall soon be added.
