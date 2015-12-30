define(["underscore", "jquery"], function(_, $) {
    $.fn.transition = function(klFrom, klActive, klFinal) {
        var self = this;
        this.addClass(klFrom);
        this.one("animationend", function(e) {
            self.removeClass(klFrom).removeClass(klActive);
            if (klFinal)
                self.addClass(klFinal);
        });
        this.addClass(klActive);
    };

    $.fn.animateAddClass = function(klBase) {
        this.classTransition(klBase + "-enter",
                             klBase + "-active");
    };

    function commas(s) {
        if (!s) return "";

        s = s.toString();
        var split = s.split("."),
            after = split[1];

        s = split[0];

        var l = s.length;
        if (l <= 3)
            return s;

        var istart = 0,
            iend = (l % 3) || 3,
            pieces = [],
            p;

        while ((p = s.slice(istart, iend))) {
            pieces.push(p);
            istart = iend;
            iend += 3;
        }

        return pieces.join(",") + (after ? ("." + after) : "");
    }

    function prettyAmount(amount, currency) {
        currency = currency || "$";

        var mag = "";

        if (amount >= 10000) {
            if (amount < 1000000) {
                mag = "k";
                amount /= 1000;
            } else if (amount < 1000000000) {
                mag = "m";
                amount /= 1000000;
            } else {
                mag = "b";
                amount /= 1000000000;
            }

            var amountStr = amount.toFixed(1).replace(/\.0$/, "");

            return currency + amountStr + mag;
        }

        return currency + commas(amount);
    }

    function prettyDistance(ft) {
        var miles = ft/5280;

        if (miles >= 1) {
            var m = miles.toFixed(1).replace(/\.0$/, "");
            return m + " mile" + (miles - 1 < 0.1 ? "" : "s");
        }

        return commas(ft) + " feet";
    }

    function capitalize(s) {
        return s[0].toUpperCase() + s.slice(1);
    }

    function setIn(obj, ks, v) {
            if (ks.length == 0)
                return v;

            var k = ks[0];
            obj[k] = setIn(obj[k] || {},
                           ks.slice(1),
                           v);
            return obj;
    }

    function flattenMap(obj, pref) {
        pref = pref || "";
        return _.reduce(obj, function(m, val, key) {
            if (_.isObject(val) && !_.isFunction(val) &&
                !_.isArray(val)) {
                return _.extend(m, flattenMap(val, key + "."));
            }

            m[pref + key] = val;

            return m;
        }, {});
    }

    var defaultHelpers = {
        formatDate: function(d) {
            return (d.toLocaleDateString) ?
                d.toLocaleDateString() :
                d.toString().slice(0, 15);
        },

        capitalize: capitalize,

        commas: commas,

        pluralize: function(n, sing, plur) {
            return n == 1 ? sing : (plur || sing + "s");
        },

        prettyAmount: prettyAmount,

        prettyDistance: prettyDistance
    };

    var $u = {
        keepArgs: function(fn, n) {
            return function() {
                return fn.apply(this, _.take(arguments, n));
            };
        },

        capitalize: capitalize,

        escapeRegex: function(s) {
            return s.replace(/[.*+?\^$[\]\\(){}|\-]/g, "\\$&");
        },

        everyPred: function(fs, arg) {
            return _.every(fs, function(f) {
                return f(arg);
            });
        },

        findIndex: function(coll, f) {
            for (var i = 0, l = coll.length; i < l; i++) {
                if (f(coll[i]))
                    return i;
            }

            return -1;
        },

        /**
         * Call function fn on an array of the 1st argument of each
         * array in colls, then on an array of the 2nd arguments,
         * etc. Stops when any of the arrays is exhausted.
         *
         * @param {Function} fn
         * @param {Array} colls
         *
         * @returns {Array} Results of calling fn on the elements of
         * colls.
         */
        zipmap: function(fn, colls) {
            var out = [],
                idx = 0;

            outer:
            while (true) {
                var args = [], i = 0, coll;

                while ((coll = colls[i++]) !== undefined) {
                    if (coll[idx] === undefined)
                        break outer;

                    args.push(coll[idx]);
                }

                out.push(fn(args));

                idx++;
            }

            return out;
        },

        promiseLocation: function() {
            var promise = $.Deferred();

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        var coords = pos.coords;
                        promise.resolve([coords.latitude,
                                         coords.longitude,
                                         coords.altitude]);
                    },
                    function() {
                        promise.reject({reason: "Permission denied"});
                    });
            } else {
                promise.reject({reason: "Geolocation unavailable in this browser."});
            }

            return promise;
        },

        mToFeet: function(m) {
            return m*3.281;
        },

        feetToM: function(ft) {
            return ft/3.281;
        },

        mToMiles: function(m) {
            return m*3.281/5280;
        },

        commas: commas,

        currentYear: function() {
            return (new Date()).getFullYear();
        },

        /**
         * @param {number} amount
         * @param {string} currency
         *
         * @returns {string}
         */
        prettyAmount: prettyAmount,

        /**
         * Present a distance in feet in a human-readable way.
         *
         * @param {number} feet Distance in feet
         */
        prettyDistance: prettyDistance,

        /**
         * Register a default template helper, which will be available
         * to templates created with $u.template().
         *
         * @param {string} name
         * @param {Function}
         */
        registerHelper: function(name, fn) {
            defaultHelpers[name] = fn;
        },

        setCookie: function(name, value, options) {
            document.cookie = [
                encodeURIComponent(name), "=",
                encodeURIComponent(value), ";"
            ].join("");
        },

        getCookie: function(name) {
            var cookie = document.cookie,
                patt = new RegExp("(^|;\\s*)" +
                                  $u.escapeRegex(encodeURIComponent(name)) +
                                 "=([^;]+)"),
                m = cookie.match(patt);

            return m && decodeURIComponents(m[2]);
        },

        setIn: setIn,

        flattenMap: flattenMap,

        encodeQuery: function(o) {
            return _.map(o, function(val, k) {
                return encodeURIComponent(k) + "=" + encodeURIComponent(val);
            }).join("&");
        },

        decodeQuery: function(s) {
            return _.reduce(s.split("&"), function(m, piece) {
                var ss = piece.split("="),
                    k = decodeURIComponent(ss[0]),
                    val = decodeURIComponent(ss[1]);

                if (k.indexOf(".") > -1) {
                    var ks = k.split(".");
                    setIn(m, ks, val);
                } else {
                    if (!m[k]) {
                        m[k] = val;
                    } else if (_.isString(m[k])) {
                        m[k] = [m[k], val];
                    } else {
                        m[k].push(val);
                    }
                }

                return m;
            }, {});
        },

        /**
         * Like _.template, except that it adds helper functions to the
         * data passed to the resulting template function.
         *
         * @param {string} templateString
         * @param {object} helpers Mapping names to functions
         * @param {object} settings Passed as second argument to _.template
         */
        template: function(templateString, helpers, settings) {
            helpers = helpers || defaultHelpers;

            if (settings) {
                var varName = settings.variable;
                delete settings.variable;
            }

            var temp = _.template(templateString, settings);

            return function(data) {
                if (varName) {
                    var d = {};
                    d[varName] = data;
                    data = d;
                }

                return temp(_.extend(data, helpers));
            };
        },

        /**
         * @param {string} id Element ID of the template element in the
         * DOM.
         * @param {object} options
         */
        templateWithId: function(id, options) {
            var templateString = $("#" + id).text();

            if (!templateString) {
                throw new Error("Unknown template: " + id);
            }
            options = options || {};
            return $u.template(templateString, options.helpers, options);
        }
    };

    return $u;
});
