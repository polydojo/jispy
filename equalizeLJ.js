(function (global) {
    'use strict';
    global.keys = Object.keys;
    global.type = function (x) {
        if (x === null) { return 'null'; }
        if (Object.prototype.toString.call(x) === '[object Array]') { return 'array'; }
        return typeof x;
    };
    global.str = function (x) {
        if (typeof x === 'object') { return JSON.stringify(x); }
        return String(x);
    };
    global.print = function (x) {
        console.log(x);
        return null;
    };
    global.len = function (x) {
       if (global.type(x) === 'object') { return Object.keys(x).length; }
        return x.length;
    };
    global.del = function (x, y) {
        if (global.type(x) === 'array') {
            x.splice(y, 1);
            return true;
        }
        return delete x[y];
    };
    global.append = function (arr, elt) { arr.push(elt);  return global.len(arr); };
    global.assert = function (expr, msg) {
        if (expr) { return null; }
        throw new Error('AssertionError: ' + global.str(msg));
    };
    global.ord = function (c) { return c.charCodeAt(0); };
    global.chr = function (i) { return String.fromCharCode(i); };
    global.math = Math;
}(this));
