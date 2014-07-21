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
        - `"boolean"`, `"number"`, `"string"`, `"array"`, `"object"`, `"function"`.
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

