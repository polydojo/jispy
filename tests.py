from jispy import lex, yacc, Runtime;

tests = [
	'''	// Test-0: testing for loop (factorial)
		var n = 6.0, ans = 1, i = 1;
		for (i = 1; i <= n; i += 1) { ans = ans * i; }
		writeln(ans === 6*5*4*3*2*1);
	''',
	#	-----------------------------------------------------
	'''	// Test-1: shorthand assignments.
		// Generating 9 times table
		var i = 0, j = 10;
		while (i < 10) {
			//writeln('9 x ' + str(i+1) + ' = ' + str(i) + str(j));
			i += 1;
			j -= 1;
		}
		writeln(i === 10 && j === 0);
	''',
	#	-----------------------------------------------------
	'''	// Test-2: inbuilt len() and keys()
		var nil = 0,
			obj = {a:'apple', b:'ball', c:'cat'},
			leno = function (x) {							// Note: when this function was written,
				if (type(x) === 'object') {					//			len() accepted strings and arrays only.
					return len(keys(x));					// 			Now, it also accepts objects.
				} else {
					return len(x);
				}
			};
		writeln(leno(obj) === 3);
	''',
	#	-----------------------------------------------------
	'''	// Test-3.: inbuilt type()
		var i = 0, flag = true,
			fon = function () { return 1; },
			arr = [true, 1, 's', [], {}, fon],
			expected = ['boolean', 'number', 'string', 'array', 'object', 'function'];
		while (i < len(arr)) {
			if (type(arr[i]) !== expected[i]) {
				flag = false;
				break;
			}
			i = i + 1;
		}
		writeln(flag);
	''',
	#	-----------------------------------------------------
	''' // Test-4: function w/ no params
		var foo = function () { return true; };
		writeln(foo());
	''',
	#	-----------------------------------------------------
	'''	// Test-5: calling a function literals w/ no params
		writeln(!!function(){return 1;}());
	''',
	#	-----------------------------------------------------
	''' // Test-6: working with objects and arrays
		var obj = {a: 'apple', b: 'ball', c: [1,2,3,4]},
			flag0 = obj.a === 'apple',
			flag1 = obj.c[0] === 1;
		obj['a'] = 0;
		obj['b'] = 1;
		obj['c'] = 2;
		flag0 = obj.a === 0 && obj.b === 1 && flag0 && flag1;
		writeln(flag0);
	''',
	#	-----------------------------------------------------
	'''
	// Test-7: recursive defn of factorial
		var inp = 6, factorial = function (x) {
			var i = 1, ans = 1;
			if (x < 0) { return -1; }
			else if (x === 0) { return 1; }
			else { return x * factorial(x - 1); }
		};
		writeln(factorial(6) === 720);
	''',
	#	-----------------------------------------------------
	'''	// Test-8: scoping and var-stmt within functions
		var g = 0,
			get1 = function (g) {
				var one = 1;
				g = 1000;		// outter-g should be 0;
				return one;
		};
		writeln(g === 0);
	''',
	#	-----------------------------------------------------
	'''	// Test-9: testing return (w/ simple add function)
		var a = 1, b = 2,
			add = function(x, y) {
				return x + y;
			};
		writeln(add(a, b) === 3);
	''',
	#	-----------------------------------------------------
	'''	// Test-10: break-statement
		var brokeOut = false;
		while (1) {
			brokeOut = true;
			break;
		}
		writeln(brokeOut);
	''',
	#	-----------------------------------------------------
	'''	// Test-11: while (factorial)
		var n = 10, i = 1, ans = 1;
		while (i <= n) {
			ans = ans * i;
			i = i + 1;
		}
		writeln(ans === 10*9*8*7*720);
	''',
	#	-----------------------------------------------------
	'''	// Test-12: simple dot-refinement
		var obj = {a : 'apple'};
		writeln(obj.a === 'apple');
	''',
	#	-----------------------------------------------------
	'''	// Test-13: cascaded dot-refinement
		var obj = {a : {b : 'bombay'} };
		writeln(obj.a.b === 'bombay');
	''',
	#	-----------------------------------------------------
	'''	// Test-14: dot & subscript
		var flag = false, obj = {
			x : 'x',
			y : {z : 'king'}
		};
		flag = obj['y'].z === obj.y['z'] && obj.y['z'] === obj.y.z;
		writeln(flag);
	''',
	#	-----------------------------------------------------
	#''' // Test-14-negative: associativity of ===					# Appropriate SyntaxError was successfully raised
	#	writeln(1 >= 0 > 1);
	#	writeln(1 === 1 === 1);
	#''',
	#	-----------------------------------------------------
	'''	// Test-15: assigning to dot-refined property
		var obj = {a : 'apple'};
		obj.a = 'newApple';
		writeln(obj.a === 'newApple');
	''',
	#	-----------------------------------------------------
	'''	// Test-16: leading dots (dot-refinements)
		var obj = { // some JSend ...
    		status : "success",
    		data : {
        			"post" : { "id" : 1, "title" : "A blog post", "body" : "Some useful content" }
     				}
		};
		writeln(obj.data
						.post.id === 1);
	''',
	#	-----------------------------------------------------
	#'''	// Test-16-negative: trailing dots (dot-refinements)		# Currently, trailing refinements are unsupported.
	#	var obj = { // some JSend ...						# An appropriate error was raised.
    #		status : "success",
    #		data : {
    #    			"post" : { "id" : 1, "title" : "A blog post", "body" : "Some useful content" }
    # 				}
	#	};
	#	writeln(obj.data.
	#					post.id === 1);
	#''',
	#	-----------------------------------------------------
	'''	// Test-17: Writing a function, `ternary`
		var inp = 7, flag = false,
			ternary = function (cond, conseq, alt) {
				if (cond) { return conseq; }
				return alt;
			};
			flag =  ternary(true, 'conseq', 'alt') === 'conseq' &&
					ternary(false, 'conseq', 'alt' === 'alt') 	// woo! a comment!!
					; // exp ends here..
			writeln(flag);
		
	''',
	#	-----------------------------------------------------
	#'''	// Test-17-negative: Multiple assignments in for	# Multiple assignments or increments in for-stmt are UNSUPPORTED
	#	var i = 0, j = 0;										# An 'illegal expression' error was raised
	#	for (i = 10, j = 20; i >= 0; i -=1) {
	#		writeln('i = ' + str(i));
	#	}
	#''',
	#	-----------------------------------------------------
	'''	// Test-18: Unary +
		var flag = +'88.88' === 88.88 && -(+'7') === -7;
		writeln(flag);
	''',
	#''' // Test-18-negative-1: Max Loop Time							# Test was SUCCESSFUL.
	#	var tmp = 0;
	#	while(1) {tmp += 1;}
	#''',
	#	-----------------------------------------------------
	#'''	// Test-18-negative-2: Max (Scope) Depth					# Test was SUCCESSFUL.
	#	var foo = function () { foo(); };
	#	foo();
	#''',
	#	-----------------------------------------------------
	#'''	// Test-19: a for apple, b for ball, c for cat;				# TEST WAS SUCCESSFUL.
	#	var obj = {}, i = 0, k = 0;										# But prints out 3 lines....
	#	obj.a = 'apple'; obj.b = 'ball'; obj.c = 'cat';					# so, the next is used instead.
	#	for (i = 0; i < len(obj); i += 1) {
	#		k = keys(obj)[i];
	#		writeln(k + ' for ' + obj[k]);
	#	}
	#''',
	''' // Test-19: going through a object via for loop;
		var obj = {t : true},
			i = 0, k = 0, flag = true;
		for (i = 0; i < len(obj); i += 1) {
			k = keys(obj)[i];
			writeln(obj[k]);
		}
	''',
	#	-----------------------------------------------------
	''' // Test-20: testing multiple assignments in for loop (assignment clause)
		var i = false, j = false, flag = true;
		for (i = 1, j = 1; i <= 10; i += 1, j += 1) {
		    if (i !== j) {
		    	flag = false;
		    	break;
			}
		}
		writeln(flag);
	''',
	# -------------------------------------------------------
	''' // Test-21: testing del
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
		writeln(!isIn(obj, 'a'));
	''',
	# -------------------------------------------------------
	'''	// Test-22: testing math''s max, min, round, floor, ceil
		var f = {};		// a container for flags
		f.a = math.round(1.23) === 1;
		f.b = math.max([1,2,3]) === 3;
		f.c = math.min([1,2,3]) === 1;
		f.d = math.ceil(1.2) === 2;
		f.e = math.floor(1.8) === 1;
		f.f = math.sqrt(4) === 2;
		writeln(f.a && f.b && f.c && f.d && f.e && f.f);
	''',
	# -------------------------------------------------------
	''' // Test-23: testing closures.						// This test lead to a MAJOR bugfix.
		var a = 10, b = 20, add1 = 0, addN = 0;				// The env in which a function-body should be executed/run
		addN = function (n) {								//		is not the env in which it was invoked,
				var func = 0;								//		but the env in which it was created. 
				n;
				func = function (x) { return x + n; };		// Previously (before the bugfix), add1 was called with
				return func;								// 		the direct parent being the Global env.
		};
		add1 = addN(1);										// Now, it is called with parrent env being that of addN,
		writeln(add1(100) === 101);							//		as it was created in addN''s env.
															
															// However, the arguments supplied to a function, must of course,
															//		be computed in the environment in which it is invoked.
	''',
	# -------------------------------------------------------
	'''	// Test-24: testing math.random()				// This test takes quite too long. Hence is not always run.
		var dis =[0,0,0,0,0,0,0,0,0,0], i = 0, x = 0,		// dis for distribution (of random samples).
			mapped = 0,
			all = function (arr) {
				var a = 0;
				for (a = 0; a < len(arr); a += 1) {
					if (!arr[a]) { return false; }
				}
				return true;
			},
			map = function(arr, func) {						// This is a BAD defn of `map`
				var m = 0;									//	as the input array is changed.
				for (m = 0; m < len(arr); m += 1) {
					arr[m] = func(arr[m]);
				}
				return arr;
			},
			within = function(x, y) {
				return function (n) {
					return  x < n && n < y;
				};
			};
		for (i = 0; i < 10000; i += 1) {
			x = math.floor(math.random()*10);
			dis[x] += 1;
		}
		//writeln(dis);
		mapped = map(dis, within(800, 1200));
		//writeln(mapped);
		writeln(all(mapped));
	''',
];

j = -1;
for prog in tests:
	j += 1;
	print str(j) + '. ',
	if j == 24: print 'skipped'; continue;					# Commentify this line to not skip Test-24.
	#if j != 23: continue;
	#print 'test     -->\n', t, '\n';
	tokens = lex(prog);
	#print 'tokens   -->\n', tokens, '\n';
	tree = yacc(tokens);
	#print 'tree 	-->\n', tree, '\n';
	rt = Runtime(maxLoopTime=13, maxDepth=100);
	rt.run('', tree = tree);								# rt.run(prog) would work, but tree would be wastefully recomputed
	#if j == 8: break;
	#break;
