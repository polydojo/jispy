////////////////////////////////////////////////////////////
//      The STANDARD LIBRARY shipped with Jispy           //
//      Written purely in LittleJ (Jispy''s JS subset)    //
//              (c) Sumukh Barve, 2014;                   //
////////////////////////////////////////////////////////////
var string = {}, array = {}, object = {};
(function () {
    'use strict';
    //In general, s denotes a string, a an array, o an object and f a function.
    string.charCodeAt = function (s, i) { return ord(s[i]); };
    string.concat = function (s1, s2) { return s1 + s2; };
    string.slice = function (s, p1, p2) {
        var ans = '', i = null, ls = len(s);
        if (p1 === null) { p1 = 0; } else if (p1 < 0) { p1 = ls + p1; }
        if (p2 === null) { p2 = ls; } else if (p2 > ls) { p2 = ls; } else if (p2 < 0) { p2 = ls + p2; }
        for (i = p1; i < p2; i += 1) { ans += s[i]; }
        return ans;
    };
    string.from = function (s, p1) { return string.slice(s, p1, null); };
    string.upto = function (s, p2) { return string.slice(s, null, p2); };
    string.indexOf = function (s, tgt, pos) {
        var i = null, ls = len(s), ltgt = len(tgt);
        if (pos === null) { pos = 0; }
        for (i = pos; i <= ls - ltgt; i += 1) {
            if (string.slice(s, i, i + ltgt) === tgt) { return i; }
        }
        return -1;
    };
    string.index = function (s, tgt) { return string.indexOf(s, tgt, null); };
    string.lastIndexOf = function (s, tgt, pos) {
        var i = null, ls = len(s), ltgt = len(tgt);
        if (pos === null) { pos = ls - 1; }
        s = string.slice(s, 0, pos + 1);
        for (i = pos; i >= (ltgt - 1); i -= 1) {
            if (string.slice(s, i - (ltgt - 1), i + 1) === tgt) {
                return i - (ltgt - 1);
            }
        }
        return -1;
    };
    string.rindex = function (s, tgt) { return string.lastIndexOf(s, tgt, null); };
    string.replace = function (s, old, rep) {
        var i = null, lold = len(old);
        while (true) {
            i = string.indexOf(s, old, null);
            if (i === -1) { break; }
            s = string.upto(s, i) + rep + string.from(s, i + lold);
        }
        return s;
    };
    array.slice = function (a, p1, p2) {
        var ans = [], i = null, la = len(a);
        if (p1 === null) { p1 = 0; } else if (p1 < 0) { p1 = la + p1; }
        if (p2 === null) { p2 = la; } else if (p2 > la) { p2 = la; } else if (p2 < 0) { p2 = la + p2; }
        for (i = p1; i < p2; i += 1) { append(ans, a[i]); }
        return ans;
    };
    array.from = function (a, p1) { return array.slice(a, p1, null); };
    array.upto = function (a, p2) { return array.slice(a, null, p2); };
    string.split = function (s, sep) {
        var ans = [], i = null, ls = len(s), lsep = len(sep);
        if (sep === '') {
            for (i = 0; i < ls; i += 1) { append(ans, s[i]); }
            return ans;
        }
        // otherwise...
        while (true) {
            i = string.index(s, sep);
            if (i === -1) {
                append(ans, s);
                break;
            }
            append(ans, string.upto(s, i));
            s = string.from(s, i + lsep);
        }
        return ans;
    };
    string.splitLimit = function (s, sep, limit) {
        return array.upto(string.split(s, sep), limit);
    };
    string.toLowerCase = function (s) {
        var ans = '', i = null, ls = len(s),
            ordA = ord('A'), ordZ = ord('Z'), ordI = null;
        for (i = 0; i < ls; i += 1) {
            ordI = ord(s[i]);
            if (ordA <= ordI && ordI <= ordZ) { ans += chr(ordI + 32); } else { ans += s[i]; }
        }
        return ans;
    };
    string.lower = string.toLowerCase;
    string.toUpperCase = function (s) {
        var ans = '', i = null, ls = len(s),
            o_a = ord('a'), o_z = ord('z'), o_i = null;
        for (i = 0; i < ls; i += 1) {
            o_i = ord(s[i]);
            if (o_a <= o_i && o_i <= o_z) { ans += chr(o_i - 32); } else { ans += s[i]; }
        }
        return ans;
    };
    string.upper = string.toUpperCase;
    array.concat = function (a1, a2) {
        var ans = [], i = null, la1 = len(a1), la2 = len(a2);
        for (i = 0; i < la1; i += 1) { append(ans, a1[i]); }
        for (i = 0; i < la2; i += 1) { append(ans, a2[i]); }
        return ans;
    };
    array.join = function (a, sep) {
        var ans = '', i = null, la = len(a);
        for (i = 0; i < la - 1; i += 1) { ans += str(a[i]) + sep; }
        return ans + str(a[i]);
    };
    array.popAt = function (a, i) {
        var ans = a[i];
        del(a, i);
        return ans;
    };
    array.pop = function (a) { return array.popAt(a, len(a) - 1); };
    array.push = append;
    array.reverse = function (a) {
        var i = null, tmp = null, la = len(a);
        for (i = 0; i < la / 2; i += 1) {
            tmp = a[i];
            a[i] = a[(la - 1) - i];
            a[(la - 1) - i] = tmp;
        }
        return null;
    };
    array.shift = function (a) {
        var ans = a[0];
        del(a, 0);
        return ans;
    };
    array.sortBy = function (a, f) {
        var i = null, j = null, tmp = null, la = len(a);
        for (i = 0; i < la - 1; i += 1) {
            for (j = i + 1; j < la; j += 1) {
                if (f(a[i], a[j]) > 0) {    // sort is stable
                    tmp = a[i];
                    a[i] = a[j];
                    a[j] = tmp;
                }
            }
        }
        return a;
    };
    array.sort = function (a) {
        var f = function (m, n) {
            if (m <= n) { return -1; }
            return 1;
        };
        return array.sortBy(a, f);
    };
    // todo: write array.sortedBy and array.sorted
    array.splice = function (a, p1, count) {
        var ans = [], i = null;
        if (count === null) { count = 1; }
        for (i = 0; i < count; i += 1) {
            append(ans, a[p1]);
            del(a, p1);
        }
        return ans;
    };
    array.unshift = function (a, elt) {
        var i = null, la = append(a, elt);
        for (i = la - 1; i >= 1; i -= 1) { a[i] = a[i - 1]; }
        a[0] = elt;
        return la;
    };
    array.indexOf = function (a, elt, pos) {
        var i = null, la = len(a);
        if (pos === null) { pos = 0; }
        for (i = pos; i < la; i += 1) { if (elt === a[i]) { return i; } }
        return -1;
    };
    array.index = function (a, elt) { return array.indexOf(a, elt, null); };
    array.lastIndexOf = function (a, elt, pos) {
        var i = null, la = len(a);
        if (pos === null) { pos = la - 1; }
        for (i = pos; i >= 0; i -= 1) { if (elt === a[i]) { return i; } }
        return -1;
    };
    array.rindex = function (a, elt) { return array.lastIndexOf(a, elt, null); };
    array.every = function (a, f) {
        var i = null, la = len(a);
        for (i = 0; i < la; i += 1) { if (!f(a[i])) { return false; } }
        return true;
    };
    array.all = array.every;
    array.some = function (a, f) {
        var i = null, la = len(a);
        for (i = 0; i < la; i += 1) { if (f(a[i])) { return true; } }
        return false;
    };
    array.any = array.some;
    array.forEach = function (a, f) {
        var i = null, la = len(a);
        for (i = 0; i < la; i += 1) { f(a[i]); }
        return null;
    };
    array.each = array.forEach;
    array.map = function (a, f) {
        var ans = [], i = null, la = len(a);
        for (i = 0; i < la; i += 1) { append(ans, f(a[i])); }
        return ans;
    };
    array.filter = function (a, f) {
        var ans = [], i = null, la = len(a);
        for (i = 0; i < la; i += 1) { if (f(a[i])) { append(ans, a[i]); } }
        return ans;
    };
    array.fold = function (a, f, initial) {
        var i = null, la = len(a);
        for (i = 0; i < la; i += 1) { initial = f(initial, a[i]); }
        return initial;
    };
    array.foldl = array.fold;
    array.reduce = function (a, f) {
        return array.fold(array.from(a, 1), f, a[0]);
    };
    array.foldr = function (a, f, initial) {
        var i = null, la = len(a);
        for (i = la - 1; i >= 0; i -= 1) { initial = f(initial, a[i]); }
        return initial;
    };
    array.reduceRight = function (a, f) {
        return array.foldr(array.upto(a, -1), f, a[len(a) - 1]);
    };
    object.keys = keys;
    object.hasOwnProperty = function (o, s) { return array.index(keys(o), s, null) !== -1; };
    return null;
}());
