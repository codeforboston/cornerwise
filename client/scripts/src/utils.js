define(["underscore", "jquery", "locale"],
       function(_, $, locale) {
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

           /**
            * Takes a numeric string s and adds thousands separators.
            * For example: commas("12345678.3") -> "12,345,678.3"
            *
            * @param {String|Number} s A number or numeric string to format.
            *
            * @returns {String} A string with commas inserted
            */
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

           function ordinal(n) {
               n = "" + n;
               var ends = {"1": "st", "2": "nd", "3": "rd"},
                   end = "th";



               if (n.length < 2 || n[n.length-2] !== "1") {
                   end = ends[n[n.length-1]] || "th";
               }

               return n + end;
           }

           function prettyAmount(amount, currency) {
               currency = currency || "$";

               var mag = "";

               if (amount >= 10000) {
                   if (amount < 1000000) {
                       mag = "K";
                       amount /= 1000;
                   } else if (amount < 1000000000) {
                       mag = "M";
                       amount /= 1000000;
                   } else {
                       mag = "B";
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
               } else if (miles >= 0.2) {
                   var denom, num;
                   if (miles > 0.5) {
                       denom = Math.round(1/(1-miles));
                       num = Math.round(miles*denom);

                   } else {
                       denom = Math.round(1/miles);
                       num = 1;
                   }

                   return "about <sup>" + num + "</sup>&frasl;<sub>" + denom + "</sub> mile";
               }

               return commas(ft) + " feet";
           }


           function prettyDate(d, format) {
               if (!(d instanceof Date)) {
                   d = new Date(d);
               }

               if (isNaN(d)) {
                   return "unknown date";
               }

               format = format || "s";

               if (format === "s") {
                   return [locale.monthNames[d.getMonth()],
                           ordinal(d.getDate())].join(" ");
               }
           }

           /**
            * @param {String} s
            *
            * @returns {String} A copy of s with its first character converted
            * to upper case.
            */
           function capitalize(s) {
               return s[0].toUpperCase() + s.slice(1);
           }

           function fromUnder(s) {
               pieces = s.split(/_+/);

               return _.map(pieces, capitalize).join(" ");
           }

           function pluralize(n, s, pl) {
               pl = pl || s + (s.slice(-1).match(/(sh|[xs])$/) ? "es" : "s");

               return n == 1 ? s : pl;
           }


           /**
            * @param {String} s
            *
            * @returns {Boolean} true if the string only contains digits.
            */
           function isDigit(s) {
               return /^[0-9]+$/.test(s);
           }

           function isSimpleObject(o) {
               return o.constructor && o.constructor === Object;
           }

           function setIn(obj, ks, v) {
               if (ks.length === 0)
                   return v;

               var k = ks[0];

               if (isDigit(k))
                   k = parseInt(k);

               if (ks.length === 1 && k === undefined) {
                   delete obj[k];
               } else {
                   obj[k] = setIn(obj[k] || {},
                                  ks.slice(1),
                                  v);
               }
               return obj;
           }

           function getIn(obj, ks) {
               if (ks.length === 0)
                   return obj;

               if (!obj)
                   return undefined;

               return getIn(obj[ks[0]], ks.slice(1));
           }

           function deepMerge(obj1, obj2) {
               _.each(obj2, function(v, k) {
                   var orig = obj2[k];
                   if (orig && isSimpleObject(v) && isSimpleObject(orig)) {
                       deepMerge(v, orig);
                   } else {
                       obj1[k] = v;
                   }
               });
           }

           function flattenMap(obj, pref) {
               pref = pref || "";
               return _.reduce(obj, function(m, val, key) {
                   if (!(!key || val === undefined)) {
                       if (isSimpleObject(val)) {
                           return _.extend(m, flattenMap(val, key + "."));
                       }

                       m[pref + key] = val;
                   }

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

               pluralize: pluralize,

               prettyAmount: prettyAmount,

               prettyDistance: prettyDistance,

               prettyDate: prettyDate
           };

           var $u = {
               keepArgs: function(fn, n) {
                   return function() {
                       return fn.apply(this, _.take(arguments, n));
                   };
               },

               parseInt10: function(n) {
                   return parseInt(n, 10);
               },

               capitalize: capitalize,

               //
               // @param {String} s
               //
               // @returns {String} s with underscores removed and words capitalized
               fromUnder: fromUnder,

               escapeRegex: function(s) {
                   return s.replace(/[.*+?\^$[\]\\(){}|\-]/g, "\\$&");
               },

               /**
                * Generate an equivalent regular expression for the given glob
                * string.
                *
                * @param {String} patt A glob pattern
                *
                * @returns {RegExp}
                */
               glob: function(patt) {
                   var re = patt
                       .replace(/[.+\^$[\]\\(){}|\-]/g, "\\$&")
                       .replace("*", ".*")
                       .replace("?", ".");

                   return new RegExp(re, "i");
               },

               everyPred: function(fs, arg) {
                   return _.every(fs, function(f) {
                       return f(arg);
                   });
               },

               idIs: function(val) {
                   return function(model) {
                       return model.id == val;
                   };
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

               /**
                * @returns {jquery.Deferred} A promise that, when resolved,
                * returns the coordinates from the user's browser.
                */
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

               closeTo: function(n1, n2, tolerance) {
                   return Math.abs(n1 - n2) <= (tolerance || 0.1);
               },

               // Unit conversions:
               mToFeet: function(m) {
                   return m*3.281;
               },

               feetToM: function(ft) {
                   return ft/3.281;
               },

               mToMiles: function(m) {
                   return m*3.281/5280;
               },

               // Formatting
               commas: commas,

               /**
                * @param {number} amount
                * @param {string} currency
                *
                * @returns {string}
                */
               prettyAmount: prettyAmount,

               /**
                * Convert a number to a human-friendly distance string.
                *
                * @param {number} feet Distance in feet
                */
               prettyDistance: prettyDistance,


               currentYear: function() {
                   return (new Date()).getFullYear();
               },

               /**
                * Register a default template helper, which will be available
                * to templates created with $u.template().
                *
                * @param {string} name
                * @param {Function}
                */
               registerHelper: function(name, fn) {
                   defaultHelpers[name] = fn;
                   return this;
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

               /**
                * Traverse a map using a sequence of keys and return the nested
                * value.
                *
                * @param {Object} obj A map
                * @param {Array} ks An array of keys
                *
                * @returns obj[ks[0]][ks[1]]...[ks[n]] or null
                */
               getIn: getIn,
               /**
                * Change a key in a nested map
                *
                * @param {Object} obj
                * @param {Array} ks
                */
               setIn: setIn,

               deepMerge: deepMerge,
               flattenMap: flattenMap,

               /**
                * @param {Object} o A map of strings to
                *
                * @returns A string encoding the contents of the map.  Nested
                * maps are flattened with flattenMap.
                */
               encodeQuery: function(o) {
                   return _.map(flattenMap(o), function(val, k) {
                       return encodeURIComponent(k) + "=" + encodeURIComponent(val);
                   }).sort().join("&");
               },

               decodeQuery: function(s) {
                   var idxRe = /\[(\d+)\]$/;
                   return _.reduce(s.split("&"), function(m, piece) {
                       var ss = piece.split("="),
                           k = decodeURIComponent(ss[0]),
                           val = decodeURIComponent(ss[1]);

                       if (k.indexOf(".") > -1) {
                           var ks = k.split(".");
                           setIn(m, ks, val);
                       } else {
                           m[k] = val;
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
               template: function(templateString, settings, helpers) {
                   helpers = _.extend({}, helpers);
                   helpers.__proto__ = defaultHelpers;

                   settings = _.clone(settings);
                   var varName = settings && settings.variable;
                   if (varName)
                       delete settings.variable;

                   var temp = _.template(templateString, settings);

                   return function(data) {
                       if (varName) {
                           var d = {options: settings};
                           d[varName] = data;
                           data = d;
                       }

                       return temp(_.extend({}, data, helpers));
                   };
               },

               /**
                * @param {string} id Element ID of the template element in the
                * DOM.
                * @param {object} options
                * @param o
                *
                * @return {Function}
                */
               templateWithId: function(id, options) {
                   var templateString = $("#" + id).text();

                   if (!templateString) {
                       throw new Error("Unknown template: " + id);
                   }
                   options = options || {};
                   return $u.template(templateString, options, options.helpers);
               },

               /**
                * @param {string} url
                * @param {object} options
                * @param options.helpers 
                */
               templateWithUrl: function(url, options) {
                   var template = null;
                   options = options || {};

                   return function(arg, cb) {
                       if (template) {
                           cb(template(arg));
                           return;
                       }

                       $.get(
                           url,
                           function(templateString) {
                               template = $u.template(templateString,
                                                      options,
                                                      options.helpers);
                               cb(template(arg));
                           }
                       );
                   };
               }
           };

           return $u;
       });
