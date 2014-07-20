#############################################################
#			Jispy: JavaScript Interpreter in Python			#
#				(c) Sumukh Barve, 2014;         			#
#############################################################

import re;
import time;
import json;	 	# used repr of arrs and objs
import inspect;
import sys;
isa = isinstance;

#############################################################
#					LEXICAL ANALYSIS						#
#############################################################

class Name(str): pass;		# for holding identifier names
class Symbol(str): pass;	# for holding keywords and ops

def makeSymbolTable(addBools):
	"Creates a symbol table."
	table = {};				# private (via closure)
	if addBools is True:
		table = {'true': True, 'false': False};	# private
	class SymbolTable(object):
		def __call__(self, s):
			if s not in table:
				table[s] = Symbol(s);
			return table[s];
		def __contains__(self, s):
			return s in table;
		def __repr__(self):
			return str(table);
	return SymbolTable();


iKeywords = '''
var if else while for break function return true false
'''.split();	# list of implemented keywords

uKeywords = '''
case class catch const continue debugger default delete do
export extends finally import in instanceof let new super
switch this throw try typeof void with yield
enum
implements package protected static interface private public

Infinity NaN undefined null
'''.split();	# list of unimplemented keywords (and globals)

keywords = iKeywords + uKeywords;

sym = makeSymbolTable(addBools = True); # true, false
map(sym, iKeywords);
map(sym, list('()[]!*/%+-><=,;{:}'));
map(sym, '>= <= === !== && ||'.split());
map(sym, '+= -='.split());
# Note: '.' (dot) is not a symbol

badsym = makeSymbolTable(addBools = False);
map(badsym, '== != << >> *= /= %= ++ --'.split());
map(badsym, uKeywords);
#############################################################

def isNameLike(s):
	"Returns if a token is name-LIKE. 'if' IS name like."
	return re.findall(r'[a-z]\w*', s) == [s] and s[-1] != '_';

def isValidName(s):
	"Returns if a token is a valid identifier name."
	return s not in keywords and isNameLike(s);

def strNum(n):
	"Converts floats to (possibly int-like) strings."
	return str(int(n)) if n == round(n) else str(n);

def isDecimal(s):
	"Checks if a number-token is decimal (non-octal)."
	if s == '0' or any(map(s.startswith, '0e 0E 0.'.split())):
		return True;
	return not s.startswith('0');
	
def lex(s):
	"Breaks input into a list of tokens. (Lexical Analysis)"
	spacer = [
		# Introducing spaces:
		('=', ' = '), (',', ' , '), (';', ' ; '),
		('(', ' ( '), ('[', ' [ '), ('{', ' { '),
		(')', ' ) '), (']', ' ] '), ('}', ' } '),
		('!', ' ! '), ('*', ' * '), ('/', ' / '),
		('%', ' % '), ('+', ' + '), ('-', ' - '),
		('>', ' > '), ('<', ' < '), (':', ' : '),
		('&&', ' && '), ('||', ' || '),
		# Removing unwanted spaces:
		('>  =', '>='), ('<  =', '<='),
		('=  =  =', '==='), ('!  =  =', '!=='),
		('+  =', '+='), ('-  =', '-='),
		# Bad (EVIL) symbols (these raise syntax errors):
		('=  =', '=='), ('!  =', '!='),
		('+  +', '++'), ('-  -', '--'),
		('>  >', '>>'), ('<  <', '<<'),
		('*  =', '*='), ('/  =', '/='), ('%  =', '%=')#, 
	];
	
	pat = r'''"(?:[^"\\]|(?:\\.))*"|'(?:[^'\\]|(?:\\.))*'|[^"']*''';
	matches = re.findall(pat, s + '\n');
	tokens = [];
	
	def handleDot(x):
		"Works with dot-refinement(s)"
		
		def subscriptify(s):
			"Helps change dots-refinements to subscripts."
			if isNameLike(s):
				toAppend = [sym('['), s, sym(']')];
				map(tokens.append, toAppend);
			else:
				raise SyntaxError('illegal refinement ' + x);
						
		if x[-1] == '.':
			raise SyntaxError('unexpected trailing . (dot) ' + x);		# TODO: Support trailing dots.
		elif x[0] == '.':
			if tokens == []:
				raise SyntaxError('unexpected refinement ' + x);
			# otherwise...
			poken = tokens[-1]; # previous token
			if poken not in [sym('}'), sym(']')]:
				raise SyntaxError('unexpected token ' + x);
			# otherwise...
			splitLi = x[1 : ].split('.');
			map(subscriptify, splitLi);
		else: # if x[0] != '.'
			splitLi = x.split('.');
			baseId = splitLi[0]; # base/first identifier
			if isValidName(baseId):
				tokens.append(Name(baseId))
				map(subscriptify, splitLi[1 : ]);
			else:
				raise SyntaxError('illegal identifier ' + baseId);
	
	def atomizeNS(x):
		"Identify (& return) bools, numbers, st & names."
		if x in uKeywords:
			raise SyntaxError('unexpected keyword ' + x);
		elif x in badsym:
			raise SyntaxError('unexpected token ' + x);
		elif x in sym: 
			tokens.append(sym(x));
		elif isValidName(x):
			tokens.append(Name(x)); 
		else:
			try: 
				tmp = float(x);
				if isDecimal(x): tokens.append(tmp);
				else:
					raise SyntaxError('illegal number ' + x);
			except ValueError:								# SyntaxError is left uncaught.
				if '.' in x: 
					handleDot(x);
				else:
					raise SyntaxError('unexpected token ' + x);
	
	def lexNS(code):
		"Tokenizes a non-string, i.e. un-quoted code snippet."
		for tup in spacer:
			code = code.replace(tup[0], tup[1]);
		map(atomizeNS, code.split());
		
	def lexS(s):
		"Shaves off quotes and decodes backslash escapes."
		assert s[0] == s[-1] and s[-1] in ['"', "'"];
		tokens.append(s[1 : -1].decode('string_escape'));
	
	j = 0;
	while j < len(matches):
		m = matches[j];
		if m.startswith('"') or m.startswith("'"):
			lexS(m);
		else:
			while '//' in m:
				start = m.index('//');
				while '\n' not in m[start : ]:
					j += 1;
					m += matches[j]; # append next match;
				end = m.index('\n', start);
				m = m[ : start] + m[end : ];
				#if 'var obj' not in m: assert 1 == 0;
			lexNS(m);
		j += 1;
	return [sym('var?')] + tokens; 							# UNINTERNED symbol, indicating that a var statement may follow.

#############################################################
#					SYNTACTIC ANALYSIS						#
#############################################################

def gmb(seq, i): # Get Matching (Closing) Bracket
	"Get index of right bracket, matching left bracket at i."
	brackets = {
		sym('('): sym(')'),
		sym('['): sym(']'),
		sym('{'): sym('}')#,
	};
	left = seq[i];
	right = brackets[left];
	count = 0;
	for j in xrange(i, len(seq), 1):
		if seq[j] == left: count += 1;
		elif seq[j] == right: count -= 1;
		if count == 0: return j;
	raise SyntaxError('unbalanced bracket ' + left);

def topSplit(li, syms):											# Consider: `add(1, sub(2, 3));`
	"Splits input list on the TOP-LEVEL non-bracket symbol(s)."	# The comma right after 2 is not a top-level comma. (Its nested.)
	if not li: return li; # empty list;							# On the other hand, the comma right after 1 is.
	if type(syms) not in [list, tuple]: syms = [syms];
	oBrackets = [sym('('), sym('{'), sym('[')];
	ans = [];
	i, j = 0, 0;
	while j < len(li):
		if li[j] in oBrackets:
			j = gmb(li, j);	# ignore commas in bracket pairs
		elif li[j] in syms:
			ans.append(li[i : j]);
			i, j = j+1, j+1;
		elif j == len(li) - 1:
			ans.append(li[i : j + 1]);
			break;
		else:
			j += 1;
	return ans;

def topIndex(li, j, symbo):	# error thrower
	"Gives index of TOP-LEVEL occurence of symbo, starting at j." 
	oBrackets = [sym('('), sym('{'), sym('[')];
	while j < len(li):
		if li[j] in oBrackets:
			j = gmb(li, j);	# ignore semis in bracket pairs
		elif li[j] is symbo:
			return j;
		else:
			j += 1;
	raise SyntaxError('expected ' + symbo);

#############################################################

class Function(object):		# for holding function values	# Functions can be completely parsed during sytactic analysis.
	def __init__(self, params, body):						# There is no need to wait for interpreting.
		self.params = params;								# This is not true about literal objects and arrays.
		self.body = body;
	def __str__ (self):
		return '...function %s %s...' % \
					(str(self.params), str(self.body));
	__repr__ = __str__ 	# uncomment for debugging

def yacc(tokens):
	"Builds an AST from a list of tokens. (Syntactic Analysis)"
	tree = []; # AST (Abstract Syntax Tree)
	
	def parseFunction(expLi, k):							# form:		... function ( a , b )  { ... } ...
		"Helps parseExp() to parse function expressions."	# indices:		k		 lp		 rp lc	  rc
		try:
			lp = expLi.index(sym('('), k);
			assert lp == k + 1;
			rp = gmb(expLi, lp);
			lc = expLi.index(sym('{'), rp);
			assert lc == rp + 1;
			rc = gmb(expLi, lc);
			assert rc > lc + 1; # ensuring non-empty block
			paramsWithCommas = expLi[lp+1 : rp];			# Do _NOT_ to call topSplit(), as each param _MUST_ be a Name
			params = [];
			for p in paramsWithCommas:
				if isa(p, Name): params.append(p);
				else: assert p == sym(',');
		except (ValueError, AssertionError):
			#print 'func ExpLI = ', expLi;
			raise SyntaxError('bad function literal');
		bodyTokens = [sym('var?')] + expLi[lc + 1 : rc]; 	# list of body tokens (non-alias)
		func = Function(params, yacc(bodyTokens));
		expLi = expLi[ : k] + [func] + expLi[rc + 1 : ];	# DO NOT DIRECTLY RETURN THE RHS EXPRESSION. It is less readable.
		return expLi;										# Substitute an instance of Function in place of function literal
	
	def parseExp(expLi):
		"Tells functions from rest and parses them."		# Remaining parts in an expression like operators etc.			
		while True:											#	are dealt with during interpreting
			#print 'expLi = ', expLi, '\n';
			funky = map(lambda x: x is sym('function'), expLi);
			#print ; print;
			#print 'expLi = ', expLi;
			#print 'funky = ', funky;
			#print ; print;
			if any(funky):									# Do NOT use `while sym("function") in expLi`
				k = funky.index(True);						# 	as the `in` operator cannot tell the difference between
				expLi = parseFunction(expLi, k);			# 	'function' the Symbol and "function" the str.
			else:
				break;
		return expLi;

	def parseVar(tokens, j):								# form:		... var a = 10 , b = 20 ; ...
		"Helps yacc() in parsing var statements."			# indices:		j          			semiPos
		if j == 0 or tokens[j - 1] != sym('var?'):
			raise SyntaxError('unexpected var statement');	# In JS, var statements may occur anywhere.
		semiPos = topIndex(tokens, j, sym(';'));			# This may create an illusion of block-scope, which JS lacks.
		subtokens = tokens[j+1 : semiPos];					# As a remedy, Jispy allows at most one var statement per scope,
		inits = topSplit(subtokens, sym(','));				#	and, if used, it must be the very first statement in the scope.
		for init in inits:									# The uninterned symbol `var?` is used to restrict var statements.
			try:
				assert len(init) >= 3;						# eg. init:	 a  =  10  +  10
				assert type(init[0]) is Name;				# indices:   0  1  2   3  4 
				assert init[1] is sym('=');
			except AssertionError:
				raise SyntaxError('illegal var statement');	# TODO: Currently, `var i = 0, i += 1` raises "illegal var statement".
			rhsParsedExp = parseExp(init[2 : ]);			#		Should it raise "i is already defined"?
			tree.append(['init', init[0], rhsParsedExp]);
		return semiPos + 1;

	def parseIf(tokens, j, tree=tree, stmtName = 'if'):		# form:		... if ( a == 20 )   { ... } ...
		"Helps yacc(..) in parsing if statements."			# indices:		j  lp        rp  lc    rc
		try:
			lp = tokens.index(sym('('), j);	# left paren	# Note: `while` & `else if` are syntactically similar to pure `if`.
			assert lp == j + 1;								#		We shall thus use parseIf() to parse `else if` and `while`.
			rp = gmb(tokens, lp);			# right paren	#		In doing so, we mustn't wrongly mutate the AST.
			assert rp > lp + 1;		   		# non-empty		#		Instead, a dummy-tree will be passed in to parseIf()
			lc = tokens.index(sym('{'), rp);# left curly
			assert lc == rp + 1;
			rc = gmb(tokens, lc);			# right curly
			assert rc > lc + 1;				# non-empty block
		except (ValueError, AssertionError):
			raise SyntaxError('illegal %s statement' % stmtName);
		cond = parseExp(tokens[lp + 1 : rp]);
		code = yacc(tokens[lc + 1 : rc]);
		tree.append(['if-ladder', cond, code])				# An if-ladder generically represents a any VALID combination
		return rc + 1;										#	of if and else constructs. (This obviously includes `else if`.)
	
	def parseElseIf(tokens, j):								# form:		... else if ( a !== 0 ) { ... } ...
		"Helps parseElse() in parsing else-if statements."	# index:		j
		tempTree = []; # dummy-tree for passing to parseIf()
		j = parseIf(tokens[:], j+1, tempTree, 'else if');	# The if-ladder, which was created on seeing `if`,
		[_, cond, code] = tempTree[0];						# is mutated as follows on seeing `else if`:
		tree[-1].append(cond);								# 	 [if-ladder cond0 cond0] --> [if-ladder cond0 code0 cond1 code1]
		tree[-1].append(code);								# Where cond0, code0 were previously seen; cond1, code1 were just seen.
		return j;
	
	def parsePureElse(tokens, j):							# form:		... else { ... } ...
		"Helps parseElse() in parsing pure-else stmts."		# indices:		j    lc    rc
		try:
			lc = tokens.index(sym('{'), j);
			assert lc == j + 1;
			rc = gmb(tokens, lc);
		except (ValueError, AssertionError):
			raise SyntaxError('illegal else statement');
		cond = [sym('true')];	# alwyas truthy.			# The if-ladder, (which was previously created,)
		code = yacc(tokens[lc+1 : rc]);						# is mutated by adding a condition which is always true:
		tree[-1].append(cond);								# 	[if-ladder cond0 code0 ] --> [if-ladder cond0 code0 TrueCond code1]
		tree[-1].append(code);								# TrueCond is always true, which makes pure `else`,
		return rc + 1;										# 	the semantic equivalent of `else if (true)`.
	
	def parseElse(tokens, j):								# Relies on parseElseIf() and parsePureElse() above.
		"Helps yacc() in parsing else statements."		
		if tree == [] or tree[-1][0] != 'if-ladder':
			raise SyntaxError('misplaced else statement');
		if j == len(tokens) - 1 :
			raise SyntaxError('unexpected else (last token)');
		if tokens[j+1] == 'if':
			return parseElseIf(tokens[:], j);
		else:
			return parsePureElse(tokens[:], j);
	
	def parseWhile(tokens, j):								# form:		... while ( a > 1 )   { ... } ...
		"Helps yacc() in parsing while statements."			# indices:		j     lp      rp  lc    rc
		tokens[j] = sym('if');	# make while look like if.
		tempTree = []; 			# dummy-tree
		j = parseIf(tokens[:], j, tempTree, 'while');		# Note:
		[_, cond, code] = tempTree[0];						# 	param `tokens` supplied to parseWhile is a 
		tree.append(['while', cond, code]);					# 	NON-ALIAS-copy of that supplied to yacc;
		return j;											# 	We may hence freely make changes in it.		
		
	def parseReturn(tokens, j):								# form:		... return 1 + 1 + 1 ; ...
		"Helps yacc() in parsing return statements."		# indices:		j				 semiPos
		semiPos = topIndex(tokens, j, sym(';'));
		parsedReturnExp = parseExp(tokens[j+1 : semiPos]);
		tree.append(['return', parsedReturnExp]);
		return semiPos + 1;
	
	def parseBreak(tokens, j):								# form:		... break ; ...
		"Helps yacc() in parsing break statements."			# indices:		j	  j+1
		try: assert tokens[j + 1] is sym(';');
		except AssertionError:
			raise SyntaxError('semicolon expected after break');
		tree.append(['break']);
		return j + 2;
	
	def checkLhsExp(expLi):	# expLi is lhsExpLi
		"Helps parseAssign() in checking LHS of assignment."
		try:
			assert len(expLi) >= 1;
			assert type(expLi[0]) is Name;
			if len(expLi) > 1:
				j = -1;	# last index
				while True:
					assert expLi[j] is sym(']');
					ls = gmob(expLi, j);					# Left Square [ 		gmob() <--> Get Matching Opening Bracket
					if expLi[ls - 1] is sym(']'): 			# cascaded indexing
						j = ls - 1;							# Right square ]
					else:
						assert ls - 1 == 0;
						break;
		except AssertionError:
			raise SyntaxError('illegal LHS in assignment');
		return None;
	
	def parseAssign(stmt, tree=tree): # Relies on checkLhsExp 		# form:		 a[0] = 1 + b + c ;
		"Helps yacc() in parsing assignment statements."			# indices:	 0    eqSign     -1
		try:
			assert type(stmt[0]) is Name;					# Note: parseAssign() was written when shorthand assignments
			eqSign = stmt.index(sym('='));					#		were NOT supported. As a result, it doen't (currently)
			lhsExp = parseExp(stmt[ : eqSign]);				#		handle them. A separate function parseShorthandAssign()
			rhsExp = parseExp(stmt[eqSign + 1 : ]);			#		has been written to do so exclusively, which 
			checkLhsExp(lhsExp);							#		converts a shorthand assignment to an assignment
		except AssertionError:								#		via parseAssign().
			raise SyntaxError('illegal assignment %s' % stmt);
		tree.append(['assign', lhsExp, rhsExp]);
		return None;
	
	def parseShortAssign(stmt, tree=tree):							# form:		k[i]	+=	1	;
		"Helps yacc() in parsing short-hand assignments."			# indices:	0				-1
		assert sym('+=') in stmt or sym('-=') in stmt;
		if sym('+=') in stmt:
			short = sym('+=');
		else:
			short = sym('-=');
		symPos = stmt.index(short);
		xtmt = stmt[: symPos] + [sym('=')] + stmt[symPos+1 :];	# Make the shorthand assignment LOOK LIKE an assignment.
		tempTree = [];	# dummy-tree
		parseAssign(xtmt, tempTree); 							# Checks legality of assignment, and hence of shorhand assignment.
		[_, lhsExp, rhsExp] = tempTree[0];
		pOrM = sym(short[0]); 									# sym('+') or sym('-'); i.e. Plus or Minus
		rhsExp = lhsExp + [pOrM] + rhsExp;						# Convertin `lhs += rhs` to `lhs = lhs + rhs`
		tree.append(['assign', lhsExp, rhsExp]);
	
	def parseFor(tokens, j):								#form:		... for ( i = 0 ;  i < 10 ; i += 1 )   { ... } ...
		"Helps yacc(..) in parsing for stmt (as while)."	#indicces:		j   lp      s1        s2       rp  lc    rc
		try:
			lp = tokens.index(sym('('), j);
			assert lp == j + 1;								# Notes:
			rp = gmb(tokens, lp);							#	1.	We shall convert the for loop to an equivalent while loop
			assert rp > lp + 1; # ( ..non-empty.. ) 		# 	2.	The equivalent while loop of the loop shown above is:
			lc = tokens.index(sym('{'), rp);				#			... i = 0 ; while (i < 10) { ... i += 1 } ...
			assert lc == rp + 1;							#		where `...` is assumend to remain the same.
			rc = gmb(tokens, lc);							#	3.	It is necessary to verify that the increment-clause
			assert rc > lc + 1;	# non-empty block			#			of for `i += 1` is NOT a disruptive statement.
			s1 = tokens.index(sym(';'), lp, rp);			#		It must be an assignment. (Pure JS is less restrictive.)
			s2 = tokens.index(sym(';'), s1 + 1, rp);
			assert s2 > s1 + 1;
			assert sym(';') not in tokens[s2 + 1 : rp];
		except (ValueError, AssertionError):
			raise SyntaxError('illegal for statement');
		asg1 = tokens[lp + 1 : s1]; # yet to be parsed		# TODO: Decompose this function into easily __readable__ chunks.
		cond = parseExp(tokens[s1 + 1 : s2]); # __parsed__	#		It seems to be doing just too much by itself.
		asg2 = tokens[s2 + 1 : rp]; # yet to be parsed
		code = tokens[lc + 1 : rc]; # yet to be parsed
		tempTree = [];
		for asg in [asg1, asg2]:	# parsing assignments	# We are parsing asg2 only to verify that its an assignment stmt.
			if sym('=') in asg:
				parseAssign(asg, tempTree);
			elif sym('+=') in asg or sym('-=') in asg:
				parseShortAssign(asg, tempTree);
			else:
				raise SyntaxError('illegal for statement');
		[pAsg1, pAsg2] = tempTree;	# parsed assignments
		code = yacc(code + asg2 + [sym(';')]); 				# parsed code; the UNPARSED increment-assignment is appended
		tree.append(pAsg1);									# initial-assignment is perormed only once
		tree.append(['while', cond, code]);					# equivalent while loop (after the initial-assigment is done) 
		return rc + 1;
	
	def parseExpStmt(stmt):
		"Helps yacc(..) parse exp-stmts like `print('Hi!');`"
		tree.append(['exp-stmt', parseExp(stmt)]);
		return None;	
		
	j = 0;
	while j < len(tokens):									# Here, we look at the a given token `tok`.
		tok = tokens[j];									# If it is special, like 'if', 'var', 'while' etc.,
		if tok is sym('var?'):								#	we ship all the tokens, along with the index `j`
			j += 1;											#	of the current token, to a helper like parseIf()
		elif tok is sym('var'):								#
			j = parseVar(tokens[:], j);						# In doing so, we send a non-alias-copy of `tokens`
		elif tok is sym('if'):								# 	by simplying slicing it to all of itself `tokens[:]`.
			j = parseIf(tokens[:], j);						# Sending a non-alias-copy is important as the helper
		elif tok is sym('else'):							# may mutate tokens, making debugging difficult (if not impossible).
			j = parseElse(tokens[:], j);					#
		elif tok is sym('while'):							# The helper, when its done parsing, returns the index of 
			j = parseWhile(tokens[:], j);					#	the NEXT token to be considered.
		elif tok is sym('return'):							#
			j = parseReturn(tokens[:], j);					# The AST is mutated by the helper function.
		elif tok is sym('break'):							# 	We needn't worry about that here.
			j = parseBreak(tokens[:], j);
		elif tok is sym('for'):
			j = parseFor(tokens[:], j);
		else:
			#print 'current token = ', tok;
			semiPos = topIndex(tokens, j, sym(';'));
			stmt = tokens[j : semiPos];
			if not stmt:
				raise SyntaxError('empty statement');
			if sym('=') in stmt:
				parseAssign(stmt);
			elif sym('+=') in stmt or sym('-=') in stmt:
				parseShortAssign(stmt); 
			else:
				parseExpStmt(stmt);
				#raise SyntaxError('unrecognized statement');
			j = semiPos + 1;
	return tree;


#############################################################
#					SEMANTIC ANALYSIS						#
#############################################################

def gmob(li, i): # GetMatchingOpeningBacket. Cousin of gmb()
	"Get index of left bracket, matching right bracket at i."
	if i < 0: i = len(li) - abs(i);	# allows -ive indexing
	brackets = {
		sym(')'): sym('('),
		sym(']'): sym('['),
		sym('}'): sym('{')#,
	};
	right = li[i];
	left = brackets[right];
	count = 0;
	for j in xrange(i, -1, -1):	# i may be -ive
		if li[j] == right : count += 1;
		elif li[j] == left : count -= 1;
		if count == 0: return j;
	raise SyntaxError('unbalanced bracket ' + right);

def cloneLi(li):
	"Creates a NON-ALIAS clone of a (possibly nested) list."
	ans = [];
	for elt in li:
		if type(elt) is list:
			ans.append(cloneLi(elt));
		else:
			ans.append(elt);
	return ans;

def isFalsy(val):											# Python and JS have (slightly) different ideas of falsehood.
		"Tells if a value is falsy."						# [] and {} are falsy in python, but truthy is JS.
		if not hasattr(val, '__call__'):
			assert type(val) in [bool, float, str, list, dict, Function];
		return val in [False, 0.0, ''];
	
def isTruthy(val):
		"Tells is a value is truthy."
		return not isFalsy(val);

def makeEnvClass(maxDepth=None): # maxDepth is private
	class Env(dict):
		"Defines a scope/context for execution."
		def __init__(self, params=[], args=[], parent=None):
			self.update(zip(params, args));
			self.parent = parent;
			self.isGlobal = (parent is None);
			if self.isGlobal: self.depth = 0;
			else: self.depth = self.parent.depth + 1;
			if maxDepth and self.depth >= maxDepth:
				raise RuntimeError('maximum scope depth exceeded');
			if (self is self.parent):
				raise Exception();	# internal error
		def getEnv(self, key):	# used (mostly) internally
			"Returns environment in which a variable appears."
			#print 'getEnv on ', self;
			if key in self:
				return self;
			elif not self.isGlobal:
				return self.parent.getEnv(key);
			raise ReferenceError('%s is not defined' % key);
		def init(self, key, value):
			"Initializes a variable in the currect environment."
			if key not in self: self[key] = value;
			else:
				raise ReferenceError('%s is already defined' % key);
		def assign(self, key, value):
			"Resets the value of a variable in its own environment."
			self.getEnv(key)[key] = value;
		def lookup(self, key):
			"Looks up the value of a variable. (convenience)"
			return self.getEnv(key)[key];
	
	return Env;
	
class ReturnStatement(Exception): pass;
class BreakStatement(Exception): pass;
#############################################################

def run(tree, env, maxLoopTime=None):
	"Executes parsed code in an environment `env`."
	# -------------------------------------------------------
	# *********************************************
	def eval(expLi, env):
		"Evaluates an expression in an environment."
		# - - - - - - - - - - - - - - - - - - - - - - - - - - 
		def subNames(expLi):
			"Substitutes identifier names w/ their values."
			#print 'entering subNames, expLi = ', expLi;
			count = 0; # counts { and }
			for j in xrange(len(expLi)):
				tok = expLi[j];
				if tok is sym('{'): count += 1;				# Keys in objects `{a: "apple"}` are NOT substituted
				elif tok is sym('}'): count -= 1;
				elif type(tok) is Name and count == 0:
					expLi[j] = env.lookup(tok);				# env was passed to eval
			return expLi;
		
		def subObject(expLi, j):							# form:		... { ... keyX : valueExpX , keyY : valueExpY ... }
			"Substitutes an object literal w/ a py-dict."	# indices:		j											  rc
			#print 'entering subObject, expLi = ', expLi;
			rc = gmb(expLi, j);
			inner = expLi[j + 1 : rc];
			pairs = topSplit(inner, sym(','));
			obj = {};
			for pair in pairs:								# pair form:	keyA :   x + y + factorial ( 5 )
				try:										# indices:		0	 1   2 3 4 5 6         7 8 9
					assert len(pair) >= 3;
					key = pair[0];
					if type(key) is Name: key = str(key);
					assert type(key) is str;				# JS keys MUST be strings. Numbers & booleans are coerced to strings.
					assert pair[1] is sym(':');
				except AssertionError :
					raise SyntaxError('bad object literal');
				valueLi = pair[2 : ];
				obj[key] = eval(valueLi, env);
			expLi = expLi[ : j] + [obj] + expLi[rc + 1 : ];
			return expLi;
		
		def subArray(expLi, j):								# form:		... [ 1 + 1 + 1 , expB , ... , expN ] ...
			"Substitutes an array literal w/ a py-list."	# indices:		j					   			rs
			#print 'entering subArray, expLi = ', expLi;
			rs = gmb(expLi, j);
			inner = expLi[j + 1 : rs];
			expLists = topSplit(inner, sym(','));			# each expression is represented by a py-list of tokens
			arr = [];
			for eLi in expLists:
				try:
					assert len(eLi) >= 1;
				except AssertionError:
					raise SyntaxError('bad array literal');
				arr.append(eval(eLi, env));
			expLi = expLi[ : j] + [arr] + expLi[rs + 1 : ];
			return expLi;
		
		def subObjsAndArrs(expLi):
			"Substitute literal objects and arrays."
			#print 'entering sOA, expLi = ' + expLi;
			j = 0;
			while j < len(expLi):
				tok = expLi[j];
				if tok is sym('{'):
					expLi = subObject(expLi, j);
				elif tok is sym('['):
					if j == 0:	# corner case (array literal)
						expLi = subArray(expLi, j);
					else:
						pok = expLi[j - 1];	# Previous tOK
						indexyTypes = [dict, list, str];
						pokIsIndexy = type(pok) in indexyTypes;
						if pokIsIndexy or pok in [sym(']'), sym(')')]:
							pass;	# indexing operation	# indexing operations are handeled by refine(..)
						else:		# array literal
							expLi = subArray(expLi, j);
				else:
					pass; 		# ignore other tokens
				j += 1;			# even if expLi changes, incr j by 1
			return expLi;
		
		def refineObject(obj, key):
			"Helps with object refinements."
			if type(key) is not str:
				raise TypeError('object keys must be strings');
			if key not in obj:
				raise KeyError(key);
			return obj[key]; # intermediate result
		
		def refineListy(li, ind):
			"Helps with list and string refinements."
			msg = 'array' if type(li) is list else 'string';
			if type(ind) is not float:
				raise TypeError(msg + ' indices must be numbers');
			elif ind < 0:
				raise TypeError(msg + ' indices must be non-negative');
			elif ind != round(ind):
				raise TypeError(msg + ' indices must integers');
			elif ind >= len(li):
				raise IndexError(msg + ' index out of range');
			return li[int(ind)];	# intermediate result
		
		def refine(expLi, j):								# form:		... <py-dict-or-list> [   10   ] ...
			"Performs a refinement on object/array."		# indices:						  j        rs
			#print 'entering refine, expLi = ', expLi;
			def getRetExpLi(inter):
				return expLi[ :j-1] + [inter] + expLi[rs+1: ];
			ob = expLi[j - 1];	# object, array or string
			assert type(ob) in [dict, list, str];
			rs = gmb(expLi, j);
			if rs == j + 1:
				raise SyntaxError('bad refinement');
			inner = expLi[j + 1 : rs];
			ki = eval(inner, env); # short for Key/Index
			if type(ob) is dict:
				inter = refineObject(ob, ki);
			else: # ob in [list, str]: (see assert)
				inter = refineListy(ob, ki);
			return getRetExpLi(inter);
			
		
		def invokeFunction(func, args):
			"Helps invokes non-native functions."
			if len(args) != len(func.params):
				raise TypeError('incorrect no. of arguments');			
			Env = type(env);								# has same maxDepth
			newEnv = Env(func.params, args, env);			# functions have their own scope
			bodyClone = cloneLi(func.body);					# shields func.body from being mutated
			try:
				run(bodyClone, newEnv);
			except ReturnStatement as r:
				inter = r.args[0];
				return inter;	# intermediate result
			raise RuntimeError('non-returning function');
		
		def invokePyFunction(func, args):
			"Helps invoke python's function."
			nParams = len(inspect.getargspec(func)[0]);		# number of parameters
			if len(args) != nParams:
				raise TypeError('incorrect no. of arguments');
			inter = func(*args);
			types = [bool, float, str, list, dict, Function];
			if type(inter) in types or inspect.isfunction(inter):
				return inter;	# intermediate result
			raise Exception('non-returning native function');			
				
		def invoke(expLi, j):								# form:		... <Function> ( 1, "king", ... , [0] ) ...
			"Helps perform function calls."					# indices:				   j                      rp
			#print 'entering invoke, expLi = ', expLi;
			def getRetExpLi(inter):
				return expLi[ :j-1] + [inter] + expLi[rp+1:];
			func = expLi[j - 1];
			assert type(func) is Function or inspect.isfunction(func);
			rp = gmb(expLi, j);
			inner = expLi[j + 1 : rp];
			augInner = [sym('[')] + inner + [sym(']')];
			args = subArray(augInner, 0)[0];	# subArray returns an expLi. Here, the returned expLi will contain a single list
			if type(func) is Function:
				inter = invokeFunction(func, args);
			else: # pythonic function
				inter = invokePyFunction(func, args);
			return getRetExpLi(inter);
		
		def solveGroup(expLi, j):								# form:		... ( a + b ) ...
			"Helps with parentheses based grouping."		# indices:		j
			#print 'entering solveGroup, expLi = ', expLi;
			rp = gmb(expLi, j);
			inner = expLi[j+1 : rp];
			gVal = eval(inner, env);	# Grouping's Value
			expLi = expLi[ : j] + [gVal] + expLi[rp+1 : ];
			return expLi;
			
		def refine_invoke_and_group(expLi):
			"Performs refinements and invocations."
			#print 'entering r_i_and_g, expLi = ', expLi;
			entered = cloneLi(expLi);
			j = 0;
			def isFunction(x) :
				return type(x) is Function or inspect.isfunction(x);
			while j < len(expLi):
				tok = expLi[j];
				if tok is sym('['):
					expLi = refine(expLi, j);
					# j = j; 		# no increment
				elif tok is sym('(') and j == 0: # corner case
					expLi = solveGroup(expLi, j);
					j += 1;
				elif tok is sym('('):
					prev = expLi[j - 1];
					if isFunction(prev):
						expLi = invoke(expLi, j);
						# j = j;	# no increment
					else:
						expLi = solveGroup(expLi, j);
						j += 1;
				else:
					j += 1; # ignore other tokens
			if expLi == [['a', 'c', 'b'], [0.0]]:
				pass;
				#print 'entering rig expLi = ', entered;
				#print 'leaving  rig expLi = ', expLi;
			return expLi;
				
		def unop(expLi, op, j):								# form:		... op value ...	
			"Evaluate a unary-operator-using expression."	# indices:		j
			#print 'entering unop, expLi = ', expLi;
			try:	
				valExpLi = [expLi[j + 1]];
			except ValueError:
				raise SyntaxError('unexpected ' + op);
			if op is sym('!'):				
				inter = not isTruthy(eval(valExpLi, env));
				expLi = expLi[ : j] + [inter] + expLi[j+2 : ];
			elif op is sym('-'):
				inter = eval(valExpLi, env);
				if type(inter) is not float:
					raise TypeError('bad operand for unary -');
				expLi = expLi[ : j] + [-inter] + expLi[j+2 : ];
			elif op is sym('+'):
				inter = eval(valExpLi, env);
				if type(inter) is str:
					tmp = float(inter);
					if isDecimal(inter): inter = tmp;
					else:
						raise SyntaxError('bad operand for unary +');
				else:
					raise TypeError('bad operand for unary +');
				expLi = expLi[ : j] + [inter] + expLi[j+2 : ];
			return expLi;
		
		def indiBinop(a, op, b):
			"Helps binop(..) with type-independent operators."
			#print 'entering indiBinop, expLi = ', expLi;
			isT = isTruthy;									# Note: JS and python have different ideas of falsehood
			def eqeqeq(x, y):								# Note: In python, `1.0 is 1.0` --> True
				if type(x) != type(y) : return False;		#		But, `a = 1.0; b = 1.0; a is b` --> False
				if type(y) in [bool, float, str]:			#		Thus `is` in py is NOT the same as `===` in JS
					return x == y;
				assert type(y) in [list, dict];
				return x is y;
			return {										# pythonic switch statement								
				sym('==='): eqeqeq,
				sym('!=='): lambda x, y: not eqeqeq(x, y),
				sym('&&'): lambda x, y: y if isT(x) else x,
				sym('||'): lambda x, y: x if isT(x) else y#,
			}[op](a, b);
		
		def strNumBinop(a, op, b):
			"Helps binop(..) with string and number operations."
			#print 'entering strNumBinop, expLi = ', expLi;
			return {										
				sym('>='): lambda x, y: x >= y,				# Note:	`1 < "king"` is `True` in python but `false` in JS
				sym('<='): lambda x, y: x <= y,				#	Thus, type equality IS necessary for meaningful use of these ops.
				sym('>'): lambda x, y: x > y,
				sym('<'): lambda x, y: x < y,
				sym('+'): lambda x, y: x + y,
			}[op](a, b);
		
		def numBinop(a, op, b):
			"Helps binop(..) with number operations."
			#print 'entering numBinop, expLi = ', expLi;
			return {
				sym('*'): lambda x, y: x * y,
				sym('/'): lambda x, y: x / y,
				sym('%'): lambda x, y: x % y,				# Note: `+` is dealt with in strNumBinop
				sym('-'): lambda x, y: x - y#,
			}[op](a, b);
		
		def checkChaining(expLi, op, j):						# On Chromium,
			nonAsso = map(sym, '> < >= <= === !=='.split());	# 				1 === 1 === 1	-->		false
			if j + 2 >= len(expLi): return;						# because,
			op2 = expLi[j + 2];									#				1 === 1  		-->		true
			rawMsg = 'operators %s and %s cannot be chained';	#				true === 1 		-->		false
			if op in nonAsso and op2 in nonAsso:				# Also,
				op2 = expLi[j + 2];								#				1 > 1 < 1		-->		true
				msg = rawMsg % (op, op2);						# because,
				if op == op2:									#				1 > 1			-->		false
					msg = 'operator %s cannot be chained' % op;	#				false < 1		-->		true
				raise SyntaxError(msg);							#
			else: pass;											# We shall not be a part of this madness!!
		
		def binop(expLi, op, j):							# form:		... value0 op value1 ...
			"Evaluates a binary-operator-using expression." # indices:		       j
			#print 'entering binop, expLi = ', expLi;
			def getRetExpLi(inter):
				return expLi[ : j-1] + [inter] + expLi[j+2 : ];			  j
			try:
				assert j > 0;
				a = expLi[j - 1];	# first operand
				b = expLi[j + 1];	# second operand
			except (AssertionError, IndexError):
				raise SyntaxError('unexpected operator ' + op);
			checkChaining(expLi, op, j);										
			indiOps = map(sym, '=== !== && ||'.split());					
			if op in indiOps:											
				inter = indiBinop(a, op, b);
				return getRetExpLi(inter);
			# otherwise...								
			if type(a) == type(b) and type(b) in [str, float]:
				strNumOps = map(sym, '>= <= > < +'.split());
				if op in strNumOps:
					inter = strNumBinop(a, op, b);
					return getRetExpLi(inter);
				elif type(b) is float:
					numOps = map(sym, list('*/%-'));
					assert op in numOps;
					inter = numBinop(a, op, b);
					return getRetExpLi(inter);
			raise TypeError('bad operands for binary ' + op);
	
		def simpleEval(expLi):
			"Evaluates unary and binary operations."
			#print 'entering simpleEval, expLi = ', expLi;
			# UNARY (right-to-left):
			j = len(expLi) - 1;			
			while j >= 0:
				if expLi[j] is sym('!'):
					expLi = unop(expLi, sym('!'), j);
				elif expLi[j] is sym('-'):
					if j == 0 or type(expLi[j - 1]) != float:
						expLi = unop(expLi, sym('-'), j);
					else: pass;	# binary subtraction
				elif expLi[j] is sym('+'):
					if j == 0 or type(expLi[j - 1]) not in [float, str]:
						expLi = unop(expLi, sym('+'), j);
					else: pass; # binary addition
				else: pass;		# ignore token
				j -= 1;
			# BINARY (left-to-right):
			binSyms = map(sym, list('*/%+-><'));
			binSyms += map(sym, '>= <= === !== && ||'.split());
			# binSyms are arranged in order of precedence
			for op in binSyms:
				j = 0;
				while j < len(expLi):
					if expLi[j] is op:
						expLi = binop(expLi, op, j);
						# j = j; do not increment !!
					else:
						j += 1;
			return expLi;
		
		# - - - - - - - - - - - - - - - - - - - - - - - - - - 
		
		expLi = subNames(expLi);							#print'leaving subNames, expLi = ', expLi, '\n';
		expLi = subObjsAndArrs(expLi);						#print'leaving subObjsAndArrs, expLi = ', expLi, '\n';
		expLi = refine_invoke_and_group(expLi);				#print'leaving r_i_and_g, expLi = ', expLi, '\n';
		expLi = simpleEval(expLi);							#print'leaving simpleEval, expLi = ', expLi, '\n';
		oldLen = len(expLi);								#print 'oldLen (first) = ', oldLen, '\n';
		while len(expLi) != 1:
			expLi = simpleEval(expLi);
			newLen = len(expLi);
			if oldLen > newLen:
				oldLen = newLen;
			else:
				raise SyntaxError('illegal expression <non-shrink>');
		# having finished looping...
		ans = expLi[0];
		if type(ans) not in [bool, float, str, list, dict, Function]:
			raise SyntaxError('illegal expression <type>');		# TODO: remove `<type>` and `<non-shrink>` form error messages
		return ans;	# end eval(..)				

	# *********************************************
	
	def runInit(stmt, env):
		"Helps exec an init `var a = 10;` statement."
		[_, name, expLi] = stmt;
		env.init(name, eval(expLi, env));
	
	def runIfLadder(stmt, env):
		"Helps run through an if-ladder."
		for j in xrange(1, len(stmt), 2):
			expLi, code = stmt[j], stmt[j+1];
			if isTruthy(eval(expLi, env)):
				run(code, env);
				break;
						
	def runWhile(stmt, env):
		"Helps run a while loop."
		[_, expLi, code] = stmt;
		t1 = time.time();
		while isTruthy(eval(expLi[:], env)):				# expLi[:] is eqvt. to cloneLi(expLi) as expLi is flat (non-nested).
			try: run(cloneLi(code), env);					# Cloning shields while's code-block from mutation
			except BreakStatement: break;
			if maxLoopTime and time.time() - t1 > maxLoopTime:
				raise RuntimeError('maximum loop time exceeded');
	
	def runReturn(stmt, env):
		"Emulates return statement."
		[_, expLi] = stmt;
		raise ReturnStatement(eval(expLi, env));	
	
	def runNameAssign(stmt, env):
		"Helps runAssign(..) in executing simple assignments."
		[_, [name], rExpLi] = stmt;
		env.assign(name, eval(rExpLi, env));
	
	def runObjArrAssign(stmt, env):
		"Helps runAssign(..) w/ assignments to object keys."
		[_, lExpLi, rExpLi] = stmt
		rhsExp = eval(rExpLi, env);
		ls = gmob(lExpLi, -1); 		# Last Square Bracket	# form of lExpLi: 	a [ "foo" ]  [  1  ] ..  [      0       ] 
		part1 = lExpLi[ : ls];								# indices:			0                        ls            -1
		part2 = lExpLi[ls + 1 : -1]							# parts:			<--------part1--------->   <---part2--->
		objarr = eval(part1, env);	# obj or arr
		innexp = eval(part2, env);	# inner exp
 		if [type(objarr), type(innexp)] == [dict, str]:
			objarr[innexp] = rhsExp;
		elif [type(objarr), type(innexp)] == [list, float]:
			eval(lExpLi, env);		# checks range and roundness
			objarr[int(innexp)] = rhsExp;
		else:	# Note: strings are immutable
			raise ReferenceError('illegal LHS in assignment');
	
	def runAssign(stmt, env):
		"Helps exec variable assignment."
		[_, lExpLi, _] = stmt;
		if len(lExpLi) == 1:
			runNameAssign(stmt, env);
		else:
			runObjArrAssign(stmt, env);
	
	def runExpStmt(stmt, env):
		'Helps eval exp-stmts like `writeln("Hi!");`'
		[_, expLi] = stmt;
		return eval(expLi, env);
	
	# -------------------------------------------------------

	for stmt in tree:
		#print 'tree-stmt = ', stmt;
		if stmt[0] == 'init':
			runInit(stmt, env);
		elif stmt[0] == 'if-ladder':
			runIfLadder(stmt, env);
		elif stmt[0] == 'while':
			runWhile(stmt, env);
		elif stmt[0] == 'return':
			runReturn(stmt, env);
		elif stmt[0] == 'break':
			raise BreakStatement();							# too simple for a function
		elif stmt[0] == 'assign':
			runAssign(stmt, env);
		elif stmt[0] == 'exp-stmt':
			runExpStmt(stmt, env);

#############################################################
def builtins(write):
	"Adds built-in functions like type(), len(), keys() etc."
	
	def n_str(x):
		if type(x) is bool:
			return 'true' if x else 'false';
		elif type(x) is float:
			if x == round(x): return str(int(x));
			else: return str(x);
		elif type(x) is str: return x;
		elif type(x) in [list, dict]:
			return json.dumps(x);
		elif type(x) is Function or inspect.isfunction(x):
			raise RuntimeError("functions don't have string equivalents");
		raise Exception(); # internal error
	
	def n_write(x):
		if write: write(n_str(x));
		return 0.0;
	
	def n_writeln(x):
		if write: write(n_str(x) + '\n');
		return 0.0;
		
	def n_type(x):
		if inspect.isfunction(x): return 'function';
		return { # pythonic switch
			bool:	'boolean',	float: 		'number',
			str:	'string',	list:		'array',
			dict:	'object',	Function:	'function'#,
		}[type(x)];			
	
	def n_len(x):
		if type(x) in [str, list, dict]: return float(len(x));
		raise TypeError('%s has no len()' % n_type(x));
	
	def n_keys(obj):
		if type(obj) is dict: return obj.keys();
		raise TypeError('%s has no keys()' % n_type(x));
	
	loDict = locals();
	output = {};
	if not write:
		loDict.pop('n_write');
		loDict.pop('n_writeln');
	for key in loDict:
		if key.startswith('n_'):
			name = Name(key[2 : ]);	 # shave off 'n_'
			output[name] = loDict[key];
	return output;

def addNatives(env, dicty):
	"Adds to the environment env."
	okTypes = [bool, float, str, list, dict, Function]		# py-function excluded
	for key in dicty:
		name = Name(key);
		if name in env:
			sys.stdout.write('WARNING!! Conflicting native name ' + name);
		# otherwise...
		if inspect.isfunction(dicty[key]):
			env[name] = dicty[key];
		elif type(dicty[key]) in okTypes:
			env[name] = dicty[key];
		else:
			raise Exception('illegal native ' + key);

#############################################################
class Runtime(object):
	"Represents a context for running (possibly many) programs."
	def __init__(self, maxDepth=None, maxLoopTime=None, write= sys.stdout.write):
		self.gEnv = makeEnvClass(maxDepth)();
		addNatives(self.gEnv, builtins(write));
		self.maxLoopTime = maxLoopTime;
	def addNatives(self, dicty):
		addNatives(self.gEnv, dicty);
	def run(self, prog):
		#tokens = lex(prog);
		#print 'tokens --->\n', tokens;
		#tree = yacc(tokens);
		#print 'tree --->\n', tree;
		run(yacc(lex(prog)), self.gEnv, self.maxLoopTime);

def console(prompt = 'jispy> '):
	"This is REPL-like, but not really a REPL."
	original_prompt = prompt;
	rt = Runtime();
	inp = '';
	write = sys.stdout.write;
	while True:
		inp += '\n';
		try: inp += raw_input(prompt) ;
		except (EOFError):
			sys.stdout.write('\n');
			return;
		if not inp.endswith('\t'):
			tmp = inp;	inp = '';
			try:
				rt.run(tmp);
			except Exception as e:
				print('%s: %s' % (type(e).__name__, e))
			prompt = original_prompt
		else:
			prompt = '.' * (len(prompt) - 1) + ' ' ;
			pass; # continue;
		

#############################################################

