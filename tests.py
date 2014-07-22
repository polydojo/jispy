from jispy import lex, yacc, Runtime;

tests = [
	'''	// Test-0: testing for loop (factorial)
		var n = 6.0, ans = 1, i = 1;
		for (i = 1; i <= n; i += 1) { ans = ans * i; }
		writeln('0.  ' + str(ans === 6*5*4*3*2*1));
	''',
	#	-----------------------------------------------------
	'''	// Test-1: shorthand assignments.
		// Generating 9 times table
		var i = 0, j = 10;
		while (i < 10) {
			//print('9 x ' + str(i+1) + ' = ' + str(i) + str(j));
			i += 1;
			j -= 1;
		}
		writeln('1.  ' + str(i === 10 && j === 0));
	''',
	#	-----------------------------------------------------
	'''	// Test-2: inbuilt len() and keys()
		var nil = 0,
			obj = {a:'apple', b:'ball', c:'cat'},
			leno = function (x) {
				if (type(x) === 'object') {
					return len(keys(x));
				} else {
					return len(x);
				}
			};
		writeln('2.  ' + str(leno(obj) === 3));
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
		writeln('3.  ' + str(flag));
	''',
	#	-----------------------------------------------------
	''' // Test-4: function w/ no params
		var foo = function () { return true; };
		writeln('4.  ' + str(foo()));
	''',
	#	-----------------------------------------------------
	'''	// Test-5: calling a function literals w/ no params
		writeln('5.  ' + str(!!  function(){return 1;}()  ));
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
		writeln('6.  ' + str(flag0));
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
		writeln('7.  ' + str(factorial(6) === 720));
	''',
	#	-----------------------------------------------------
	'''	// Test-8: scoping and var-stmt within functions
		var g = 0,
			get1 = function (g) {
				var one = 1;
				g = 1000;		// outter-g should be 0;
				return one;
		};
		writeln('8.  ' + str(g === 0));
	''',
	#	-----------------------------------------------------
	'''	// Test-9: testing return (w/ simple add function)
		var a = 1, b = 2,
			add = function(x, y) {
				return x + y;
			};
		writeln('9.  ' + str(add(a, b) === 3));
	''',
	#	-----------------------------------------------------
	'''	// Test-10: break-statement
		var brokeOut = false;
		while (1) {
			brokeOut = true;
			break;
		}
		writeln('10. ' + str(brokeOut));
	''',
	#	-----------------------------------------------------
	'''	// testing while (factorial)
		var n = 10, i = 1, ans = 1;
		while (i <= n) {
			ans = ans * i;
			i = i + 1;
		}
		writeln('11. ' + str(ans === 10*9*8*7*720));
	''',
	#	-----------------------------------------------------
	'''	// Test-12: simple dot-refinement
		var obj = {a : 'apple'};
		writeln('12. ' + str(obj.a === 'apple'));
	''',
	#	-----------------------------------------------------
	'''	// Test-13: cascaded dot-refinement
		var obj = {a : {b : 'bombay'} };
		writeln('13. ' + str(obj.a.b === 'bombay'));
	''',
	#	-----------------------------------------------------
	'''	// Test-14: dot & subscript
		var flag = false, obj = {
			x : 'x',
			y : {z : 'king'}
		};
		flag = obj['y'].z === obj.y['z'] && obj.y['z'] === obj.y.z;
		writeln('14. ' + str(flag));
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
		writeln('15. ' + str(obj.a === 'newApple'));
	''',
	#	-----------------------------------------------------
	'''	// Test-16: leading dots (dot-refinements)
		var obj = { // some JSend ...
    		status : "success",
    		data : {
        			"post" : { "id" : 1, "title" : "A blog post", "body" : "Some useful content" }
     				}
		};
		writeln('16. ' + str(obj.data
						  .post.id === 1
						)
			 );
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
			writeln('17. ' + str(flag));
		
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
		writeln('18. ' + str(flag));
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
			writeln('19. ' + str(obj[k]));
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
		writeln('20. ' + str(flag));
	'''
];

j = -1;
for prog in tests:
	j += 1;
	#if j != 20: continue;
	#print 'test     -->\n', t, '\n';
	tokens = lex(prog);
	#print 'tokens   -->\n', tokens, '\n';
	tree = yacc(tokens);
	#print 'tree 	-->\n', tree, '\n';
	rt = Runtime(maxLoopTime=13, maxDepth=100);
	rt.run('', tree = tree);								# rt.run(prog) would work, but tree would be wastefully recomputed
	#if j == 8: break;
	j += 1;
	#break;
