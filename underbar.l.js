var _ = {};
(function () {
    var x = 'tmp', y = 'tmp';
    _.concat = function (u1, u2) {
        var ans = [], i = null; // assumed: u is an _
        if (type(u1) === 'string') { return u1 + u2; }
        for (i = 0; i < len(u1); i += 1) { append(ans, u1[i]); }
        for (i = 0; i < len(u2); i += 1) { append(ans, u2[i]); }
        return ans;
    };
    _.slice = function (u, p1, p2) {
        var ans = [], i = null; // assumed: u is an _
        if (type(u) === 'string') { ans = ''; }
        if (p1 === null) { p1 = 0; }
        else if (p1 < 0) { p1 = len(u) + p1; }
        if (p2 === null) { p2 = len(u); }
        else if (p2 < 0) { p2 = len(u) + p2; }
        for (i = p1; i < p2; i += 1) {
            if (type(u) === 'array') { append(ans, u[i]); }
            else { ans += u[i]; }
        }
        return ans;
    };
    _.from = function (u, p1) { return _.slice(u, p1, null); };
    _.upto = function (u, p2) { return _.slice(u, null, p2); };
    _.indexOf = function (u, tgt, pos) {
        var i = null;
        if (pos === null) { pos = 0; }
        else if (pos < 0) { pos = len(u) + pos; }
        if (type(u) === 'array') {
            for (i = pos; i < len(u); i += 1) {
                if (u[i] === tgt) { return i; }
            }
        } else { // assumend: u is a string
            for (i = pos; i <= len(u) - len(tgt); i += 1) {
                if (_.slice(u, i, i + len(tgt)) === tgt) {
                    return i;
                }
            }
        }
        return -1;
    };
    _.index = function (u, tgt) { return _.indexOf(u, tgt, null); };
    _.lastIndexOf = function (u, tgt, pos) {
        var i = null;
        if (pos === null) { pos = len(u) - 1; }
        if (pos < 0) { pos = len(u) + pos; }
        if (type(u) === 'array') {
            for (i = pos; i >= 0; i -= 1) {
                if (u[i] === tgt) { return i; }
            }
        } else {
            for (i = pos; i >= len(tgt) -1; i -= 1) {
                if(_.slice(u, i - len(tgt) + 1, i + 1) === tgt) {
                    return i - len(tgt) + 1;
                }
            }
        }
        return -1;
    };
    _.rindex = function (u, tgt) { return _.lastIndexOf(u, tgt, null); };
    _.replace = function (s, old, rep) {
        var i = null;
        while (true) {
            i = _.index(s, old);
            if (i === -1) { break; }
            s = _.upto(s, i) + rep + _.from(s, i+1);
        }
        return s;
    };
    _.split = function (s, sep) {
        var ans = [], i = null;
        if (sep === '') {
            for (i = 0; i < len(s); i += 1) { append(ans, s[i]); }
            return ans;
        }
        while(true) {
            i = _.index(s, sep);
            if (i === -1) {
                append(ans, s);
                return ans;
            }
            append(ans, _.upto(s, i));
            s = _.from(s, i + 1);
        }
    };
    _.splitN = function (s, sep, n) { return _.upto(_.split(s, sep), n); };
    _.toLowerCase = function (s) {
        var ans = '', i = null,
            ordA = ord('A'), ordZ = ord('Z'), ordI = null;
        for (i = 0; i < len(s); i += 1) {
            ordI = ord(s[i]);
            if (ordA <= ordI && ordI <= ordZ) {
                ans += chr(ordI + 32);
            } else { ans += s[i]; }
        }
        return ans;
    };
    _.lower = _.toLowerCase;
    _.toUpperCase = function (s) {
        var ans = '', i = null,
            ord_a = ord('a'), ord_z = ord('z'), ord_i = null;
        for (i = 0; i < len(s); i += 1) {
            ord_i = ord(s[i]);
            if (ord_a <= ord_i && ord_i <= ord_z) {
                ans += chr(ord_i - 32);
            } else { ans += s[i]; }
        }
        return ans;
    };
    _.upper = _.toUpperCase;
    
    // TODO: write _.trim (String.prototype.trim.call)
    
    _.join = function (a, sep) {
        var ans = '', i = null;
        for (i = 0; i < len(a) - 1; i += 1) {
            ans += str(a[i]) + sep;
        }
        return ans + str(a[i]);
    };
    _.pop = function (a) {
        var ans = a[len(a) - 1];
        del(a, len(a) - 1);
        return ans;
    };
    _.push = append;
    _.reverse = function (a) {
        var i = null, tmp = null;
        for (i = 0; i < len(a) / 2; i += 1) {
            tmp = a[i];
            a[i] = a[len(a) - 1 - i];
            a[len(a) - 1 - i] = tmp;
        }
        return a;
    };
    _.shift = function (a) {
        var ans = a[0];
        del(a, 0);
        return ans;
    };
    _.unshift = function (a, elt) {
        append(_.reverse(a), elt);
        return len(_.reverse(a));
    };
    _.sort = function (a, f) {
        var i = null, j = null, tmp = null;
        if (f === null) {
            f = function (m, n) {
                if (m <= n) { return -1; }  // don''t sort
                return 1;                   // sort
            };
        }
        for (i = 0; i < len(a) - 1; i += 1) {
            for (j = i + 1; j < len(a); j += 1) {
                if (f(a[i], a[j]) > 0) {
                    tmp = a[i];
                    a[i] = a[j];
                    a[j] = tmp;
                }
            }
        }
        return a;
    };
    _.splice = function (a, p1, count) {
        var ans = [], i = null, j = null;
        if (count === null) { count = 1; }
        for (i = 0; i < count; i += 1) {
            append(ans, a[p1]);
            del(a, p1);
        }
        return ans;
    };
    _.every = function (a, f) {
        var i = null;
        for (i = 0; i < len(a); i += 1) {
            if (!f(a[i])) { return false; }
        }
        return true;
    };
    _.all = _.every;
    _.some = function (a, f) {
        var i = null;
        for (i = 0; i < len(a); i += 1) {
            if (f(a[i])) { return true; }
        }
        return false;
    };
    _.any = _.some;
    _.forEach = function (a, f) {
        var i = null;
        for (i = 0; i < len(a); i += 1) { f(a[i]); }
        return null;
    };
    _.each = _.forEach;

    _.filter = function (a, f) {
        var ans = [], i = null;
        for (i = 0; i < len(a); i += 1) {
            if (f(a[i])) { append(ans, a[i]); }
        }
        return ans;
    };
    _.reject = function (a, f) {
        return _.filter(a, function (x) { return !f(x); });
    };
    _.reduce = function (a, f, prev) {
        var i = 0;
        if (prev === null) { prev = a[0]; i = 1; }
        for (i = i; i < len(a); i += 1) { prev = f(prev, a[i]); }
        return prev;
    };
    _.foldl = function (a, f) { return _.reduce(a, f, null); };
    _.reduceRight = function (a, f, prev) {
        var i = len(a) - 1;
        if (prev === null) {
            prev = a[len(a) - 1]; // last elt
            i = i - 1;            // second-last elt
        }
        for (i = i; i >= 0; i -= 1) { prev = f(prev, a[i]); }
        return prev;
    };
    _.foldr = function (a, f) { return _.reduceRight(a, f, null); };
    _.find = function (a, f) {
        var i = null;
        for (i = 0; i < len(a); i += 1) {
            if (f(a[i])) { return a[i]; }
        }
        return null;
    };
    _.contains = function (x, elt) {
        if (type(x) === 'object') {
            return _.index(keys(x), elt) !== -1;
        }
        return _.index(x, elt) !== -1;
    };
    _.matches = function (subO) { // subO <--> sub-object
        return function (o) {
            var i = null, j = null,
                k = null, kez = keys(subO);
            if (o === subO) { return true; }
            for (i = 0; i < len(subO); i += 1) {
                k = kez[i];
                if (!_.contains(o, k)) { return false; }
                if (o[k] !== subO[k]) { return false; }
            }
            return true;
        };
    };
    _.where = function (aO, subO) { // aO <--> array of objects
        var matches = _.matches(subO);
        return _.filter(aO, matches);
    };
    _.findWhere = function (aO, subO) {
        var matches = _.matches(subO);
        return _.find(aO, matches);
    };
    
return null;}());
