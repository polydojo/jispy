#############################################################################
#                                                                           #
#   Test code for Jispy.                                                    #
#                                                                           #
#   Copyright (c) 2017 Polydojo, Inc.                                       #
#                                                                           #
#                                                                           #
#                                                                           #
#   This Source Code Form is subject to the terms of the Mozilla Public     #
#   License, v. 2.0. If a copy of the MPL was not distributed with this     #
#   file, You can obtain one at http://mozilla.org/MPL/2.0/.                #
#                                                                           #
#############################################################################

from jispy import lex, yacc, Runtime

tests = [
    '''    // Test-0: testing for loop (factorial)
        var n = 6.0, ans = 1, i = 1;
        for (i = 1; i <= n; i += 1) { ans = ans * i; }
        print(ans === 6*5*4*3*2*1);
    ''',
    #    -----------------------------------------------------
    '''    // Test-1: shorthand assignments.
        // Generating 9 times table
        var i = 0, j = 10;
        while (i < 10) {
            //print('9 x ' + str(i+1) + ' = ' + str(i) + str(j));
            i += 1;
            j -= 1;
        }
        print(i === 10 && j === 0);
    ''',
    #    -----------------------------------------------------
    '''    // Test-2: inbuilt len() and keys()
        var nil = 0,
            obj = {a:'apple', b:'ball', c:'cat'},
            leno = function (x) {                            // Note: when this function was written,
                if (type(x) === 'object') {                    //            len() accepted strings and arrays only.
                    return len(keys(x));                    //             Now, it also accepts objects.
                } else {
                    return len(x);
                }
            };
        print(leno(obj) === 3);
    ''',
    #    -----------------------------------------------------
    '''    // Test-3.: inbuilt type()
        var i = 0, flag = true,
            fon = function () { return 1; },
            arr = [true, 1, 's', [], {}, fon],
            expected = ['boolean', 'number', 'string', 'array', 'object', 'function'];
        while (i < len(arr)) {
            if (type(arr[i]) !== expected[i]) {
                flag = false;
                //print('false - '+str(arr[i])+' is not '+ expected[i]);
                break;
            }
            i = i + 1;
        }
        print(flag);
    ''',
    #    -----------------------------------------------------
    ''' // Test-4: function w/ no params
        var foo = function () { return true; };
        print(foo());
    ''',
    #    -----------------------------------------------------
    '''    // Test-5: calling a function literals w/ no params
        print(!!function(){return 1;}());
    ''',
    #    -----------------------------------------------------
    ''' // Test-6: working with objects and arrays
        var obj = {a: 'apple', b: 'ball', c: [1,2,3,4]},
            flag0 = obj.a === 'apple',
            flag1 = obj.c[0] === 1;
        obj['a'] = 0;
        obj['b'] = 1;
        obj['c'] = 2;
        flag0 = obj.a === 0 && obj.b === 1 && flag0 && flag1;
        print(flag0);
    ''',
    #    -----------------------------------------------------
    '''
    // Test-7: recursive defn of factorial
        var inp = 6, factorial = function (x) {
            var i = 1, ans = 1;
            if (x < 0) { return -1; }
            else if (x === 0) { return 1; }
            else { return x * factorial(x - 1); }
        };
        print(factorial(6) === 720);
    ''',
    #    -----------------------------------------------------
    '''    // Test-8: scoping and var-stmt within functions
        var g = 0,
            get1 = function (g) {
                var one = 1;
                g = 1000;        // outter-g should be 0;
                return one;
        };
        print(g === 0);
    ''',
    #    -----------------------------------------------------
    '''    // Test-9: testing return (w/ simple add function)
        var a = 1, b = 2,
            add = function(x, y) {
                return x + y;
            };
        print(add(a, b) === 3);
    ''',
    #    -----------------------------------------------------
    '''    // Test-10: break-statement
        var brokeOut = false;
        while (1) {
            brokeOut = true;
            break;
        }
        print(brokeOut);
    ''',
    #    -----------------------------------------------------
    '''    // Test-11: while (factorial)
        var n = 10, i = 1, ans = 1;
        while (i <= n) {
            ans = ans * i;
            i = i + 1;
        }
        print(ans === 10*9*8*7*720);
    ''',
    #    -----------------------------------------------------
    '''    // Test-12: simple dot-refinement
        var obj = {a : 'apple'};
        print(obj.a === 'apple');
    ''',
    #    -----------------------------------------------------
    '''    // Test-13: cascaded dot-refinement
        var obj = {a : {b : 'bombay'} };
        print(obj.a.b === 'bombay');
    ''',
    #    -----------------------------------------------------
    '''    // Test-14: dot & subscript
        var flag = false, obj = {
            x : 'x',
            y : {z : 'king'}
        };
        flag = obj['y'].z === obj.y['z'] && obj.y['z'] === obj.y.z;
        print(flag);
    ''',
    #    -----------------------------------------------------
    #''' // Test-14-negative: associativity of ===                    # Appropriate SyntaxError was successfully raised
    #    print(1 >= 0 > 1);
    #    print(1 === 1 === 1);
    #''',
    #    -----------------------------------------------------
    '''    // Test-15: assigning to dot-refined property
        var obj = {a : 'apple'};
        obj.a = 'newApple';
        print(obj.a === 'newApple');
    ''',
    #    -----------------------------------------------------
    '''    // Test-16: leading dots (dot-refinements)
        var obj = { // some JSend ...
            status : "success",
            data : {
                    "post" : { "id" : 1, "title" : "A blog post", "body" : "Some useful content" }
                     }
        };
        print(obj.data
                        .post.id === 1);
    ''',
    #    -----------------------------------------------------
    #'''    // Test-16-negative: trailing dots (dot-refinements)        # Currently, trailing refinements are unsupported.
    #    var obj = { // some JSend ...                        # An appropriate error was raised.
    #        status : "success",
    #        data : {
    #                "post" : { "id" : 1, "title" : "A blog post", "body" : "Some useful content" }
    #                 }
    #    };
    #    print(obj.data.
    #                    post.id === 1);
    #''',
    #    -----------------------------------------------------
    '''    // Test-17: Writing a function, `ternary`
        var inp = 7, flag = false,
            ternary = function (cond, conseq, alt) {
                if (cond) { return conseq; }
                return alt;
            };
            flag =  ternary(true, 'conseq', 'alt') === 'conseq' &&
                    ternary(false, 'conseq', 'alt' === 'alt')     // woo! a comment!!
                    ; // exp ends here..
            print(flag);
        
    ''',
    #    -----------------------------------------------------
    '''    // Test-18: Unary +
        var flag = +'88.88' === 88.88 && -(+'7') === -7;
        print(flag);
    ''',
    #''' // Test-18-negative-1: Max Loop Time                            # Test was SUCCESSFUL.
    #    var tmp = 0;
    #    while(1) {tmp += 1;}
    #''',
    #    -----------------------------------------------------
    #'''    // Test-18-negative-2: Max (Scope) Depth                    # Test was SUCCESSFUL.
    #    var foo = function () { foo(); };
    #    foo();
    #''',
    #    -----------------------------------------------------
    '''    // Test-19: a for apple, b for ball, c for cat;
        var obj = {}, i = 0, k = 0, out = '';
        obj.a = 'apple'; obj.b = 'ball'; obj.c = 'cat';
        for (i = 0; i < len(obj); i += 1) {
            k = keys(obj)[i];
            out += k + ' for ' + obj[k] + ' ';
        }
        print(out === 'a for apple c for cat b for ball ');
    ''',
    #    -----------------------------------------------------
    ''' // Test-20: multiple assignments in for loop (assignment clause)
        var i = false, j = false, flag = true;
        for (i = 1, j = 1; i <= 10; i += 1, j += 1) {
            if (i !== j) {
                flag = false;
                break;
            }
        }
        print(flag);
    ''',
    # -------------------------------------------------------
    ''' // Test-21: del() (with objects)
        var obj = {a: 'apple', b: 'ball'}, ks = false, i = 0,
            isIn = function (obj, key) {
                ks = keys(obj);
                for (i = 0; i < len(ks); i += 1) {
                    if (ks[i] === key) {
                        return true;
                    }
                }
                return false;
            };
        del(obj, 'a');
        print(!isIn(obj, 'a'));
    ''',
    # -------------------------------------------------------
    '''    // Test-22: math''s max, min, round, floor, ceil
        var f = {};        // a container for flags
        f.a = math.round(1.23) === 1;
        f.b = math.max([1,2,3]) === 3;
        f.c = math.min([1,2,3]) === 1;
        f.d = math.ceil(1.2) === 2;
        f.e = math.floor(1.8) === 1;
        f.f = math.sqrt(4) === 2;
        print(f.a && f.b && f.c && f.d && f.e && f.f);
    ''',
    # -------------------------------------------------------
    ''' // Test-23: closures                                // This test lead to a MAJOR bugfix.
        var a = 10, b = 20, add1 = 0, addN = 0;             // The env in which a function-body should be executed/run
        addN = function (n) {                               //        is not the env in which it was invoked,
                var func = 0;                               //        but the env in which it was created. 
                n;
                func = function (x) { return x + n; };      // Previously (before the bugfix), add1 was called with
                return func;                                //         the direct parent being the Global env.
        };
        add1 = addN(1);                                     // Now, it is called with parrent env being that of addN,
        print(add1(100) === 101);                           //        as it was created in addN''s env.
                                                            
                                                            // However, the arguments supplied to a function, must of course,
                                                            //        be computed in the environment in which it is invoked.
    ''',
    # -------------------------------------------------------
    '''    // Test-24: math.random()                            // This test takes quite long. Hence is not always run.
        var dis =[0,0,0,0,0,0,0,0,0,0], i = 0, x = 0,        // dis for distribution (of random samples).
            mapped = 0,
            all = function (arr) {
                var a = 0;
                for (a = 0; a < len(arr); a += 1) {
                    if (!arr[a]) { return false; }
                }
                return true;
            },
            map = function(arr, func) {                       // This is a BAD defn of `map`
                var m = 0;                                    //    as the input array is changed.
                for (m = 0; m < len(arr); m += 1) {
                    arr[m] = func(arr[m]);                    // map was written before the inbuilt `concat` was introduced in LJ
                }
                return arr;
            },
            within = function(x, y) {
                return function (n) {
                    return  x < n && n < y;
                };
            };
        for (i = 0; i < 200; i += 1) {
            x = math.floor(math.random()*10);
            dis[x] += 1;
        }
        //print(dis);
        mapped = map(dis, within(2*4, 2*16));
        //print(mapped);
        print(str(all(mapped)) + ' // probability based');
    ''',
    # -------------------------------------------------------
    '''    // Test-25: del() with arrays
        var a = [1,2,3];    // len(a) is 3;
        print(del(a, 0) && len(a) === 2);
    ''',
    # -------------------------------------------------------
    '''    // Test-26: append()
        var a = [];
        append(a, 'x');
        print(len(a) === 1 && a[0] === 'x');
    ''',
    # -------------------------------------------------------
    '''    // Test-27: null via factorial
        var f = function (n) { 
            if (n < 0 || n !== math.round(n)) { return null; }
            if (n <= 1) { return 1; }
            return n * f(n - 1);
        };
        print(f(-1) === null && f(5.5) === null && f(6) === 720);
    ''',
    # -------------------------------------------------------
    ''' // Test-28: using append() and assert()
        //            to write map() and filter()
        var a = [3, 4], m = null,
            flagMap = false, flagFilter = false,
            allF = [0, false, '', null],    // all truthy
            allT = [1, true, 'x', [], {}],    // all falsy
            map = function (arr, fon) {
                var ans = [], i = null;
                assert(type(arr) === 'array', 'map() called on non-array');
                assert(type(fon) === 'function', 'map() called with non-function');
                for (i = 0; i < len(arr); i += 1) {
                    append(ans, fon(arr[i]));
                }
                return ans;
            },
            filter = function (arr, fon) {
                var ans = [], i = null, tmp = null;
                assert(type(arr) === 'array', 'cannot filter() a non-array');
                fon = fon || function (x) { return x; };
                for (i = 0; i < len(arr); i += 1) {
                    tmp = fon(arr[i]);
                    if (tmp) { append(ans, tmp); }
                }
                return ans;
            };
            m = map(a, function (x) { return x * x; });
            
            //print(m);
            //print(filter(allT, null)); 
            //print(filter(allF, null));
            
            flagMap = len(m) === 2 && m[0] === 9 && m[1] === 16;
            flagFilter = len(filter(allF, null)) === 0 &&
                        len(filter(allT, null)) === len(allT);
            print(flagMap && flagFilter);
    ''',        
    # -------------------------------------------------------
    '''    //Test-29: writing clone()
        var arr = [3, 4], obj = {a: 'apple', b: 'ball'},
            arrClone = null, objClone = null,
            cloneArray = function (arr) {
                var clone = [], i = null, tmp = null;
                for (i = 0; i < len(arr); i += 1) {
                    tmp = arr[i];
                    if (type(tmp) === 'array') {
                        append(clone, cloneArray(tmp));
                    } else if (type(tmp) === 'object') {
                        append(clone, cloneObject(tmp));
                    } else {
                        append(clone, tmp);
                    }
                }
                return clone;
            },
            cloneObject= function (obj) {
                var clone = {}, kez = keys(obj), i = null, val = null;
                for (i = 0; i < len(kez); i += 1) {
                    val = obj[kez[i]];
                    if (type(val) === 'object') {
                        clone[kez[i]] = cloneObject(val);
                    } else if (type(val) === 'array') {
                        clone[kez[i]] = cloneArray(val);
                    } else {
                        clone[kez[i]] = val;
                    }
                }
                return clone;
            },
            clone = function (x) {
                if (type(x) === 'array') {
                    return cloneArray(x);
                } else if (type(x) === 'object') { 
                    return cloneObject(x);
                } else {
                    assert(false, 'bad call to clone()');
                }
            };
        arrClone = clone(arr);
        objClone = clone(obj);
        print(arrClone !== arr && objClone !== obj);
        //print(arrClone); print(arr);                        // Clones were visually confirmed.
        //print(objClone); print(obj);                        // This test was successful.
    ''',
    # -------------------------------------------------------
    ''' // Test-30: writing indexOf()
        var a = [0, 1, 2, 3, 4, 'five'],
            indexOf = function (arr, elt) {
                var i = null;
                for (i = 0; i < len(arr); i += 1) {
                    if (arr[i] === elt) { return i; }
                }
                return -1;
            };
        print(indexOf(a, 0) === 0 && indexOf(a, 'five') === 5 &&
                indexOf(a, 100) === -1 && indexOf([], 8) === -1);
    ''',
    # -------------------------------------------------------
    ''' // Test-31: writing rot13() using ord() and chr()
        var rot1 = function (c) {
                var i = null;               
                if (c === 'z') { return 'a'; }
                if (c === 'Z') { return 'A'; }
                i = ord(c);
                if ((97 <= i && i < 97 + 26) || (65 <= i && i < 65 + 26)) {
                    return chr(i + 1);
                }
                return c;
            },
            rot13 = function (s) {
                var ans = '', i = null, j = null, c = null;
                for (i = 0; i < len(s); i += 1) {
                    c = s[i];
                    for (j = 0; j < 13; j += 1) { c = rot1(c); }
                    ans += c;
                }
                return ans;
            };
            print(rot13('zing&&kong!!') === 'mvat&&xbat!!');
    ''',
    # -------------------------------------------------------
    ''' // Test-30: Closure (Similar to Test-23)
        var mkAddX = null, add1 = null, add100 = null;
        mkAddX = function (x) {
            return function (n) {
                return x + n;
            };
        };
        add1 = mkAddX(1);
        add100 = mkAddX(100);
        
        print (add1(1) === 2 && add100(100) === 200);
    ''',
]

j = -1
for prog in tests:
    j += 1
    print str(j) + '. ',
    #print 'test     -->\n', t, '\n';
    tokens = lex(prog)
    #print 'tokens   -->\n', tokens, '\n';
    tree = yacc(tokens)
    #print 'tree     -->\n', tree, '\n';
    rt = Runtime(maxLoopTime=13, maxDepth=100)
    rt.run(tree)
