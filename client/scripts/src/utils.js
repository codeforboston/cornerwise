define(["underscore", "jquery", "locale", "config", "lib/leaflet", "optional!build/templates"],
       function(_, $, locale, config, L, templates) {
           var errors = config.errors;

           /**
            * Takes a numeric string s and adds thousands separators.
            * For example: commas("12345678.3") -> "12,345,678.3"
            *
            * @param {string|Number} s A number or numeric string to format.
            *
            * @returns {string} A string with commas inserted
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

           function acresToSqFt(acres) {
               return Math.round(acres * 43560);
           }

           function prettyFraction(dec) {
               var whole = Math.floor(dec),
                   frac = dec - whole,
                   denom, num;

               if (frac > 0.5) {
                   denom = Math.round(1/(1-frac));
                   num = Math.round(frac*denom);
               } else {
                   denom = Math.min(Math.round(1/frac), 10);
                   num = Math.round(frac*denom);
               }

               return [whole, num, denom];
           }

           function prettyDistance(meters) {
               var ft = meters * 3.2808,
                   miles = ft/5280;

               if (miles >= 0.2) {
                   var m = miles.toFixed(1).replace(/\.0$/, "");
                   return m + " mile" + (Math.abs(miles - 1) < 0.1 ? "" : "s");
               }

               return commas(ft) + " feet";
           }


           function prettyDate(d, format) {
               // TODO: Use the Internationalization API when available
               // https://marcoscaceres.github.io/jsi18n/
               if (!(d instanceof Date)) {
                   d = new Date(d);
               }

               if (isNaN(d)) {
                   return "unknown date";
               }

               format = format || "s";

               if (format == "s") {
                   return [d.getMonth()+1,
                           d.getDate(),
                           d.getFullYear().toString().slice(2)].join("/");
               } else if (format === "m") {
                   return [locale.monthNames[d.getMonth()],
                           ordinal(d.getDate())].join(" ");
               }

               return "";
           }

           /**
            * @param {string} s
            *
            * @returns {string} A copy of s with its first character converted
            * to upper case.
            */
           function capitalize(s) {
               return s[0].toUpperCase() + s.slice(1);
           }

           function fromUnder(s) {
               var pieces = s.split(/_+/);

               return _.map(pieces, capitalize).join(" ");
           }

           function startsWith(s, pref) {
               return s.slice(0, pref.length) === pref;
           }

           function pluralize(n, s, pl) {
               pl = pl || s + (s.slice(-1).match(/(sh|[xs])$/) ? "es" : "s");

               return n == 1 ? s : pl;
           }

           function strToDate(dateStr) {
               var m = /^(\d\d\d\d)(\d\d)(\d\d)/.exec(dateStr);

               if (m) {
                   var date = new Date();
                   date.setYear(m[1]);
                   date.setMonth(parseInt(m[2])-1);
                   date.setDate(parseInt(m[3]));
                   date.setHours(0);
                   date.setMinutes(0);
                   date.setSeconds(0);
                   date.setMilliseconds(0);

                   return date;
               }

               return null;
           }

           function strToDateRange(rangeStr) {
               if (rangeStr[0] == "<") {
                   // Special syntax for representing 'the last n days'
                   var now = new Date(),
                       n = parseInt(rangeStr.slice(1));

                   if (isNaN(n)) n = 60;

                   return [new Date(now.getTime() - (n*86400000)), now];
               }

               var dates = rangeStr.split("-"),
                   start = strToDate($.trim(dates[0])),
                   end = strToDate($.trim(dates[1])) || new Date();

               if (start)
                   return [start, end];

               return null;
           }


           /**
            * @param {string} s
            *
            * @returns {Boolean} true if the string only contains digits.
            */
           function isDigit(s) {
               return /^[0-9]+$/.test(s);
           }

           function isSimpleObject(o) {
               return o && o.constructor && o.constructor === Object;
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
                   var orig = obj1[k];
                   if (orig && isSimpleObject(v) && isSimpleObject(orig)) {
                       deepMerge(orig, v);
                   } else {
                       obj1[k] = v;
                   }
               });

               return obj1;
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

           /**
            * Like map, but discards results that are null or undefined.
            */
           function keep(coll, fn, ctx) {
               ctx = ctx || this;
               coll = _.toArray(coll);
               var result = [];
               for (var i = 0, l = coll.length; i < l; i++) {
                   var val = fn.call(ctx, coll[i]);
                   if (val || val !== undefined && val !== null)
                       result.push(val);
               }
               return result;
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

               prettyDate: prettyDate,

               acresToSqFt: acresToSqFt
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

               pluralize: pluralize,

               /**
                * @param {string} s
                *
                * @returns {string} s with underscores removed and words capitalized
                */
               fromUnder: fromUnder,

               /**
                * @param {string} s
                * @param {string} pref
                *
                * @returns {boolean} true if the string s begins with the string
                * pref
                */
               startsWith: startsWith,

               /**
                * Given a string, escapes special characters.
                *
                * @param {string} s
                *
                * @returns {string} - a string with special regex characters
                * escaped
                */
               escapeRegex: function(s) {
                   return s.replace(/[.*+?\^$[\]\\(){}|\-]/g, "\\$&");
               },

               wordsRegex: function(s) {
                   var words = s.split(/\s+/);

                   return new RegExp(_.map(words, $u.escapeRegex).join("|"), "i");
               },

               /**
                * Generate an equivalent regular expression for the given glob
                * string.
                *
                * @param {string} patt A glob pattern
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
                   for (var i = 0, l = fs.length; i < l; ++i) {
                       if (!fs[i](arg))
                           return false;
                   }

                   return true;
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
                           function(err) {
                               var reason = err.code,
                                   message = errors.geolocation[
                                       reason === 1 ? "denied" :
                                           reason === 3 ? "timeout" :
                                           "unavailable"
                                   ];
                               promise.reject({reason: message, error: err});
                           },
                           {timeout: 10000});
                   } else {
                       promise.reject({reason: errors.geolocation.unavailable});
                   }

                   return promise;
               },

               /**
                * Convert a Leaflet LatLng object to a Google Maps LatLng.
                *
                * @param coords A Leaflet coordinate
                *
                * @returns A Google Maps coordinate
                */
               gLatLng: function(coords) {
                   return new google.maps.LatLng(coords.lat, coords.lng);
               },

               gBounds: function(bounds) {
                   return new google.maps.LatLngBounds(
                       $u.gLatLng(bounds.getSouthWest()),
                       $u.gLatLng(bounds.getNorthEast()));
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
                * Convert a number (in meters) to a human-friendly distance
                * string.
                *
                * @param {number} meters Distance in meters
                */
               prettyDistance: prettyDistance,


               currentYear: function() {
                   return (new Date()).getFullYear();
               },

               /**
                * @param {string}
                */
               strToDateRange: strToDateRange,

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

                   return m && decodeURIComponent(m[2]);
               },

               getCsrfToken: function() {
                   return $u.getCookie("csrftoken");
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
                * @param {Object[]} coll
                * @param {Function} fn
                * @param {Object} ctx The value to which 'this' is bound
                *
                * @returns The function fn applied to each member of coll, with
                * null and undefined values removed.
                */
               keep: keep,

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
                * Converts a string of the form swLat,swLong,neLat,neLong to an
                * instance of Leaflet's LatLngBounds class.
                *
                * @param {string} boxStr
                *
                * @returns {L.LatLngBounds}
                */
               boxStringToBounds: function(boxStr) {
                   // TODO: Cache most recent call arg and return value to avoid
                   // recomputing this a bunch of times in a row?
                   var pieces = boxStr.split(",");

                   return L.latLngBounds([pieces[0], pieces[1]],
                                         [pieces[2], pieces[3]]);
               },

               /**
                * Converts a latLngBounds to a string.
                *
                * @param {L.LatLngBounds} bounds
                *
                * @returns {string}
                */
               boundsToBoxString: function(bounds) {
                   var sw = bounds.getSouthWest(),
                       ne = bounds.getNorthEast();

                   return [sw.lat, sw.lng, ne.lat, ne.lng].join(",");
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
                * Store a map of URLs to jQuery xhr objects, so that overlapping
                * requests to the same URL will not create multiple requests.
                */
               _getting: {},
               _getUrl: function(url) {
                   if (this._getting[url])
                       return this._getting[url];

                   if (templates[url])
                       return $.Deferred().resolve(templates[url]);

                   return (this._getting[url] = $.get(url));
               },

               /**
                * @param {string} url
                * @param {object} options
                * @param options.helpers
                */
               templateWithUrl: function(url, options) {
                   var template = null, self = this;
                   options = options || {};

                   return function(arg, cb) {
                       if (template) {
                           cb(template(arg));
                           return;
                       }

                       self._getUrl(url)
                           .done(function (templateString) {
                               template = $u.template(templateString,
                                                      options,
                                                      options.helpers);
                               cb(template(arg));
                           });
                   };
               }
           };

           return $u;
       });
