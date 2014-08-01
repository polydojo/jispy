// The following is written in pure LittleJ.
// It is meant to evolve into an Underscore.js like library.

var buildUtils = function () {
    var string = {}, array = {}, object = {}, _ = {}, x = 'Hello ', y = 'World!!';
    // string, array and object are holders for ES5 natives.
    
    // Generally, s denotes string, a array, o object and f function.
    
    ////////////////////////////////////////////////////////////////////////////
    // Writing ES5 natives.
    ////////////////////////////////////////////////////////////////////////////
    string.charCodeAt = function (s, i) { return ord(s[i]); };   
    string.concat = function (s1, s2) { return s1 + s2; };
    string.slice = function (s, p1, p2) {
        var ans = '', i = null;
        if (p1 === null) { p1 = 0; }
        else if (p1 < 0) { p1 = len(s) + p1; }
        if (p2 === null) { p2 = len(s); }
        else if (p2 > len(s)) { p2 = len(s); }
        else if (p2 < 0) { p2 = len(s) + p2; }
        for (i = p1; i < p2; i += 1) { ans += s[i]; }
        return ans;
    };
    string.indexOf = function (s, sub, pos) { 
        var i = null;
        if (pos === null) { pos = 0; }
        for (i = pos; i <= len(s) - len(sub); i += 1) {
            if (string.slice(s, i, i + len(sub)) === sub) { return i; }
        }
        return -1;
    };
    string.lastIndexOf = function (s, sub, pos) {
        var i = null, ans = -1;
        if (pos === null) { pos = len(s) - 1; }
        s = string.slice(s, 0, pos + 1);                                        // This is cheeky. But works!
        for (i = 0; i <= len(s) - len(sub); i += 1) {
            if (string.slice(s, i, i + len(sub)) === sub) { ans = i; }
        }
        return ans;
    };
    string.replace = function (s, old, rep) {
        var i = null;
        while (true) {
            i = string.indexOf(s, old, null);
            if (i === -1) { break; }
            s = string.slice(s, 0, i) + rep + p.str.slice(s, i + len(old), null);
        }
        return s;
    };
    array.slice = function (a, p1, p2) {
        var ans = [], i = null;
        if (p1 === null) { p1 = 0; }
        else if (p1 < 0) { p1 = len(p1) + p1; }
        if (p2 === null) { p2 = len(a); }   // p2 === null || p2 > len(s) won''t always work because || has very low precedence
        else if (p2 > len(a)) { p2 = len(a); }
        else if (p2 < 0) { p2 = len(a) + p2; }
        for (i = p1; i < p2; i += 1) { append(ans, a[i]); }
        return ans;
    };
    string.split = function (s, sep, limit) {
        var ans = [], i = null;
        if (sep === '') {
            for (i = 0; i < len(s); i += 1) { append(ans, s[i]); }
            return array.slice(ans, null, limit);
        }
        // otherwise...
        while (true) {
            i = string.indexOf(s, sep, null);
            if (i === -1) {
                append(ans, s);
                break;
            }
            append(ans, p.str.slice(s, 0, i));
            s = string.slice(s, i + len(sep), null);
        }
        return array.slice(ans, null, limit);
    };    
    string.toLowerCase = function (s) {
        var ans = '', i = null, ordA = ord('A'), ordZ = ord('Z'), ordI = null;
        for (i = 0; i < len(s); i += 1) {
            ordX = ord(s[i]);
            if (ordA <= ordI && ordI <= ordZ) { ans += chr(ordI + 32); }
            else { ans += s[i]; }
        }
        return ans;
    };
    string.toUpperCase = function (s) {
        var ans = '', i = null, o_a = ord('a'), o_z = ord('z'), o_i = null;
        for (i = 0; i < len(s); i += 1) {
            o_i = ord(s[i]);
            if (o_a <= o_i && o_i <= o_z) { ans += chr(o_i - 32); }
            else { ans += s[i]; }
        }
        return ans;
    };
    array.concat = function (a1, a2) {
        var ans = [], i = null;
        for (i = 0; i < len(a1); i += 1) { append(ans, a1[i]); }
        for (i = 0; i < len(a2); i += 1) { append(ans, a2[i]); }
        return ans;
    };
    array.join = function (a, sep) {
        var ans = '', i = null;
        for (i = 0; i < len(a) - 1; i += 1) { ans += str(a[i]) + sep; }
        return ans + str(a[i]);
    };
    array.pop = function (a) {
        var ans = a[len(a) - 1];
        del(a, len(a) - 1);
        return ans;
    };
    array.push = append;
    array.reverse = function (a) {
        var i = null, tmp = null;
        for (i = 0; i < len(a) / 2; i += 1) {
            tmp = a[i];
            a[i] = a[len(a) - 1 - i];
            a[len(a) - 1 - i] = tmp;
        }
        return null;
    };
    array.shift = function (a) {
        var ans = a[0];
        del(a, 0);
        return ans;
    };        
    array.sort = function(a, f) {
        var less = [], equal = [], more = [], pivot = null, i = null, tmp = null;
        if (len(a) <= 1) { return a; }
        if (f === null) {
            f = function (m, n) {
                if (m < n) { return -1; }
                else if (m === n) { return 0; }
                return +1;
            };
        }
        pivot = a[0];
        append(equal, pivot);
        for (i = 1; i < len(a); i += 1) {
            tmp = f(a[i], pivot);
            if (tmp < 0) { append(less, a[i]); }
            else if (tmp === 0) { append(equal, a[i]); }
            else { append(more, a[i]); }
        }
        tmp = array.concat(array.sort(less, f), equal);
        return array.concat(tmp, array.sort(more, f));
    };
    array.splice = function (a, p1, count) {
        var ans = [], i = null, j = null;
        if (count === null) { count = 1; }
        for (i = 0; i < count; i += 1) {
            append(ans, a[p1]);
            del(a, p1);
        }
        return ans;
    };
    array.unshift = function (a, elt) {
        var ans = null;
        array.reverse(a);
        ans = append(a, elt);
        array.reverse(a);
        return ans;
    };
    array.indexOf = function (a, elt, pos) {
        var i = null;
        if (pos === null) { pos = 0; }
        for (i = pos; i < len(a); i += 1) { if (elt === a[i]) { return i; } }
        return -1;
    };
    array.lastIndexOf = function (a, elt, pos) {
        var tmp = null, i = null;
        if (pos === null) { pos = len(a) - 1; }
        for (i = pos; i >= 0; i -= 1) { if (elt === a[i]) { return i; } }
        return -1;
    };
    array.every = function (a, f) {
        var i = null, l1 = len(a);
        for (i = 0; i < l1; i += 1) { if (!f(a[i])) { return false; } }
        return true;
    };
    array.some = function (a, f) {
        var i = null;
        for (i = 0; i < len(a); i += 1) { if (f(a[i])) { return true; } }
        return false;
    };
    array.forEach = function (a, f) {
        var i = null;
        for (i = 0; i < len(a); i += 1) { f(a[i]); }
        return null;
    };
    array.map = function (a, f) {
        var ans = [], i = null;
        for (i = 0; i < len(a); i += 1) { append(ans, f(a[i])); }
        return ans;
    };
    array.filter = function (a, f) {
        var ans = [], i = null;
        for (i = 0; i < len(a); i += 1) { if (f(a[i])) { append(ans, a[i]); } }
        return ans;
    };
    array.reduce = function (a, f, prev) {
        var i = 0;
        if (prev === null) { prev = a[0]; i = 1; }
        for (i = i; i < len(a); i += 1) { prev = f(prev, a[i]); }
        return prev;
    };
    array.reduceRight = function (a, f, prev) {
        var leftmost = 0, i = null;
        if (prev === null) { prev = a[len(a) - 1]; leftmost = 1; }
        for (i = len(a) - 1; i >= leftmost; i -= 1) { prev = f(prev, a[i]); }
        return prev;
    };
    object.keys = keys;
    object.hasOwnProperty = function (o, s) { return array.indexOf(keys(o), s, null) !== -1; };
    
    print(len(array) + len(string) + len(object));
return _;}();
