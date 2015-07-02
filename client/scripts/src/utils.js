define(["underscore", "jquery"], function(_, $) {
    return {
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
        }
    };
});
