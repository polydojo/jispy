var keys = Object.keys,
	type = function (x) {
		if (x === null) { return 'null'; }
		if (typeof x === 'object' && Object.prototype.toString.call(x) === '[object Array]') { return 'array'; }
		return typeof x;
	},
	str = function (x) {
		if (x === null) { return 'null'; }
		if (typeof x === 'object') { return JSON.stringify(x); }
		return String(x);
	},
	print = function (x) {
		console.log(x);
		return null;
	},
	len = function (x) {
		if (type(x) === 'array' || type(x) === 'string') { return x.length; }
		if (typeof x === 'object') { return Object.keys(x).length; }
		throw new TypeError(type(x) + ' has no len()');
	},
	del = function (x, y) {
		if (typeof x === 'object' && typeof y === 'string') {
			if (x.hasOwnProperty(y)) { return delete x[y]; }
			throw new Error('IndexError: del() called with non-existent key');
		} else if (type(x) === 'array') {
			if (y === Math.round(y) && 0 <= y && y < len(x)) {	
				x.splice(y, 1);
				return true;
			}
			throw new Error('IndexError: invalid array index passed to del()');
		}
		throw new TypeError('bad call to del()');
	},
	append = function (arr, elt) {
		if (type(arr) === 'array') {
			arr.push(elt);
			return null;
		}
		throw new TypeError('cannot append() to non-array');
	},
	assert = function (expr, msg) {
		if (expr) { return null; }
		throw new Error ('AssertionError: ' + str(msg));
	};
