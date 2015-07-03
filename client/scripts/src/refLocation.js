define(["backbone", "config", "arcgis", "utils"], function(B, config, arcgis, $u) {
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
            var self = this;
            return $u.promiseLocation().then(function(loc) {
                self.set({
                    lat: loc[0],
                    lng: loc[1],
                    altitude: loc[2]
                });
                return loc;
            });
        },

        setFromAddress: function(addr) {
            var self = this;
            return arcgis.geocode(addr).then(arcgis.getLatLngForFirstAddress).done(function(loc) {
                self.set({
                    lat: loc[0],
                    lng: loc[1],
                    altitude: null
                });
            });
        }
    });

    return new LocationModel();
});
