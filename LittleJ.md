# <center>LittleJ</center>

The subset of JavaScript which Jispy interprets is fondly called LittleJ (or **LJ**).

It is a <u>**strict subset of JavaScript**</u>, strict in two senses:

+ LittleJ is a **proper subset** of Javascript. Thus,
    - Ever valid LittleJ program is also a valid JavaScript program.
    - Every valid LittleJ program retains its meaning (semantics) in JavaScript.
    - However, every valid JavaScript program is **NOT** a valid LittleJ program.
+ LittleJ is **far less permissive** than JavaScript.
    - The rest of this specification explores this ascept in depth.

**Note:**

- This document and each document linked herein is work in progress. 
- In particular, inbuilts functions (apart from `type()`) are not described.
- Although not likely, some specification/feature may change.

LittleJ borrows **heavily** from [Douglas Crockford's JS Conventions](http://javascript.crockford.com/code.html). In a few cases, it is stricter (than [JSLint](http://jslint.com/)).

### <center>Features & Rules</center>

#### 1. No `undefined`

All languages have some notion of emptiness. It may be called may it be called `None`, `nil`, `void`, `null` etc. [JavaScript calls it `undefined`; and also has `null` (which indicates *intentional* emptiness.)](http://javascriptweblog.wordpress.com/2010/08/16/understanding-undefined-and-preventing-referenceerrors/)

JavaScript's **overindulgence** in `undefined` *masks otherwise easily detectable errors*. For clarity and ease of understanding, `undefined` is excluded from LittleJ; it is meaningless and may not be used. This has the following implications:

+ Every variable must be **initialized** with a value, it may not merely be defined.
    - `var ans = [], x = null, i = 0;` is valid. But,
    - `var ans = [], x, i = 0;` is **INVALID** because `x` is not initialized.
+ All functions **MUST** have a return value.
    - A non-returning function causes a `TypeError`
+ You may not pass too many or too few arguments to a function.
    - Passing too many or too few arguments is a `TypeError`.
    - Thus, **the keyword `arguments` is meaningless** and cannot be used.

**Note:**  
Losing `arguments` does not limit a function's ability to accept a variable number of inputs. It may receive multiple inputs by accepting a single array or object.

#### 2. No Implied Globals

In JavaScript, any variable which wasn't defined with a `var` statement is assumed to belong to the global scope. Such variables are called implied globals and [are very bad](http://yuiblog.com/blog/2006/06/01/global-domination/).

To remedy this problem, in LittleJ:

+ All variables must be *initialized* using a `var` statement.
+ Once initialized, they may not be reinitialized (in the same scope.)
    - Trying to do so would cause a `ReferenceError`.

**Note:**  
While you may not reinitialize a variable, you may always reset its value via (mere) assignment. Thus, `var a = 10; a = 11;` is legal. However, `var a = 10, a = 11;` is **ILLEGAL**.

#### 3. Clean Scoping

*JavaScript does **NOT** have block scope*. It has functional scope. Initializing a variable just before its point for first use is very BAD advise in JavaScript.

In particular,
> ".. defining variables in blocks can confuse programmers who are experienced with other C family languages. ... " *~ Douglas Crockford*

LJ's remedy:

+ There may be **atmost one `var` statement per scope.**
+ If a `var` statement is used in a any given scope:
    - the keyword `var` must be the **first token** in that scope;
    - and it  may **NOT** (re)appear anywhere else in that scope.
+ This is applicable to the global scope as well.

This makes it very difficult to goof up scoping Even those who don't know about functional scope cannot go wrong.

##### The `null` convention:
Wherever you would use `var a = [], i` in JavaScript, use `var a = [], i = null` in LittleJ. This makes your intentions very clear. Do so even if you are about to set `i` to `0` in a `for` statement.

#### 4. Functions are first class citizens

Functions are one of the very best parts of JavaScript. LittleJ is proud to include them. The meaning of the "Functions are first class citizens" is:

+ A function may return a function.
+ A function may be passed (as an argument) to a function.
+ A function may close over other functions. (Closures are supported.)

However, as with most things in JavaScript, there is a (small) bad part associated with function declarations, namely **function hoisting**. It allows you to use functions before you declare them. This unsettles me.

Luckily, function values (created via function expressions) are not hoisted. Therefore, in LittleJ: 

+ Function declarations such as `function foo() { return null; }` are excluded.
+ Only function expressions as `foo = function () { return null; }` are supported.

When a function is to be invoked immediately, wrap the entire invocation in a pair of parenthesis. This not only makes your intention clear, but is (in some cases) required by JavaScript.
That is, use:
```js
(function (x) { return x * x; }(2));
```
instead of:
```js function (x) { return x * x; }(2);```

**Note:**  
Currently, only anonymous functions are supported. This is not likely to change in the near future. (Anonymous functions may be recursive.)

#### 5. No `NaN` and no `Infinity`

Like `undefied`, `NaN` and `Infinity` *mask too many errors that may otherwise be easily detected*. Their exclusion from LittleJ has the following implications:

+ `1 / "a string"` causes a `TypeError`, it isn't `NaN`.
+ `1 / 0` causes `ZeroDivisionError`, it isn't `Infinity`.

#### 6. `type()` in place of `typeof`

JavaScript's `typeof` operator is not particularly helpful. In fact, it is confusing. In LittleJ, it has been replaced by a more meaningful inbuilt function `type()`.

+ `type(x)` may be one of: 
    - `"boolean"`, `"number"`, `"string"`, `"array"`, `"object"`, `"function"`, `"null"`.
    - It may **not** be `"undefined"` as that is excluded.

**Note:**  
LittleJ's `type()` function has a [JavaScript equivalent](http://javascript.crockford.com/code.html). Before running a LittleJ program in JavaScript, `type()` (and a few other inbuilts) should be defined in JavaScript. Having done so, LittleJ continues to be a strict subset of JavaScript. The job of so setting-up JavaScript for handling LittleJ programs is done by [equalizeLJ.js](https://github.com/sumukhbarve/jispy/blob/master/LittleJ.md).

#### 6. Bitwise operators,  along with  `==`, `!=` `++` and `--` are excluded.

Thesedays, we realize that a high level programming language such as JavaScript doesn't need bitwise operators. They are not included in LittleJ.

Javascript's `==` and `!=` operators are nothing but a recipe for disaster. They, likewise, are not included in LittleJ.

The increment and decrement operators are not really required. Use shorthand assignment `+=` and `-=` instead. Far more readable. 

#### 7. Relational (and equality) operators cannot be chained

Try the following code in your browser's console. It might shock you.

```js
console.log(1 === 1 === 1); // --> false; (true === 1) is false
console.log(1 > 1 < 1);     // --> true;  (false < 1) is true
console.log(0 >= 0 >= 1);   // --> true;  (true >= 1) is true
```

The above example aptly demonstrates that JavaScript's relational operators should not be chained. LittleJ doesn't allow you to.

#### 8. No `this` and *no prototype chain*

In JavaScript, there are four function invocation patterns. The value of `this` is determined by the invocation pattern used. `this` makes JavaScript look like Java. Apart from that, it rarely does anything useful.

JavaScript's constructors are amazing at diverting our attention from its truly prototypal nature. Why do we need to use constructors (or equally classes) when objects are object factories! We don't. No exceptions.

Perhaps the biggest irony in JavaScript is that the prototype chain shadows the language's true prototypal nature. In my opinion, Lua's `setmetatable` is what JavaScript's `setprototype` should have been. Further, the prototype chain leads to unwanted noise with the `in` keyword.

LittleJ address problems associated with `this` and `prototype` by simply not including them at all. This has the following implications on LittleJ:

+ The `in` keyword is excluded. It may not be used.
+ There are no constructors. We don't need them.  
    - Thus, all variable names must begin with a <u>**lowercase**</u> alphabet.
    - This seems like  a good time to mention that dangling underbars `_` and dollar signs `$` are not allowed in variable names.
+ The `new` keyword is excluded. It may not be used.
+ JavaScript's globally available `Object`, `Array`, `String`, `Number` , `Boolean`etc. are excluded.
+ **Things are exactly what they seem. *No magic.* **
    - Objects are objects, arrays are arrays (not objects), functions are functions (not objects), strings are strings, numbers are numbers and booleans are booleans.
    - Values don't *implicitly* inherit anything (from anywhere.)
    - Thus, `var obj = {};` initializes an object with **NO properties**. Not even properties like `hasOwnProperty`, which in JavaScript, would be inherited from `Object.hasOwnProperty`. There's an inbuilt function `keys()`, equivalent to JavaScript's `Object.keys()`
    - Similarly, `var arr = []` initializes an empty array with no indices. **Arrays DON'T have properties** in LittleJ. They don't even have a `length` property. There's an inbuilt function `len()`, which returns the length of arrays (, strings and objects).
    - `str()` is another inbuilt function which converts all types except functions to a string form.
    - You may use the **unary** `+` operator to convert strings to numbers, and `!!` to convert anything to a boolean.

#### Doesn't LittleJ  sound like a new programming language?

Yes. It **SOUNDS** like a new programming language. But it is **NOT** a new language.

Toward the beginning of this document the following was stated:

+ Every valid LJ program is also a valid JS program.
+ Every valid LJ program has the same meaning in JS, as it does in LJ.

The above statements are still true, with an added requirement:

+ Before executing an LJ program in JS, LJ's inbuilts `type()`, `keys()`, `len()`, and `str()` should be defined as JS functions. These definitions are quite simple.

+ Also, the functions `write()` and `writeln()` are (by default) included in LJ by Jispy's `Runtime` class. These may be disabled via the Python API. See [README.md](https://github.com/sumukhbarve/jispy/blob/master/README.md) for more details. In either case, these functions too have JavaScript equivalents.

#### 9. Blocks are required wherever legal

The following types of statements are included in LJ:

+ `if` (including `else` and if-else ladders)
+ `while`
+ conventional `for`

Each one of the above statements requires a block `{  }`.

The `for` loop has the following form:
```js
for (assignment, condition, increment) {
   body
}
```

Each clause, i.e. `assignment`, `condition`, `increment` and `body` must be non-blank.

#### 10. No `try` and `catch`

`try` and `catch` blocks are useful. Unfortunately, if included, LittleJ ceases to be a semantic subset of JavaScript.

Consider the following code:
```js
var n = 10, s = "foobar", ans = 0;
try {
    ans = n / s;           // line A
    foo();                 // line B
}
catch (e) {
    bar();                 // line C
}
```

As per LJ, line A produces a `TypeError`. But there is no error according to JS.

On hitting line A, if LJ causes control to jump to the `catch` block,
then the function `bar()` will be invoked. However, in JS the function `foo()` will be invoked.

So, an LJ program would have a different meaning than a JS program. This is a contradiction. LJ may not include `try` and `catch` blocks.


#### Keywords

The following JS keywords are meaningful in LJ:
```js
var if else while for break function return true false
```

All other JS keywords along with the words ` undefined`, `NaN` and `Infinity` are meaningless in LJ and **may not be used**.

---------------------------------------------------------------------

## Example Programs

Computing factorial:
```js
var n = 6, factorial = function (n) {
    if (n <= 1) { return 1; }
    return n * factorial(n - 1);
};
writeln(factorial(n)); // prints 720
```

More examples coming soon.
