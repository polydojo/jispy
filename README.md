# Jispy
Jispy is a recursive descent parser for a strict subset of Javascript.  
It is written purely in Python; and is distributed as a single file.

**Note:** This document is work in progress. New material shall soon be added.

## Inspiration

Jispy has two primary influences:

+ [**Lispy**](http://norvig.com/lispy.html) - (A (Lisp) Interpreter (in Python)) by [**Peter Norvig**](http://norvig.com/).
+ [**Javascript: The Good Pargs**](http://www.amazon.com/exec/obidos/ASIN/0596517742/wrrrldwideweb), by [**Douglas Crockfork**](http://www.crockford.com/).

This project is respectfully dedicated to them. (Hope they don't mind.)

## LittleJ

LittleJ is the subset of JavaScript which Jispy interprets. It is a strict subset of JavaScript; strict in two senses:

+ LittleJ is a proper syntactic and semantic subset of JavaScript.
+ LittleJ enforces far stricter rules than JavaScript. Its less forgiving.

The following is a **brief** overview of LittleJ. Philosophy is not discussed herein.

+ There are **no implied globals**.
    - All variables must be defined before use.
+ There may be **at most one var statement per scope.**
    - If present, `var` must be the first token within that scope.
+ **Functions are first class citizens**.
    - However, function declarations are excluded.
    - All functions must be defined via function expressions.
    - **Closures are fully supported.**
+ `==`, `!=`, and **bitwise operators** are **NOT** included.
    - Use `===` and `!==` instead.
    - Logical operators `&&` and `||` are supported.
+ No `undefined` and no `arguments`.
    - All variables must be initialized with a value.
    - Too many or too few arguments may not be passed to a function.
    - **All functions must have a return value.**
+ `NaN`, `Infinity` and `null` are excluded.
    - Multiplying a number by a string results in a `TypeError`.
    - `ZeroDivisionError` is accordingly introduced.
+ **Much stricter type checking.**
    - One can't add numbers to strings (without explicitly converting either).
    - Removing `NaN` makes the language far less permissive.
+ A more meaningful `type()` function replaces the `typeof` operator.
    - `type(x)` may be one of: 
        - `"boolean"`, `"number"`, `"string"`, `"array"`, `"object"`.
    - It may **not** be `"undefined"` or `"null"`. (Those are excluded.)
+ No `this` and no `new`. There are no JS-like constructors.
    - However, **objects and object literals are included.**
    - Similary, **arrays and array literals are included.**
+ There's no `prototype` and no `in`.
    - However, prototypal inheritance ***is*** possible.
    - Objects don't inherit properties form the prototype chain (as there isn't one.)
    - Thus, `hasOwnProperty` is not required (and is excluded).
+ The `switch` statement is excluded.
+ `if`, the `else`-`if` ladder, `while`, the conventional-`for` and `break` statements are supported.

The above covers most of LittleJ.  
However, there are a few other caveats which we shall get to later.

## A LittleJ Program

Consider the following LittleJ program for computing factorial:
```javascript
var n = 6, factorial = function (n) {
    if (n <= 1) { return 1; }
    return n * factorial(n - 1);
};
writeln(factorial(n)); // prints 720
// writeln() is an inbuilt function (in the standard version) of Jispy.
// It may be disable by the end user or re-assigned via this Python API.
```

Four functions come inbuilt (in the standard configuration) with Jispy:

+ `write()`, `writeln()`, `type()`, `keys()`, `str()`, `len()`.  
Each accepts a single argument. The last two are like their python-versions.  
`keys()` is equivalent to `Object.keys()` in JS or `dict.keys()` in Python.

## Using Jispy:

Jispy has an API and a console.  
The console is fun, but the API lets you do much more.

### The API

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

if `write` is set to `None`, inbuilts `write` and `writeln` shall not be make available.

### Adding Natives

Functions such as `writeln` may be added via `Runtime`'s `addNatives` method.
It accepts a single dictionary as input. The key-value pairs are added to the global environment.

For example, let's add a native version of the `factorial` function and set native `inbuilt_num` to `7.0` :
```python
from jispy import Runtime
inbuilt_num = 7.0
factorial = lambda n: 1.0 if n <= 1.0 else n * factorial(n-1)
rt = Runtime(maxLoopTime = 13, maxDepth = 100)
rt.addNatives({'factorial' : factorial, 'inbuilt_num' : 7.0})
demoProgo = 'writeln(factorial(inbuilt_num));'
rt.run(demoProgo) # prints 5040
```

Please note that the LittleJ program may redefine all natives. And a native variable may be initialized (as a fresh variable) in any non-global environment.

### The Python `console()`
```python
 >>> from jispy import console
 >>> console()
 jispy> var h = 'Hello World', arr = ['I', 'am', 'an', 'array'], obj = {}; 
 jispy> writeln(h);
 Hello World
 jispy> writeln(type(arr) + ' is not the same as ' + type(obj));
 array is not the same as object
 jispy> writeln(1 + 2 + 3 === 3 + 2 + 1);
 true
 jispy> writeln(1 + 2 + 3 != 1 + 1);
 SyntaxError: unexpected token !=
 jispy> writeln('bye!!');
 bye!!
```

Each call to `console()` uses a single instance of `Runtime`. Each line of input is executed as an independent program, in a **common** `Runtime`. This allows us to define the variable `h` and print it using `writeln(h)` on separate lines of input.

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

More will soon be added. As already noted, THIS IS WORK IN PROGRESS.
There are more caveats, but error messages should be helpful enough.
