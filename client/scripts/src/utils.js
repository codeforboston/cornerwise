define(["underscore"], function(_) {
    return {
        everyPred: function(fs, arg) {
            return _.every(fs, function(f) {
                return f(arg);
            });
        }
    };
});
