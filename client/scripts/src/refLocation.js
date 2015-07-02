define(["backbone", "config"], function(B, config) {
    /*
     * The primary purpose of this model is to set up the observation
     * machinery for a location.
     */
    var LocationModel = B.Model.extend({
        defaults: {
            lat: config.refPointDefault.lat,
            lng: config.refPointDefault.lng
        },

        /**
         *
         */
        setFromBrowser: function() {
            if (navigator.geolocation) {
                var self = this;
                navigator.geolocation.getCurrentPosition(function(pos) {
                    self.set("lat", pos.coords.latitutde);
                    self.set("lng", pos.coords.longitude);
                });
            }
        }
    });

    return new LocationModel();
});
