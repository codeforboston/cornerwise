define(["backbone", "jquery"], function(B, $) {
    return B.Model.extend({
        getFeatures: function() {
            // Returns a Deferred feature collection once the data
            // becomes available.
            var f = this.get("features");

            if (f) {
                return $.Deferred().resolve(f);
            }

            this.set("_loading", true);

            var self = this;
            return $.getJSON(this.get("source"))
                .then(function(json) {
                    self.set({features: json, _loading: false});
                    return json;
                }, function(response) {
                    self.set({_loading: false, _errorResponse: response});
                    return _;
                });
        }
    });
});
