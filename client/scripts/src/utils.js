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
        var re = /(\d+)(\d{3})(\.\d+|\b|$)/g, m,
            pieces = [];

        while((m = re.exec(s))) {
            s = m[1];

            pieces.unshift(m[2] + (m[3] || ""));
        }

        pieces.unshift(s);

        return pieces.join(",");
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

    var defaultHelpers = {
        formatDate: function(d) {
            return (d.toLocaleDateString) ?
                d.toLocaleDateString() :
                d.toString().slice(0, 15);
        },

        commas: commas,

        pluralize: function(n, sing, plur) {
            return n == 1 ? sing : (plur || sing + "s");
        },

        prettyAmount: prettyAmount
    };

    var $u = {
        everyPred: function(fs, arg) {
            return _.every(fs, function(f) {
                return f(arg);
            });
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
         * @param {String} currency
         */
        prettyAmount: prettyAmount,

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
