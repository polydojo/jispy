#############################################################################
#                                                                           #
#   Jispy: A JavaScript interpreter in Python                               #
#   Copyright (c) 2017 Polydojo, Inc.                                       #
#                                                                           #
#                                                                           #
#                                                                           #
#   This Source Code Form is subject to the terms of the Mozilla Public     #
#   License, v. 2.0. If a copy of the MPL was not distributed with this     #
#   file, You can obtain one at http://mozilla.org/MPL/2.0/.                #
#                                                                           #
#############################################################################

import re;
import time;
import inspect;
import sys;
import math;
import random;
isa = isinstance;

#############################################################
#                    LEXICAL ANALYSIS                       #
#############################################################

class Name(str): pass;        # for holding identifier names
class Symbol(str): pass;    # for holding keywords and ops

def makeSymbolTable(addLiterals):
    "Creates a symbol table."
    table = {};                # private (via closure)
    if addLiterals is True:
        table = {'true': True, 'false': False, 'null': None};    # Note: hash('x') is the same as hash(Symbol('x'))
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
var if else while for break function return true false null
'''.split();    # list of implemented keywords

uKeywords = '''
case class catch const continue debugger default delete do
export extends finally import in instanceof let new super
switch this throw try typeof void with yield
enum
implements package protected static interface private public
Infinity NaN undefined
'''.split();    # list of unimplemented keywords (and globals)

keywords = iKeywords + uKeywords;

sym = makeSymbolTable(addLiterals = True); # true, false, null
map(sym, iKeywords);
map(sym, list('()[]!*/%+-><=,;{:}'));
map(sym, '>= <= === !== && ||'.split());
map(sym, '+= -='.split());
# Note: '.' (dot) is not a symbol

badsym = makeSymbolTable(addLiterals = False);
map(badsym, '== != << >> *= /= %= ++ --'.split());
map(badsym, uKeywords);
#############################################################

class LJErr(Exception): pass;
class LJSyntaxErr(LJErr): pass;
class LJTypeErr(LJErr): pass;
class LJRuntimeErr(LJErr): pass;
class LJReferenceErr(LJErr): pass;
class LJKeyErr(LJErr): pass;
class LJIndexErr(LJErr): pass;
class LJAssertionErr(LJErr): pass;

def isNameLike(s):
    "Returns if a token is name-LIKE. 'if' IS name like."
    if s == '_' or s == '$': return True;
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
    tokens = []; # Output. Filled by enclosed functions.
    
    ###    
    def segmentifyLine(s):
        "Helps segmentify() with segmenting a single line." # segmentifyLine() uses an FSM which looks as follows:
        mode = 'code'; quote = None;                        #
        ans = [''];                                         #           .--> (CODE) <--> STRING
        for i in range(len(s)):                            #
            if mode == 'code' and quote is None:            # CODE is the start state and the only accepting state.
                if s[i] in ['"', "'"]:
                    mode = 'string';
                    quote = '"' if s[i] == '"' else "'";
                    ans.append(quote);
                elif s[i] == '/' and i + 1 < len(s) and s[i+1] == '/':
                    return ans;
                else:
                    ans[-1] += s[i];
            elif mode == 'string' and quote in ['"', "'"]:  # A segment is a un-quoted code snippet
                prev = ans[-1][-1];                         #   or a quoted-string snippet.
                ans[-1] += s[i];
                if s[i] == quote and prev != '\\':
                    mode = 'code';
                    ans.append('');
                    quote = None;
            else:
                assert False;
        if mode != 'code':
            raise LJSyntaxErr('EOL while scanning string literal');
        return ans;
    
    def segmentify(s):
        "Segments input into code-segements & string-segments."
        segments = [];
        for line in s.splitlines():
            if line and not line.isspace():
                segments += segmentifyLine(line);
        return segments;
    
    def isPropertyName(s):
        "Helps subscriptify() tell if `s` is a valid key."  # TODO: Currently, `a = {}; a.function = 1;` is legal; 
        return re.findall(r'\w+', s) == [s];                #        BUT, `a = {function : 1};` is illegal. FIX THIS.
    
    def subscriptify(s):
        "Helps handleDot() change dots to subscripts."
        if isPropertyName(s):
            toAppend = [sym('['), s, sym(']')];
            map(tokens.append, toAppend);
        else:
            raise LJSyntaxErr('illegal refinement ' + s);
    
    def handleDot(x):
        "Converts dot-refinements to subscript-refinements."    # The parser cannot handle dot-refinements (yet);
        if x[-1] == '.':
            raise LJSyntaxErr('unexpected trailing . (dot) ' + x);      # TODO: Support trailing dots.
        elif x[0] == '.':
            if tokens == []:
                raise LJSyntaxErr('unexpected refinement ' + x);
            # otherwise...
            poken = tokens[-1]; # previous token
            if not (poken in '})]' or isValidName(poken)):          # Note: `in` is weaker than `is`.
                raise LJSyntaxErr('unexpected token ' + x + poken); # Thus,
            # otherwise...                                          #      poken in [sym('}'), sym(')'), sym(']')]
            splitLi = x[1 : ].split('.');                           #   is not used.
            map(subscriptify, splitLi);
        else: # if x[0] != '.'
            splitLi = x.split('.');
            baseId = splitLi[0]; # base/first identifier
            if isValidName(baseId):
                tokens.append(Name(baseId))
                map(subscriptify, splitLi[1 : ]);
            else:
                raise LJSyntaxErr('unexpected token ' + baseId);
    
    def atomizeNS(x):
        "Identify (& return) bools, numbers, strings & names."
        if x in uKeywords:
            raise LJSyntaxErr('unexpected keyword ' + x);
        elif x in badsym:
            raise LJSyntaxErr('unexpected token ' + x);
        elif x in sym: 
            tokens.append(sym(x));
        elif isValidName(x):
            tokens.append(Name(x)); 
        else:
            try: 
                tmp = float(x);
                if isDecimal(x): tokens.append(tmp);
                else:
                    raise LJSyntaxErr('illegal (octal) number ' + x);
            except ValueError:                                # SyntaxError is left uncaught.
                if '.' in x: 
                    handleDot(x);
                else:
                    raise LJSyntaxErr('unexpected token ' + x);
    
    def lexNS(code):
        "Tokenizes a non-string, i.e. un-quoted code snippet."
        for tup in spacer:
            code = code.replace(tup[0], tup[1]);
        map(atomizeNS, code.split());
        
    def lexS(s):
        "Shaves off quotes and decodes backslash escapes."
        assert s[0] == s[-1] and s[-1] in ['"', "'"];
        tokens.append(s[1 : -1].encode().decode('unicode_escape'));
    
    for seg in segmentify(s):
        if seg.startswith('"') or seg.startswith("'"):
            lexS(seg);
        else:
            lexNS(seg);
    return [sym('var?')] + tokens;                             # UNINTERNED symbol, indicating that a var statement may follow.

#############################################################
#                    SYNTACTIC ANALYSIS                     #
#############################################################

def eMsgr(li):
    "Helps print error messages."
    err_repr = lambda x: '' if x == 'var?' else lj_repr(x);
    return ' ... ' + ' '.join(map(err_repr, li[:20]));

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
    raise LJSyntaxErr('unbalanced bracket' + eMsgr(seq[i:]));

def topSplit(li, symbo):                                        # Consider: `add(1, sub(2, 3));`
    "Splits input list on the TOP-LEVEL non-bracket symbol."    # The comma right after 2 is not a top-level comma. (Its nested.)
    if not li: return li; # empty list;                         # On the other hand, the comma right after 1 is.
    oBrackets = [sym('('), sym('{'), sym('[')];
    ans = [];
    i, j = 0, 0;
    while j < len(li):
        if li[j] in oBrackets:
            j = gmb(li, j);    # ignore commas in bracket pairs
        elif li[j] is symbo:
            ans.append(li[i : j]);
            i, j = j+1, j+1;
        elif j == len(li) - 1:
            ans.append(li[i : j + 1]);
            break;
        else:
            j += 1;
    return ans;

def isTopIn(li, symbo):
    "Tells if symbo is a top-level-symbol in list li."
    return len(topSplit(li, symbo)) != 1;

def topIndex(li, j, symbo):    # error thrower                    # Bugfix:
    "Gives index of TOP-LEVEL occurence of symbo, starting at j." # Originally, topIndex accepted a list of symbols `syms` to
    oBrackets = [sym('('), sym('{'), sym('[')];                   # to split on. If a non-list x was passed, it'd set syms = [x].
    if symbo in oBrackets:                                        # Splitting was accomplished by checking `if li[j] in syms`
        raise Exception('');    # internal error                  # as opposed to the current check `if li[j] is symbo`
    while j < len(li):                                            # The `in` test is insufficient as it cannot tell the difference
        if li[j] in oBrackets:                                    #     between types str and Symbol. The `is` test is necessary.
            j = gmb(li, j);    # ignore semis in bracket pairs    # Luckily, topSplit was always called on a single symbol.
        elif li[j] is symbo:                                      # The bug was thus, easily fixed by changing the test is `is`.
            return j;
        else:
            j += 1;
    raise LJSyntaxErr('expected ' + symbo + eMsgr(li));

#############################################################

class Function(object):        # for holding function values  # Functions can be completely parsed during sytactic analysis.
    def __init__(self, params, tree, iTokens):                # There is no need to wait for interpreting.
        self.params = params;                                 # This is not true about literal objects and arrays.
        self.tree = tree;                                     
        self.iTokens = iTokens;
        self.crEnv = None;    # creation ENVironment          # However, the crEnv of a function can be know only at rumtime.
    def __str__ (self):                                      # So, for now, we set it to None;
        return '...function %s %s...' % \
                    (str(self.params), str(self.tree));
    __repr__ = __str__     # uncomment for debugging

def yacc(tokens):
    "Builds an AST from a list of tokens. (Syntactic Analysis)"
    tree = []; # AST (Abstract Syntax Tree)
    def parseFunction(expLi, k):                            # form:        ... function ( a , b )  { ... } ...
        "Helps parseExp() to parse function expressions."   # indices:         k        lp         rp lc      rc
        try:
            lp = expLi.index(sym('('), k);
            assert lp == k + 1;
            rp = gmb(expLi, lp);
            lc = expLi.index(sym('{'), rp);
            assert lc == rp + 1;
            rc = gmb(expLi, lc);
            assert rc > lc + 1; # ensuring non-empty block
            paramsWithCommas = expLi[lp+1 : rp];            # Do _NOT_ to call topSplit(), as each param _MUST_ be a Name
            params = [];
            for p in paramsWithCommas:
                if isa(p, Name): params.append(p);
                else: assert p == sym(',');
        except (ValueError, AssertionError):
            #print 'func ExpLI = ', expLi;
            raise LJSyntaxErr('bad function literal');
        iTokens = [sym('var?')] + expLi[lc + 1 : rc];    # list of body tokens (non-alias)
        func = Function(params, yacc(iTokens), iTokens);
        expLi = expLi[ : k] + [func] + expLi[rc + 1 : ];    # DO NOT DIRECTLY RETURN THE RHS EXPRESSION. It is less readable.
        return expLi;                                       # Substitute an instance of Function in place of function literal
    
    def parseExp(expLi):
        "Tells functions from rest and parses them."        # Remaining parts in an expression like operators etc.            
        while True:                                            #    are dealt with during interpreting
            #print 'expLi = ', expLi, '\n';
            funky = map(lambda x: x is sym('function'), expLi);
            #print ; print;
            #print 'expLi = ', expLi;
            #print 'funky = ', funky;
            #print ; print;
            if any(funky):                                  # Do NOT use `while sym("function") in expLi`
                k = funky.index(True);                      #     as the `in` operator cannot tell the difference between
                expLi = parseFunction(expLi, k);            #     'function' the Symbol and "function" the str.
            else:
                break;
        return expLi;

    def parseVar(tokens, j):                                # form:        ... var a = 10 , b = 20 ; ...
        "Helps yacc() in parsing var statements."           # indices:         j                   semiPos
        if j == 0 or tokens[j - 1] != sym('var?'):
            raise LJSyntaxErr('unexpected var statement');   # In JS, var statements may occur anywhere.
        semiPos = topIndex(tokens, j, sym(';'));             # This may create an illusion of block-scope, which JS lacks.
        subtokens = tokens[j+1 : semiPos];                   # As a remedy, Jispy allows at most one var statement per scope,
        inits = topSplit(subtokens, sym(','));               #    and, if used, it must be the very first statement in the scope.
        for init in inits:                                   # The uninterned symbol `var?` is used to restrict var statements.
            try:
                assert len(init) >= 3;                       # eg. init:     a  =  10  +  10
                assert type(init[0]) is Name;                # indices:   0  1  2   3  4 
                assert init[1] is sym('=');
            except AssertionError:
                raise LJSyntaxErr('illegal var statement');
            rhsParsedExp = parseExp(init[2 : ]);
            tree.append(['init', init[0], rhsParsedExp]);
        return semiPos + 1;

    def parseIf(tokens, j, tree=tree, stmtName = 'if'):     # form:        ... if ( a == 20 )   { ... } ...
        "Helps yacc(..) in parsing if statements."          # indices:         j  lp        rp  lc    rc
        try:
            lp = tokens.index(sym('('), j);    # left paren    # Note: `while` & `else if` are syntactically similar to pure `if`.
            assert lp == j + 1;                                #        We shall thus use parseIf() to parse `else if` and `while`.
            rp = gmb(tokens, lp);            # right paren     #        In doing so, we mustn't wrongly mutate the AST.
            assert rp > lp + 1;                   # non-empty  #        Instead, a dummy-tree will be passed in to parseIf()
            lc = tokens.index(sym('{'), rp);# left curly
            assert lc == rp + 1;
            rc = gmb(tokens, lc);            # right curly
            assert rc > lc + 1;                # non-empty block
        except (ValueError, AssertionError):
            raise LJSyntaxErr('illegal %s statement' % stmtName);
        cond = parseExp(tokens[lp + 1 : rp]);
        code = yacc(tokens[lc + 1 : rc]);
        tree.append(['if-ladder', cond, code])                # An if-ladder generically represents a any VALID combination
        return rc + 1;                                        #    of if and else constructs. (This obviously includes `else if`.)
    
    def parseElseIf(tokens, j):                               # form:        ... else if ( a !== 0 ) { ... } ...
        "Helps parseElse() in parsing else-if statements."    # index:        j
        tempTree = []; # dummy-tree for passing to parseIf()
        j = parseIf(tokens[:], j+1, tempTree, 'else if');   # The if-ladder, which was created on seeing `if`,
        [_, cond, code] = tempTree[0];                      # is mutated as follows on seeing `else if`:
        tree[-1].append(cond);                              #      [if-ladder cond0 cond0] --> [if-ladder cond0 code0 cond1 code1]
        tree[-1].append(code);                              # Where cond0, code0 were previously seen; cond1, code1 were just seen.
        return j;
    
    def parsePureElse(tokens, j):                             # form:        ... else { ... } ...
        "Helps parseElse() in parsing pure-else stmts."       # indices:         j    lc    rc
        try:
            lc = tokens.index(sym('{'), j);
            assert lc == j + 1;
            rc = gmb(tokens, lc);
        except (ValueError, AssertionError):
            raise LJSyntaxErr('illegal else statement');
        cond = [sym('true')];    # alwyas truthy.         # The if-ladder, (which was previously created,)
        code = yacc(tokens[lc+1 : rc]);                   # is mutated by adding a condition which is always true:
        tree[-1].append(cond);                            #     [if-ladder cond0 code0 ] --> [if-ladder cond0 code0 TrueCond code1]
        tree[-1].append(code);                            # TrueCond is always true, which makes pure `else`,
        return rc + 1;                                    #     the semantic equivalent of `else if (true)`.
    
    def parseElse(tokens, j):                             # Relies on parseElseIf() and parsePureElse() above.
        "Helps yacc() in parsing else statements."        
        if tree == [] or tree[-1][0] != 'if-ladder':
            raise LJSyntaxErr('misplaced else statement');
        if j == len(tokens) - 1 :
            raise LJSyntaxErr('unexpected else (last token)');
        if tokens[j+1] == 'if':
            return parseElseIf(tokens[:], j);
        else:
            return parsePureElse(tokens[:], j);
    
    def parseWhile(tokens, j):                                # form:        ... while ( a > 1 )   { ... } ...
        "Helps yacc() in parsing while statements."           # indices:         j     lp      rp  lc    rc
        tokens[j] = sym('if');    # make while look like if.
        tempTree = [];             # dummy-tree
        j = parseIf(tokens[:], j, tempTree, 'while');        # Note:
        [_, cond, code] = tempTree[0];                       #     param `tokens` supplied to parseWhile is a 
        tree.append(['while', cond, code]);                  #     NON-ALIAS-copy of that supplied to yacc;
        return j;                                            #     We may hence freely make changes in it.        
        
    def parseReturn(tokens, j):                              # form:        ... return 1 + 1 + 1 ; ...
        "Helps yacc() in parsing return statements."         # indices:         j                semiPos
        semiPos = topIndex(tokens, j, sym(';'));
        parsedReturnExp = parseExp(tokens[j+1 : semiPos]);
        tree.append(['return', parsedReturnExp]);
        return semiPos + 1;
    
    def parseBreak(tokens, j):                               # form:        ... break ; ...
        "Helps yacc() in parsing break statements."          # indices:         j     j+1
        try: assert tokens[j + 1] is sym(';');
        except AssertionError:
            raise LJSyntaxErr('expected ; (semicolon) after break');
        tree.append(['break']);
        return j + 2;
    
    def checkLhsExp(expLi):    # expLi is lhsExpLi
        "Helps parseAssign() in checking LHS of assignment."
        try:
            assert len(expLi) >= 1;
            assert type(expLi[0]) is Name;
            if len(expLi) > 1:
                j = -1;    # last index
                while True:
                    assert expLi[j] is sym(']');
                    ls = gmob(expLi, j);                     # Left Square [         gmob() <--> Get Matching Opening Bracket
                    if expLi[ls - 1] is sym(']'):            # cascaded indexing
                        j = ls - 1;                          # Right square ]
                    else:
                        assert ls - 1 == 0;
                        break;
        except AssertionError:
            raise LJTypeErr('illegal LHS in assignment' + eMsgr(expLi));
        return None;
    
    def parseAssign(stmt, tree=tree): # Relies on checkLhsExp  # form:         a[0] = 1 + b + c ;
        "Helps yacc() in parsing assignment statements."       # indices:     0    eqSign
        try:
            assert type(stmt[0]) is Name;                    # Note: parseAssign() was written when shorthand assignments
            eqSign = stmt.index(sym('='));                   #        were NOT supported. As a result, it doen't (currently)
            lhsExp = parseExp(stmt[ : eqSign]);              #        handle them. A separate function parseShorthandAssign()
            rhsExp = parseExp(stmt[eqSign + 1 : ]);          #        has been written to do so exclusively, which 
            checkLhsExp(lhsExp);                             #        converts a shorthand assignment to an assignment
        except AssertionError:                               #        via parseAssign().
            raise LJTypeErr('illegal LHS in assignment' + eMsgr(stmt));
        tree.append(['assign', lhsExp, rhsExp]);
        return None;
    
    def parseShortAssign(stmt, tree=tree):                     # form:        k[i]    +=    1    ;
        "Helps yacc() in parsing short-hand assignments."      # indices:     0
        assert sym('+=') in stmt or sym('-=') in stmt;
        if sym('+=') in stmt:
            short = sym('+=');
        else:
            short = sym('-=');
        symPos = stmt.index(short);
        xtmt = stmt[: symPos] + [sym('=')] + stmt[symPos+1 :];  # Make the shorthand assignment LOOK LIKE an assignment.
        tempTree = [];    # dummy-tree
        parseAssign(xtmt, tempTree);                            # Checks legality of assignment, and hence of shorhand assignment.
        [_, lhsExp, rhsExp] = tempTree[0];
        pOrM = sym(short[0]);                                   # sym('+') or sym('-'); i.e. Plus or Minus
        rhsExp = lhsExp + [pOrM] + rhsExp;                      # Convertin `lhs += rhs` to `lhs = lhs + rhs`
        tree.append(['assign', lhsExp, rhsExp]);

    def sepForCls(tokens, j):                                 #form:        ... for ( i = 0 ;  i < 10 ; i += 1 )   { ... } ...
        "Helps parseFor() w/ separating sub-clauses in for."  #indices:         j   lp      s1        s2       rp  lc    rc
        try:
            lp = tokens.index(sym('('), j);
            assert lp == j + 1;                               # Notes:
            rp = gmb(tokens, lp);                             #    1. We shall convert the for loop to an equivalent while loop
            assert rp > lp + 1; # ( ..non-empty.. )           #    2. The equivalent while loop of the loop shown above is:
            lc = tokens.index(sym('{'), rp);                  #         ... i = 0 ; while (i < 10) { ... i += 1 } ...
            assert lc == rp + 1;                              #         where `...` is assumend to remain the same.
            rc = gmb(tokens, lc);                             #    3. It is necessary to verify that the increment-clause
            assert rc > lc + 1;    # non-empty block          #         of for `i += 1` is NOT a disruptive statement.
            s1 = tokens.index(sym(';'), lp, rp);              #         It must be an assignment. (Pure JS is less restrictive.)
            s2 = tokens.index(sym(';'), s1 + 1, rp);          #    4. Assignment & increment clauses within (parens of) for
            assert s2 > s1 + 1;                               #         may not include function values; as tokens.index()
            assert sym(';') not in tokens[s2 + 1 : rp];       #         is used as opposed to topIndex(). 
        except (ValueError, AssertionError):
            raise LJSyntaxErr('illegal for statement');
        asgnCl = tokens[lp + 1 : s1];    # ASSiGNment CLause, yet to be parsed
        condCl  = tokens[s1 + 1 : s2];
        incrCl = tokens[s2 + 1 : rp];
        codeCl  = tokens[lc + 1 : rc];
        return (asgnCl, condCl, incrCl, codeCl, rc); # Each clause is yet to be parsed.
    
    def parseForAssignments(asgnClause):
        "Helps in parsing assignment and increment clauses."
        tempTree = [];
        asgns = topSplit(asgnClause, sym(','));
        #print 'split asgns = ', asgns;
        for asg in asgns:
            if sym('=') in asg:
                parseAssign(asg, tempTree);
            elif sym('+=') in asg or sym('-=') in asg:
                parseShortAssign(asg, tempTree);
            else:
                raise LJSyntaxErr('illegal for statement');
        return tempTree;
    
    def parseFor(tokens, j):                            
        "Helps yacc(..) in parsing for stmt (as while)."
        (asgnCl, condCl, incrCl, codeCl, rc) = sepForCls(tokens, j);
        pAsgns = parseForAssignments(asgnCl);                # parsed assignments (from assignment clause)
        pCond = parseExp(condCl);                            # parsed condition
        pIncrs = parseForAssignments(incrCl);                # only for error checking
        pCode = yacc(codeCl) + pIncrs;# + incrCl + [sym(';')]);            # parsed code; the UNPARSED increment clause is appended
        map(tree.append, pAsgns);                            # Assignment is placed before while (in our parse tree)
        tree.append(['while', pCond, pCode]);                # equivalent while loop
        return rc + 1;
    
    def parseExpStmt(stmt):
        "Helps yacc(..) parse exp-stmts like `print('Hi!');`"
        if stmt[0] is sym('function'):
            raise LJSyntaxErr('unexpected token function');    # functions, unless wrapped in parens, are illegal pure-expressions
        tree.append(['exp-stmt', parseExp(stmt)]);
        return None;    
        
    j = 0;
    while j < len(tokens):                                    # Here, we look at the a given token `tok`.
        tok = tokens[j];                                      # If it is special, like 'if', 'var', 'while' etc.,
        if tok is sym('var?'):                                #    we ship all the tokens, along with the index `j`
            j += 1;                                           #    of the current token, to a helper like parseIf()
        elif tok is sym('var'):                               #
            j = parseVar(tokens[:], j);                       # In doing so, we send a non-alias-copy of `tokens`
        elif tok is sym('if'):                                #     by simplying slicing it to all of itself `tokens[:]`.
            j = parseIf(tokens[:], j);                        # Sending a non-alias-copy is important as the helper
        elif tok is sym('else'):                              # may mutate tokens, making debugging difficult (if not impossible).
            j = parseElse(tokens[:], j);                      #
        elif tok is sym('while'):                             # The helper, when its done parsing, returns the index of 
            j = parseWhile(tokens[:], j);                     #    the NEXT token to be considered.
        elif tok is sym('return'):                            #
            j = parseReturn(tokens[:], j);                    # The AST is mutated by the helper function.
        elif tok is sym('break'):                             #     We needn't worry about that here.
            j = parseBreak(tokens[:], j);
        elif tok is sym('for'):
            j = parseFor(tokens[:], j);
        else:
            #print 'current token = ', tok;
            semiPos = topIndex(tokens, j, sym(';'));
            stmt = tokens[j : semiPos];
            if not stmt:
                #pass;
                raise LJSyntaxErr('empty statement');
            #if sym('=') in stmt:
            #    parseAssign(stmt);
            #elif sym('+=') in stmt or sym('-=') in stmt:
            #    parseShortAssign(stmt); 
            if isTopIn(stmt, sym('=')):
                parseAssign(stmt);
            elif isTopIn(stmt, sym('+=')) or isTopIn(stmt, sym('-=')):
                parseShortAssign(stmt);
            else:
                parseExpStmt(stmt);
            j = semiPos + 1;
    return tree;

#############################################################
#                    SEMANTIC ANALYSIS                      #
#############################################################

def gmob(li, i): # GetMatchingOpeningBacket. Cousin of gmb()
    "Get index of left bracket, matching right bracket at i."
    if i < 0: i = len(li) - abs(i);    # allows -ive indexing
    brackets = {
        sym(')'): sym('('),
        sym(']'): sym('['),
        sym('}'): sym('{')#,
    };
    right = li[i];
    left = brackets[right];
    count = 0;
    for j in xrange(i, -1, -1):    # i may be -ive
        if li[j] == right : count += 1;
        elif li[j] == left : count -= 1;
        if count == 0: return j;
    raise LJSyntaxErr('unbalanced bracket ' + right);

#def cloneLi(li):
#    "Creates a NON-ALIAS clone of a (possibly nested) list."
#    ans = [];
#    for elt in li:
#        if type(elt) is list:
#            ans.append(cloneLi(elt));
#        else:
#            ans.append(elt);
#    return ans;

def cloneTree (iTree):
    "";
    oTree = [];
    for iNode in iTree:
        if type(iNode) is Function:
            oNode = Function(*map(cloneTree, [iNode.params, iNode.tree, iNode.iTokens]));
        elif type(iNode) is list:
            oNode = cloneTree(iNode);
        else:
            oNode = iNode;
        oTree.append(oNode);
    return oTree;
cloneLi = cloneTree;    # Backward compatible alias.
            

def isFalsy(val):                                             # Python and JS have (slightly) different ideas of falsehood.
        "Tells if a value is falsy."                          # [] and {} are falsy in python, but truthy is JS.
        if not hasattr(val, '__call__'):
            assert type(val) in [bool, float, str, list, dict, Function, type(None)];
        return val in [False, 0.0, '', None];
    
def isTruthy(val):
        "Tells is a value is truthy."
        return not isFalsy(val);

def makeEnvClass(maxDepth=None): # maxDepth is private
    class Env(dict):
        "Defines a scope/context for execution."
        def __init__(self, params=[], args=[], parent=None):
            if len(params) != len(args): raise Exception();        # internal error
            self.update(zip(params, args));
            self.parent = parent;
            self.isGlobal = (parent is None);
            if self.isGlobal: self.depth = 0;
            else: self.depth = self.parent.depth + 1;
            if maxDepth and self.depth >= maxDepth:
                raise LJRuntimeErr('maximum scope depth exceeded');
            if (self is self.parent):
                raise Exception();    # internal error
        def getEnv(self, key):    # used (mostly) internally
            "Returns environment in which a variable appears."
            d = 'Global' if self.isGlobal else self;
            #print '\nlooking for %s in %s' % (key, d);
            if key in self:
                return self;
            elif not self.isGlobal:
                return self.parent.getEnv(key);
            raise LJReferenceErr('%s is not defined' % key);
        def init(self, key, value):
            "Initializes a variable in the currect environment."
            if key not in self: self[key] = value;
            else:
                raise LJReferenceErr('%s is already defined' % key);
        def assign(self, key, value):
            "Resets the value of a variable in its own environment."
            self.getEnv(key)[key] = value;
        def lookup(self, key):
            "Looks up the value of a variable. (convenience)"
            return self.getEnv(key)[key];
        def makeChild(self, params=[], args=[]):
            "Creates an Env with current Env `self` as parent."
            return Env(params=params, args=args, parent=self);
        def setDepth(self, depth):
            self.depth = depth;
            if maxDepth and self.depth >= maxDepth:
                raise LJRuntimeErr('maximum call depth exceeded');
        #def show(self):
        #    "Helps with debugging."
        #    out = '\n';
        #    for k in self:
        #        if k not in 'type str len keys write writeln'.split():
        #            out += '\t\t%s : %s\n' % (k, self[k]);
        #    return out;
    
    return Env;

class LJJump(Exception):
    def __str__(self):
        return 'unexpected jump statement';
class LJReturn(LJJump): pass;
class LJBreak(LJJump): pass;

def lj_repr(x):
    if x is None: return 'null';
    if type(x) is bool: return 'true' if x else 'false';
    if type(x) is float:
        if x == round(x): return str(int(x));
        else: return str(x);
    if type(x) is str:
        return '"' + x.replace('"', '\\"') + '"'; 
    if type(x) in [Name, Symbol]: return x;
    if type(x) is list:
        if not x: return '[]' # corner case (see shaving)
        out = '[';
        for elt in x: out += lj_repr(elt) + ', ';
        out = out[ : -2]; # shave off trailing ", "
        return out + ']';
    if type(x) is dict:
        if not x: return '{}'; # corner case
        out = '{';
        for k in x: out += lj_repr(k) + ': ' + lj_repr(x[k]) + ', ';
        out = out[ : -2]; # shave off trailing ", "
        return out + '}';
    if type(x) is Function:
        return 'function (' + ', '.join(x.params) + ') { ' + ' '.join(map(lj_repr, x.iTokens[1:])) + ' }';
    if inspect.isfunction(x):
        return 'function () { [native code] }'
    assert False;
#############################################################

def run(tree, env, maxLoopTime=None, writer=None):
    "Executes parsed code in an environment `env`."
    # -------------------------------------------------------
    # *********************************************
    def eval(expLi, env):
        "Evaluates an expression in an environment."
        # - - - - - - - - - - - - - - - - - - - - - - - - - - 
        def setFuncCreationEnvs(expLi):
            "Set the creation Env (crEnv) for all functions."
            for elt in expLi:
                if type(elt) is Function and elt.crEnv == None:    # elt.crEnv may have been previously set due to the recursive
                    elt.crEnv = env;                               #     nature of eval().
            return expLi;                                         # Not required, but all other functions return expLi.
        
        def subNames(expLi):
            "Substitutes identifier names w/ their values."
            #print 'entering subNames, expLi = ', expLi;
            count = 0; # counts { and }
            for j in xrange(len(expLi)):
                tok = expLi[j];
                if tok is sym('{'): count += 1;               # Keys in objects `{a: "apple"}` are NOT substituted
                elif tok is sym('}'): count -= 1;
                elif type(tok) is Name and count == 0:
                    expLi[j] = env.lookup(tok);               # env was passed to eval
            return expLi;
        
        def subObject(expLi, j):                              # form:        ... { ... keyX : valueExpX , keyY : valueExpY ... }
            "Substitutes an object literal w/ a py-dict."     # indices:         j                                             rc
            #print 'entering subObject, expLi = ', expLi;
            rc = gmb(expLi, j);
            inner = expLi[j + 1 : rc];
            pairs = topSplit(inner, sym(','));
            obj = {};
            for pair in pairs:                                # pair form:    keyA :   x + y + factorial ( 5 )
                try:                                          # indices:        0  1   2 3 4 5     6     7 8 9
                    assert len(pair) >= 3;
                    key = pair[0];
                    if type(key) is Name: key = str(key);
                    assert type(key) is str;                 # JS keys MUST be strings. Numbers & booleans are coerced to strings.
                    assert pair[1] is sym(':');
                except AssertionError :
                    raise LJSyntaxErr('illegal object literal' + eMsgr(expLi));
                valueLi = pair[2 : ];
                obj[key] = eval(valueLi, env);
            expLi = expLi[ : j] + [obj] + expLi[rc + 1 : ];
            return expLi;
        
        def subArray(expLi, j):                               # form:        ... [ 1 + 1 + 1 , expB , ... , expN ] ...
            "Substitutes an array literal w/ a py-list."      # indices:        j                                rs
            #print 'entering subArray, expLi = ', expLi;
            rs = gmb(expLi, j);
            inner = expLi[j + 1 : rs];
            expLists = topSplit(inner, sym(','));            # each expression is represented by a py-list of tokens
            arr = [];
            for eLi in expLists:
                try: assert len(eLi) >= 1;                    # try-except used over `if` to maintain consistency.
                except AssertionError:                        # In the future, there may be more assertions.
                    raise LJSyntaxErr('illegal array literal');
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
                    if j == 0:    # corner case (array literal)
                        expLi = subArray(expLi, j);
                    else:
                        pok = expLi[j - 1];    # Previous tOK
                        indexyTypes = [dict, list, str];
                        pokIsIndexy = type(pok) in indexyTypes;
                        if pokIsIndexy or pok in [sym(']'), sym(')')]:
                            pass;    # indexing operation    # indexing operations are handeled by refine(..)
                        else:        # array literal
                            expLi = subArray(expLi, j);
                else:
                    pass;         # ignore other tokens
                j += 1;            # even if expLi changes, incr j by 1
            return expLi;
        
        def refineObject(obj, key):
            "Helps with object refinements."
            if type(key) is not str:
                raise LJTypeErr('object keys must be strings');
            if key not in obj:
                raise LJKeyErr(key);
            return obj[key]; # intermediate result
        
        def refineListy(li, ind):
            "Helps with list and string refinements."
            msg = 'array' if type(li) is list else 'string';
            if type(ind) is not float:
                raise LJTypeErr(msg + ' indices must be numbers ... ' + lj_repr(i));
            elif ind < 0:
                raise LJTypeErr(msg + ' indices must be non-negative ... ' + lj_repr(i));
            elif ind != round(ind):
                raise LJTypeErr(msg + ' indices must integers ... ' + lj_repr(i));
            elif ind >= len(li):
                raise LJIndexErr(msg + ' index out of range ... ' + lj_repr(ind));
            return li[int(ind)];    # intermediate result
        
        def refine(expLi, j):                                # form:        ... <py-dict-or-list> [   10   ] ...
            "Performs a refinement on object/array."         # indices:                          j        rs
            #print 'entering refine, expLi = ', expLi;
            def getRetExpLi(inter):
                return expLi[ :j-1] + [inter] + expLi[rs+1: ];
            ob = expLi[j - 1];    # object, array or string
            assert type(ob) in [dict, list, str];
            rs = gmb(expLi, j);
            if rs == j + 1:
                raise LJSyntaxErr('illegal refinement');
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
                raise LJTypeErr('incorrect no. of arguments ... (%s)' % lj_repr(args)[1:-1]);            
            if func.crEnv is None: raise Exception();           # internal error
            assert func.crEnv is not None;
            newEnv = func.crEnv.makeChild(func.params, args);   # A function is executed in its environ of creation
            newEnv.setDepth(env.depth + 1);                     # Depth of newEnv is changed to invocation_env's depth + 1
            treeClone = cloneTree(func.tree);                   # shields func.tree from being mutated
            #print 'bodyClone = ', bodyClone, '\n';
            try:
                run(treeClone, newEnv, maxLoopTime, writer);
                #print('about to exit invokeFunc...`try` block w/ no return');
            except LJReturn as r:
                #print('in except block of invokeFunc.. due to return, retval = %s' % r.args[0]);
                inter = r.args[0];
                return inter;    # intermediate result
            raise LJTypeErr('non-returning function');
        
        def invokePyFunction(func, args):
            "Helps invoke python's function."
            nParams = len(inspect.getargspec(func)[0]);        # number of parameters
            if len(args) != nParams:
                raise LJTypeErr('incorrect no. of arguments');
            inter = func(*args);
            types = [bool, float, str, list, dict, Function, type(None)];
            if type(inter) in types or inspect.isfunction(inter):
                return inter;    # intermediate result
            #print func;
            raise Exception('non-returning native function');            
                
        def invoke(expLi, j):                                # form:        ... <Function> ( 1, "king", ... , [0] ) ...
            "Helps perform function calls."                  # indices:                    j                      rp
            #print 'entering invoke, expLi = ', expLi;
            def getRetExpLi(inter):
                return expLi[ :j-1] + [inter] + expLi[rp+1:];
            func = expLi[j - 1];
            assert type(func) is Function or inspect.isfunction(func);
            rp = gmb(expLi, j);
            inner = expLi[j + 1 : rp];
            augInner = [sym('[')] + inner + [sym(']')];
            args = subArray(augInner, 0)[0];    # subArray returns an expLi. Here, the returned expLi will contain a single list
            if type(func) is Function:
                inter = invokeFunction(func, args);
            else: # pythonic function
                inter = invokePyFunction(func, args);
            return getRetExpLi(inter);
        
        def solveGroup(expLi, j):                             # form:        ... ( a + b ) ...
            "Helps with parentheses based grouping."          # indices:         j
            #print 'entering solveGroup, expLi = ', expLi;
            rp = gmb(expLi, j);
            inner = expLi[j+1 : rp];
            gVal = eval(inner, env);    # Grouping's Value
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
                    # j = j;         # no increment
                elif tok is sym('(') and j == 0: # corner case
                    expLi = solveGroup(expLi, j);
                    j += 1;
                elif tok is sym('('):
                    prev = expLi[j - 1];
                    if isFunction(prev):
                        expLi = invoke(expLi, j);
                        # j = j;    # no increment
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
                
        def unop(expLi, op, j):                               # form:        ... op value ...    
            "Evaluates a single unary expression like !true." # indices:         j
            #print 'entering unop, expLi = ', expLi;
            try:    
                valExpLi = [expLi[j + 1]];
            except ValueError:
                raise LJSyntaxErr('unexpected unary operator' + op);
            if op is sym('!'):                
                inter = not isTruthy(eval(valExpLi, env));
                expLi = expLi[ : j] + [inter] + expLi[j+2 : ];
            elif op is sym('-'):
                inter = eval(valExpLi, env);
                if type(inter) is not float:
                    raise LJTypeErr('bad operand for unary -');
                expLi = expLi[ : j] + [-inter] + expLi[j+2 : ];
            elif op is sym('+'):
                inter = eval(valExpLi, env);
                if type(inter) in [str, float]:
                    try: interF = float(inter);                # Note: `isDecimal` is not useful here.
                    except ValueError:
                        raise LJTypeErr('bad operand for unary +');
                else:
                    raise LJTypeErr('bad operand for unary +');
                expLi = expLi[ : j] + [interF] + expLi[j+2 : ];
            return expLi;
        
        def indiBinop(a, op, b):
            "Helps binop(..) with type-independent operators."
            #print 'entering indiBinop, expLi = ', expLi;
            isT = isTruthy;                                    # Note: JS and python have different ideas of falsehood
            def eqeqeq(x, y):                                  # Note: In python, `1.0 is 1.0` --> True
                if type(x) != type(y) : return False;          #        But, `a = 1.0; b = 1.0; a is b` --> False
                if type(y) in [bool, float, str, type(None)]:  #        Thus `is` in py is NOT the same as `===` in JS
                    return x == y;
                refTypes = [list, dict, Function];
                assert type(y) in refTypes or inspect.isfunction(y);
                return x is y;
            return {                                        # pythonic switch statement                                
                sym('==='): eqeqeq,
                sym('!=='): lambda x, y: not eqeqeq(x, y),
                sym('&&'): lambda x, y: y if isT(x) else x,
                sym('||'): lambda x, y: x if isT(x) else y#,
            }[op](a, b);
        
        def strNumBinop(a, op, b):
            "Helps binop(..) with string and number operations."
            #print 'entering strNumBinop, expLi = ', expLi;
            return {                                        
                sym('>='): lambda x, y: x >= y,            # Note:    `1 < "king"` is `True` in python but `false` in JS
                sym('<='): lambda x, y: x <= y,            #    Thus, type equality IS necessary for meaningful use of these ops.
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
                sym('%'): lambda x, y: x % y,                # Note: `+` is dealt with in strNumBinop
                sym('-'): lambda x, y: x - y#,
            }[op](a, b);
        
        def checkChaining(expLi, op, j):                        # On Chromium,
            nonAsso = map(sym, '> < >= <= === !=='.split());    #                 1 === 1 === 1    -->        false
            if j + 2 >= len(expLi): return;                     # because,
            op2 = expLi[j + 2];                                 #                1 === 1          -->        true
            rawMsg = 'operators %s and %s cannot be chained';   #                true === 1         -->        false
            if op in nonAsso and op2 in nonAsso:                # Also,
                op2 = expLi[j + 2];                             #                1 > 1 < 1        -->        true
                msg = rawMsg % (op, op2);                       # because,
                if op == op2:                                   #                1 > 1            -->        false
                    msg = 'operator %s cannot be chained' % op; #                false < 1        -->        true
                raise LJSyntaxErr(msg);                         #
            else: pass;                                         # We shall not be a part of this madness!!
        
        def binop(expLi, op, j):                                # form:        ... value0 op value1 ...
            "Evaluates a single binary expression like 1 + 1."  # indices:                j
            #print 'entering binop, expLi = ', expLi;
            def getRetExpLi(inter):
                return expLi[ : j-1] + [inter] + expLi[j+2 : ];              j
            try:
                assert j > 0;
                a = expLi[j - 1];    # first operand
                b = expLi[j + 1];    # second operand
            except (AssertionError, IndexError):
                raise LJSyntaxErr('unexpected operator ' + op);
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
            raise LJTypeErr('bad operands for binary ' + op + eMsgr(expLi));
        
        def allUnary(expLi):
            "Evaluates all unary expressions in expLi."
            # UNARY (right to left)
            j = len(expLi) - 1;            
            while j >= 0:
                if expLi[j] is sym('!'):
                    expLi = unop(expLi, sym('!'), j);
                elif expLi[j] is sym('-'):
                    if j == 0 or type(expLi[j - 1]) != float:
                        expLi = unop(expLi, sym('-'), j);
                    else: pass;    # binary subtraction
                elif expLi[j] is sym('+'):
                    #if j == 0 or type(expLi[j - 1]) not in [float, str]:
                    if j == 0 or type(expLi[j - 1]) is Symbol:
                        expLi = unop(expLi, sym('+'), j);
                    else: pass; # binary addition
                else: pass;        # ignore token
                j -= 1;
            return expLi;
            
        def allBinary(expLi):
            "Evaluates all binary expressions in expLi."
            # BINARY (left-to-right):
            precedence = [
                [sym('*'), sym('/'), sym('%')],             # Note: ['*', '/', '%'] would also work just fine.
                [sym('+'), sym('-')],                       # Because, in Python
                [sym('>='), sym('<='), sym('>'), sym('<')], # ``` class S(str): pass;
                [sym('==='), sym('!==')],                   #     s = S('king');  
                [sym('&&')],                                #     s == 'king'; # ==> True
                [sym('||')]#,
            ];
            for level in precedence:
                #print expLi, level;
                j = 0;
                while j < len(expLi):
                    if expLi[j] in level and type(expLi[j]) is Symbol:
                        expLi = binop(expLi, expLi[j], j);
                        #j = j; do not increment!!
                    else:
                        j += 1;
                if len(expLi) == 1: break;
            return expLi;
    
        def simpleEval(expLi):                              # TODO: remove this function.
            "Evaluates unary and binary operations."
            return(allBinary(allUnary(expLi)));
        # - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
        None;                                                #print 'incomming expLi = ', expLi, '\n';
        expLi = setFuncCreationEnvs(expLi);
        expLi = subNames(expLi);                             #print'leaving subNames, expLi = ', expLi, '\n';
        expLi = subObjsAndArrs(expLi);                       #print'leaving subObjsAndArrs, expLi = ', expLi, '\n';
        expLi = refine_invoke_and_group(expLi);              #print'leaving r_i_and_g, expLi = ', expLi, '\n';
        expLi = simpleEval(expLi);                           #print'leaving simpleEval, expLi = ', expLi, '\n';
        oldLen = len(expLi);                                 #print 'oldLen (first) = ', oldLen, '\n';
        while len(expLi) != 1:
            expLi = simpleEval(expLi);
            newLen = len(expLi);
            if oldLen > newLen:
                oldLen = newLen;
            else:
                errStr = ' '.join(map(str, expLi));
                raise LJErr('illegal expression' + eMsgr(expLi));
        # having finished looping...
        ans = expLi[0];
        LJTypes = [bool, float, str, list, dict, Function, type(None)];
        if not (type(ans) in LJTypes or inspect.isfunction(ans)):
            raise LJTypeErr('illegal expression (of unknown type)');
        return ans;    # end eval(..)                

    # *********************************************
    def runInit(stmt, env):
        "Helps exec an init `var a = 10;` statement."
        [_, name, expLi] = stmt;
        #print 'pre init ', stmt, ' env = ', env.show();
        env.init(name, eval(expLi, env));
        #print 'post init ', stmt, ' env = ', env.show();
    
    def runIfLadder(stmt, env):
        "Helps run through an if-ladder."
        for j in xrange(1, len(stmt), 2):
            expLi, code = stmt[j], stmt[j+1];
            if isTruthy(eval(expLi, env)):
                run(code, env, maxLoopTime, writer);
                break;
                        
    def runWhile(stmt, env):
        "Helps run a while loop."
        [_, expLi, code] = stmt;
        #print 'while cond = ', expLi, ' & env = ', env.show();
        t1 = time.time();
        while isTruthy(eval(expLi[:], env)):                # expLi[:] is eqvt. to cloneLi(expLi) as expLi is flat (non-nested).
            try: run(cloneLi(code), env, maxLoopTime, writer);        # Cloning shields while's code-block from mutation
            except LJBreak: break;
            if maxLoopTime and time.time() - t1 > maxLoopTime:
                raise LJRuntimeErr('looping for to long');
    
    def runReturn(stmt, env):
        "Emulates return statement."
        [_, expLi] = stmt;
        #tmp = eval(expLi, env);
        #print ('runReturn... returning ...' + str(tmp));
        raise LJReturn(eval(expLi, env));    
    
    def runNameAssign(stmt, env):
        "Helps runAssign(..) in executing simple assignments."
        #print 'nameAssign, ', stmt;
        [_, [name], rExpLi] = stmt;
        env.assign(name, eval(rExpLi, env));
    
    def runObjArrAssign(stmt, env):
        "Helps runAssign(..) w/ assignments to object keys."
        [_, lExpLi, rExpLi] = stmt
        rhsExp = eval(rExpLi, env);
        ls = gmob(lExpLi, -1);         # Last Square Bracket  # form of lExpLi:     a [ "foo" ]  [  1  ] ..  [      0       ] 
        part1 = lExpLi[ : ls];                                # indices:            0                        ls            -1
        part2 = lExpLi[ls + 1 : -1]                           # parts:              <--------part1--------->   <---part2--->
        objarr = eval(part1, env);    # obj or arr
        innexp = eval(part2, env);    # inner exp
        if [type(objarr), type(innexp)] == [dict, str]:
            objarr[innexp] = rhsExp;
        elif [type(objarr), type(innexp)] == [list, float]:
            eval(lExpLi, env);        # checks range and roundness
            objarr[int(innexp)] = rhsExp;
        else:    # Note: strings are immutable
            raise LJTypeErr('illegal LHS in assignment' + eMsgr(stmt));
    
    def runAssign(stmt, env):
        "Helps exec variable assignment."
        [_, lExpLi, _] = stmt;
        #print 'pre runAssign, ', stmt, ' env = ', env.show();
        if len(lExpLi) == 1:
            runNameAssign(stmt, env);
        else:
            runObjArrAssign(stmt, env);
        #print 'pre runAssign, ', stmt, ' env = ', env.show();
    
    def runExpStmt(stmt, env):
        'Helps eval exp-stmts like `writeln("Hi!");`'
        [_, expLi] = stmt;
        ans = eval(expLi, env);
        if writer and ans != None and env.isGlobal:
            writer(lj_repr(ans) + '\n');
        return ans;
    
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
            raise LJBreak();                            # too simple for a function
        elif stmt[0] == 'assign':
            runAssign(stmt, env);
        elif stmt[0] == 'exp-stmt':
            runExpStmt(stmt, env);

#############################################################
def inbuilts(writer):
    "Adds built-in functions like type(), len(), keys() etc."
    # n_ in the following functions/variables indicates NATIVE
    def n_str(x):
        "Returns the string form of input."
        if type(x) is str: return x;
        return lj_repr(x); 
    
    def n_print(x):
        "Default output function."
        if writer: writer(n_str(x) + '\n');
        else: raise LJReferenceErr('print is not defined');
        return None; # null
    
    def n_type(x):
        "Returns the string name of LJ type."
        if inspect.isfunction(x): return 'function';
        return { # pythonic switch
            bool:    'boolean',    float:         'number',
            str:    'string',    list:        'array',
            dict:    'object',    Function:    'function',
            type(None): 'null'#,
        }[type(x)];            
    
    def n_len(x):
        "Returns length of LJ strings, arrays and objects."
        if type(x) in [str, list, dict]: return float(len(x));
        raise LJTypeErr('%s has no len(): %s' % (n_type(x), x));
    
    def n_keys(dicty):
        "Returns an array of keys in an object `obj`."
        if type(dicty) is dict: return dicty.keys();
        raise LJTypeErr('%s has no keys()' % n_type(dicty));
        
    def n_del(x, y):
        "Deletes from an object or array."
        if [type(x), type(y)] == [dict, str]:
            if y in x:
                x.pop(y); 
                return True;
            raise LJKeyErr('del() called with non-existent key');
        if [type(x), type(y)] == [list, float]:
            if y == round(y) and 0 <= y < len(x):
                x.pop(int(y));
                return True;
            raise LJIndexErr('invalid array index passed to del()');
        raise LJTypeErr('bad call to del()');
    
    def n_append(li, elt):
        if type(li) is list: li.append(elt);
        else: raise LJTypeErr('cannot append() to non-array');
        return float(len(li));
            
    def n_assert(exp, msg):
        "Python-like assert via assert(). Replaces `throw`."
        if isTruthy(exp): return None; # null
        raise LJAssertionErr(n_str(msg));
    
    def n_ord(c):
        if type(c) is str and len(c) == 1: return float(ord(c));
        raise LJTypeErr('non-character supplied to ord()');
    
    def n_chr(i):
        if not (type(i) is float and i == round(i)):
            raise LJTypeErr('chr() requires an integer');
        if not (i < 256):
            raise LJErr('chr() arg not less than 256');
        return chr(int(i));
    
    def isF(*args):
        "Helps f() check that each argument passed is float."
        if all(type(n) is float for n in args):
            return True;
        raise LJTypeErr('methods of math accept numbers only');
    
    def fm(func, n): # fm <--> Function Math
        "Creates a mathy function that calls `func` with `n` args."
        if n == 0:
            return lambda: func();                            # Creating a lambda is required, as all native functions must 
        if n == 1:                                            #    be USER DEFINED.
            return lambda x: func(x) if isF(x) else None;     # Thus, we may return `lambda x: abs(x)` but not `abs`;
        if n == 2:
            return lambda x, y: func(x, y) if isF(x, y) else None;
        raise Exception(); # internal error
    
    e = math.e;
    n_math = {
        'E': e, 'PI': math.pi, 'LN10': math.log(10.0, e), 
        'LN2': math.log(2.0, e), 'LOG2E': math.log(e, 2.0), 
        'LOG10E': math.log(e, 10.0), 'SQRT1_2': math.sqrt(0.5),
        'SQRT2': math.sqrt(2.0),'abs': fm(abs, 1),
        'acos': fm(math.acos, 1), 'asin': fm(math.asin, 1),
        'atan': fm(math.atan, 1), 'atan2': fm(math.atan2, 2),
        'ceil': fm(math.ceil, 1), 'cos': fm(math.cos, 1), 
        'exp': fm(math.exp, 1), 'floor': fm(math.floor, 1),
        'log': lambda x: math.log(x, e) if isF(x) else None,
        'max': lambda arr: max(arr) if isF(*arr) else None,
        'min': lambda arr: min(arr) if isF(*arr) else None,
        'pow': fm(pow, 2), 'random': fm(random.random, 0),
        'round': fm(round, 1), 'sin': fm(math.sin, 1),
        'sqrt': fm(math.sqrt, 1), 'tan': fm(math.tan, 1)#,
    };
    
    loDict = locals();
    output = {};
    if not writer:
        loDict.pop('n_write');
        loDict.pop('n_writeln');
    for key in loDict:
        if key.startswith('n_'):
            name = Name(key[2 : ]);     # shave off 'n_'
            output[name] = loDict[key];
    return output;

def addNatives(env, dicty):
    "Adds to the environment env."
    okTypes = [bool, float, str, list, dict, Function, type(None)]        # py-function excluded
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
    
    def __init__(self, maxLoopTime=None, maxDepth=None, writer=sys.stdout.write):
        "Initializes a Runtime, which has a single global Env."
        self.gEnv = makeEnvClass(maxDepth)();
        self.writer = writer;
        addNatives(self.gEnv, inbuilts(self.writer));
        self.maxDepth = maxDepth;
        self.maxLoopTime = maxLoopTime;
    
    def addNatives(self, dicty):
        "Adds native functions to the Runtimes' global Env."
        addNatives(self.gEnv, dicty);
    
    def run(self, prog, env=None, console=False): # console <--> isInConsoleMode?
        "Runs a program in any  environment `env`."
        try:
            if env is None: env = self.gEnv;                    # We cannot use `run(.. env=self.gEnv ..)` as `self` is not defined
            tree = None; # parse tree                           # at the time of evaluating arguments. This is a work-around.
            if type(prog) is list:
                tree = prog;
            elif type(prog) is str and prog.endswith('.l.js'):
                with open(prog) as f:
                    tree = yacc(lex(f.read()));
            elif type(prog) is str:
                tree = yacc(lex(prog));
            else:
                raise TypeError('bad input to Runtime.run()');
            writer = self.writer if console else None;
            run(tree, env, self.maxLoopTime, writer);
        except LJErr as e:
            print('%s: %s' % (type(e).__name__[2:] + 'or' , e))
        except LJJump as e:
            if isa(e, LJReturn):
                print('SyntaxError: unexpected return statement');
            elif isa(e, LJBreak):
                print('SyntaxError: unexpected break statement');
            else:
                raise e; # unexpected
    
    def runG(self, prog, console=False):                            # Note: run(prog) and runG(prog) 
        "Runs the program in the Runtime's global environment."     #       have exactly the same effect.
        self.run(prog, env=self.gEnv, console=console);             # But the second is more explicit,
                                                                    #       and hence preferable.
    def runC(self, prog, console=False):
        "Runs program in a child of Runtimes' global environment."
        self.run(prog, env=self.gEnv.makeChild(), console=console);
    
    def runX(self, prog, console=False):
        tmpRT = Runtime(self.maxDepth, self.maxLoopTime, self.writer);
        tmpRT.runG(prog, console);

def console(rt=None, semify=False, prompt='LJ> '):       # semify __tries__ to auto-appends semicolons (as required)
    "This is REPL-like, but not really a REPL."
    original_prompt = prompt;
    if not rt: rt = Runtime();                              # Don't put rt=Runtime() as a default argument.
    inp = '';                                               #  If you do so, runtime will not be renewed on each call to console();
    while True:
        inp += '\n';
        try: inp += input(prompt) ;
        except (EOFError):
            print('');
            return;
        if not inp.endswith('\t'):
            tmp = inp;    inp = '';
            if not semify: pass;
            elif tmp.endswith(';') or tmp.endswith('}'): pass;
            else: tmp += ';';
            rt.run(tmp, console=True);
            prompt = original_prompt
        else:
            prompt = '.' * (len(prompt) - 1) + ' ' ;
            pass; # continue;

if __name__ == '__main__':
    console();
        
############################################################
