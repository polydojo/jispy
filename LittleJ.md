# LittleJ

The subset of JavaScript interpreted by Jispy is fondly called LittleJ (or **LJ**). **It is a strict subset of JavaScript,** strict in two senses:

1. LJ is a *syntactic and semantic subset* of JS.
2. LJ is *far less permissive* than JS.

Thus, every valid LittleJ program is also a valid JavaScript program, but every valid JavaScript program is not a valid LittleJ program.

**Note:** This document and each document linked herein is work in progress. 

LJ *borrows heavily* from [Douglas Crockford's JS Conventions](http://javascript.crockford.com/code.html). In a few cases, it is stricter than [JSLint](http://jslint.com/).

## Features & Rules

### 1. No `undefined`

Most programming languages have some notion of emptiness. It may be called `void`, `None`, `null`, `nil` etc. JavaScript calls it `undefined` and also has `null`. [This can be very confusing.](http://javascriptweblog.wordpress.com/2010/08/16/understanding-undefined-and-preventing-referenceerrors/).

JavaScript's **overindulgence** in `undefined` *masks otherwise easily detectable errors*. Choosing to drop it makes the language far more robust and dependable. `undefined` has beenis excluded from LittleJ; it is meaningless and may not be used. This has the following implications:

#### 1.1 All variables must be initialized.

In JS, the value of a declared but uninitialized variable is `undefined`. Since there no `undefined` in LJ, variables must have an initial value. Mere declaration is illegal. 

```js
// Thus,
var a, b, c, d, e, f, g; // is ILLEGAL (SyntaxError);
// But,
var a = null, b = null;  // is legal
```

#### 1.2 Every function must return

In JS, functions that don't have an explicit return statement return `undefined`. As LJ lacks `undefined`, all functions must explicitly return something.

```js
// Thus,
sayHi = function (name) { print('Hi ' + name + '!'); }; // is ILLEGAL (TypeError)
// But,
sayHi = function (name) { print('Hi ' + name + '!'); return null;}; // is legal.
```

#### 1.3 No `arguments`

In JS, if you pass too few arguments to a function, the remaining arguments take `undefined`. As there's no `undefined` in LJ, you may not pass too few arguments to any function. As passing too few arguments is illegal, so is passing too many.

```js
// Thus, assuming reduce to be Array.prototype.reduce.call
add = function () { return sum(arguments); }; // is ILLEGAL
// Instead, use:
add = function (args) { return sum(args); };  // (legal)
```
### 2. No Implied Globals

In JavaScript, any variable which wasn't defined with a `var` statement is assumed to belong to the global scope. Such variables are called implied globals and [are very bad](http://yuiblog.com/blog/2006/06/01/global-domination/) and make you code vulnerable.

To remedy this problem, LittleJ requires all variables to be initialized before use, via `var` statements. Further, once initialized, they may not be reinitialized (in the same scope.)

```js
// Thus,
var a = 10; b = 100; // is ILLEGAL. (Assuming b was not defined in an enclosing scope.)
// Similarly,
var a = 10; var a = 100; // is also ILLEGAL.
// But,
var a = 10, b = 100; a = 100; // is perfectly legal.
```

### 3. Clean Scoping

*JavaScript does **NOT** have block scope*. It has ***functional scope***. Initializing a variable just before its point for first use is very BAD advise in JavaScript.

In particular,
> ".. defining variables in blocks can confuse programmers who are experienced with other C family languages. ... " *~ Douglas Crockford*

#### 3.1 `var` statements

To clarify scopes, there may be ***at most one `var` statement per scope.*** If a `var` statement is used in a scope, the first token within that scope must be `var`. This is also applicable to the global scope.

```js
// Thus,
var a = 1, b = 2; var c = 3; // is ILLEGAL
// But,
var a = 1, b = 2, c= 3; // is legal.
```

Because of this rule, even a programmer who is unaware of functional scoping won't go wrong with scoping. Similarly, programmers who work closely with block-scoped languages will be less likely to misread code.

### 4. First Class Functions

Functions are one of the very best parts of JavaScript. LittleJ is proud to include them. The meaning of the "Functions are first class citizens" is:

+ A function may return a function.
+ A function may be passed (as an argument) to a function.
+ A function may close over other functions. (Closures are fully supported.)

#### 4.1 Function expressions only please!

As with most things in JavaScript, there is a bad part associated with function declarations, namely **function hoisting**. It allows us to use functions before we declare them. This unsettles me.

Luckily, function values (created via function expressions) are not hoisted. LittleJ supports function expressions only. Funtion declarations have been dropped.

```js
// Thus,
function add(a, b) { return a + b; } // is ILLEGAL (SyntaxError).
// But,  
add = function (a, b) { return a + b; } // is legal
```

#### 4.2 Immediate invocation:

When a function is to be invoked immediately, wrap the entire invocation in a pair of parenthesis. This not only makes your intention clear, but (in some cases) is required by JavaScript.

```js
//That is, use,
(function (x) { return x * x; }(2));
//instead of,
function (x) { return x * x; }(2);
```

**Note:**
Currently, only anonymous functions are supported. This is not likely to change in the near future. (Anonymous functions may be recursive.)

### 5. No `NaN` and no `Infinity`

Getting rid of `undefined` exposed a huge class of errors that may go unchecked in JS. Getting rid of `NaN` and `Infinity` as well makes the programming extremely robust, reliable and clear.

Like `undefied`, `NaN` and `Infinity` *mask too many errors that may otherwise be easily detected*. We are better off without them, than with them.

#### 5.1 You can't do meaningless stuff!

```js
// That is,
a = 'James Bond' / 700; // is ILLEGAL (TypeError). It is not NaN.
// And
a = 99 / 0; // is also ILLEGAL (ZeroDivisionError).
```

#### 5.2 No `try`-`catch` blocks

Unfortunately, there is no `ZeroDivisionError` in JavaScript. Keeping that in mind, consider the following snippet of code:

```js
var a = null;
try {
    a = 1/0;
    print('This is JS');
} catch (e) {
    print('This is LJ');
}
```

In JavaScript, the output would be `This is JS`. In LittleJ, on account of `ZeroDivisionError` one may expect the output to be `This is LJ`, but wait! The moment any program has a different meaning in JavaScript than in LittleJ, LJ ceases to be semantic subset of JS. This contradicts our premise!

Thus, unfortunately, `try`-`catch` blocks are not included in LittleJ. If you can come up with a way to include them meaningfully, please let me know. I shall be forever grateful. 

### 6. No `this`

In JavaScript, there are four function invocation patterns. The value of `this` is determined by the invocation pattern used. `this` makes JavaScript look like Java. Apart from that, it only rarely does anything useful.

JavaScript's constructors are do a very good job at diverting our attention from its truly prototypal nature. Why do we need to use constructors (or equally classes) when objects are object factories! We don't. No exceptions.

#### 6.1 Builders vs Constructors

As there's no `this`, there cannot be any constructors in LittleJ. Instead, we use builders:
```js
// ... preceeding code ...
buildPoint = function (x, y) {
    var self = {},
        square = function (n) { return n * n; };
    self.getX = function () { return x; };
    self.getY = function () { return y; };
    self.dist = function (pt) {
        return math.sqrt(square(x - pt.x) + square(y - pt.y));
    };
    return self;
};
origin = buildPoint(0, 0);
// ... more code ... 
```

For comparison, here's the JS equivalent of above code:
```js
// ... (possibly) preceeding code ...
Point = function (x, y) {
    var square = function (n) { return n * n; };
    this.getX = function () { return x; };
    this.getY = function () { return y; };
    this.dist = function (pt) {
        return Math.sqrt(square(x - pt.x) + square(y - pt.y));
    };
    return this; // (optional)
};
origin = new Point(0, 0);
// ... more code ...
```

Before delving into the difference between the above two, please take a minute to observe the similarities. The differences are discussed in the following sections.

#### 6.1.1 No `new`

In JS , if you forget the `new` operator, `this` will be bound to the global object (`window` in browsers.) Thus, `getX()`, `getY()` and `dist()` will be added in the global namespace! This is very bad!

Excluding `this` not only prevents you from making the `new` blunder, but is equally (or arguably more) expressive.

#### 6.1.2 Identifier names

In JS, names of constructors conventionally begin with a capital letters. Being mindful of this convention, in LittleJ, identifier names may not being with an upper case letter.

There are two more limitations, namely:

- Unless the identifier is `_`, it may not contain dangling underscores.
- Unless the identifier is `$`, it may not contain any dollar signs. 

Both `_` and `$` are meant to be used as namespaces for standard libraries (currently under development.) Programmers are highly discouraged from using them (for any other purpose.)

#### 6.1.3 No `Foo.prototype`

`this` comes with its share of goodies, namely the prototype chain. Prototypal inheritance is perhaps the best model for code reuse. However, JavaScript's implementation of prototypal inheritance is confusing (and perhaps irritating.)

As there are no constructors in LittleJ, JavaScript-like prototype chains are not supported. However, the `underbar.l.js` library (currently under development) should largely fill this void. It contains the method `_.setPrototype()` which is analogous to Lua's `setmetatable()`.

#### 6.1.4 No `in`

The `in` keyword in JavaScript (notoriously) looks for properties up the prototype-chain. Including it in LittleJ would lead to semantic inequality (with JavaScript). It has hence been excluded.

#### 6.1.5 Things are just what they seem

As there's no prototype chain, objects do not have any mysterious properties. An object has exactly what you put in it. The same goes with arrays and all other datatypes.

Unfortunately, this means that arrays and strings don't even have useful properties like `length`. This is fixed via inbuilt functions discussed in the next section. 

### 6. Inbuilt Functions & Objects

There are **9** inbuilt functions, complimented by the inbuilt `math` object. Each inbuilt has an equivalent in JavaScript, which can be defined in a few lines of code.

#### 6.1 `type()`

JavaScript's `typeof` operator is not particularly helpful. In fact, it is confusing. In LittleJ, it has been replaced by a more meaningful `type()` function.

`type(x)` may be one of: 

- `"boolean"`, `"number"`, `"string"`, `"array"`, `"object"`, `"function"`, `"null"`.

JS Equivalent:
```js
var type = function (x) {
    if (x === null) { return 'null'; }
    if (Object.prototype.toString.call(x) === '[object Array]') { return 'array'; }
    return typeof x;
};
```

#### 6.2 `del()`

`del()` replaces JavaScript's `delete` operator. It accepts two arguments, an object and key or an array and index. This makes it clear that `del()` cannot be used to delete variables.

JS Equivalent:
```js
var del = function (x, y) {
    if (global.type(x) === 'array') {
        x.splice(y, 1);
        return true;
    } else { return delete x[y]; }
}
```

As opposed to `delete`, `del` does not leave any `undefined` holes when deleting from arrays.

#### 6.3 `len()`

The length of arrays, strings and objects is available via the `len()` function. The `len()` of an object is the number of keys it has.

JS Equivalent:
```js
var len = function (x) {
    if (type(x) === 'object') { return Object.keys(x).length; }
    return x.length;
};
```
`type()` defined in section 6.1 was used above. If you don't like this treatment, then use:

```js
var len = function (x) {
    if (typeof x === 'string') { return x.length; }
    return Object.keys(x).length;
};
``` 

#### 6.4 `keys()`

`keys()` in LittleJ returns the all the keys in an object.

JS Equivalent: 
```js
var keys = Object.keys;
```

#### 6.4.1 `KeyError`

In JS, trying to retrieve a non-existent key from an object results in `undefined`. There is no `undefined` in LJ; instead, a `KeyError` is thrown. The `underbar.l.js` library has a function `_.hasKey` which should be used if the unsure about any key.

### The rest of this article is incomplete.
### The following is rough sketch.

#### 6.5 `str()`

#### 6.6 `append()`

#### 6.7 `assert()`

#### 6.8 `ord()`

#### 6.9 `chr()`

#### 6.10 `math`

#### 6.11 `print` (bonus)

#### 6.12 [equalizeLJ.js](https://github.com/sumukhbarve/jispy/blob/master/equalizeLJ.js)

**Note:**  
LittleJ's `type()` function has a [JavaScript equivalent](http://javascript.crockford.com/code.html). Before running a LittleJ program in JavaScript, `type()` (and a few other inbuilts) should be defined in JavaScript. Having done so, LittleJ continues to be a strict subset of JavaScript. The job of so setting-up JavaScript for handling LittleJ programs is done by [equalizeLJ.js](https://github.com/sumukhbarve/jispy/blob/master/LittleJ.md).

### 7. Bitwise operators,  `==`, `!=` `++` and `--` are excluded.

Thesedays, we realize that a high level programming language such as JavaScript doesn't need bitwise operators. They are not included in LittleJ.

Javascript's `==` and `!=` operators are nothing but a recipe for disaster. They, likewise, are not included in LittleJ.

The increment and decrement operators are not really required. Use shorthand assignment `+=` and `-=` instead. Far more readable. 

### 8. Relational (and equality) operators cannot be chained

Try the following code in your browser's console. It might shock you.

```js
console.log(1 === 1 === 1); // --> false; (true === 1) is false
console.log(1 > 1 < 1);     // --> true;  (false < 1) is true
console.log(0 >= 0 >= 1);   // --> true;  (true >= 1) is true
```

The above example aptly demonstrates that JavaScript's relational operators should not be chained. LittleJ doesn't allow you to.

### 9. Blocks are required wherever legal

The following types of statements are included in LJ:

+ `if` (including `else` and if-else ladders)
+ `while`
+ conventional `for`

Each one of the above statements requires a block `{  }`.

The `for` loop has the following form:
```js
for (assignment; condition; increment) {
   body
}
```

Each clause, i.e. `assignment`, `condition`, `increment` and `body` 

### 10. Keywords

The following JS keywords are meaningful in LJ:
```js
var if else while for break function return true false
```

All other JS keywords along with the words ` undefined`, `NaN` and `Infinity` are meaningless in LJ and **may not be used**.

### 11. Examples

See [`underbar.l.js`](https://github.com/sumukhbarve/jispy/blob/master/underbar.l.js). It is written in pure LJ.
