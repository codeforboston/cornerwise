/*
 * The reference location is used to determine the
 */
define(["backbone", "leaflet", "config", "arcgis", "utils"], function(B, L, config, arcgis, $u) {
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

        getLatLng: function() {
            return L.latLng(this.get("lat"), this.get("lng"));
        },

        getRadiusMeters: function() {
            var r = this.get("radius");
            return r && $u.feetToM(r);
        },

        /**
         * Set the latitude and longitude using the browser's
         * geolocation features, if available.
         */
        setFromBrowser: function() {
            this.set("geolocating", true);

            var self = this;
            return $u.promiseLocation()
                .then(function(loc) {
                    self.set({
                        lat: loc[0],
                        lng: loc[1],
                        altitude: loc[2]
                    });

                    return loc;
                })
                .always(function() {
                    self.set("geolocating", false);
                });
        },

        setFromAddress: function(addr) {
            var self = this;
            this.set("geolocating", true);
            return arcgis.geocode(addr).then(arcgis.getLatLngForFirstAddress).done(function(loc) {
                self.set({
                    lat: loc[0],
                    lng: loc[1],
                    altitude: null
                });
            }).always(function() {
                self.set("geolocating", false);
            });
        }
    });

    return new LocationModel();
});
