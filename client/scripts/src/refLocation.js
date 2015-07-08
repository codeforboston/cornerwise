/*
 * The reference location is used to determine the
 */
define(["backbone", "config", "arcgis", "utils"], function(B, config, arcgis, $u) {
    var LocationModel = B.Model.extend({
        defaults: {
            lat: config.refPointDefault.lat,
            lng: config.refPointDefault.lng,
            // The search radius, centered on the current latitude and longitude:
            radius: null
        },

        getPoint: function() {
            return [this.get("lat"), this.get("lng")];
        },

        getRadiusMeters: function() {
            var r = this.get("radius");
            return r && (r / 3.281);
        },

        /**
         * Set the latitude and longitude using the browser's
         * geolocation features, if available.
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
