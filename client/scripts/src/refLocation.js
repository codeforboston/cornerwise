/*
 * The reference location is used to determine the distance to
 */
define(["backbone", "leaflet", "alerts", "config", "arcgis", "regions", "utils"],
       function(B, L, alerts, config, arcgis, Regions, $u) {
           var currentRegion, bounds;



           var LocationModel = B.Model.extend({
               defaults: {
                   lat: config.refPointDefault.lat,
                   lng: config.refPointDefault.lng,
                   // The search radius, centered on the current latitude and longitude:
                   radius: null,
                   setMethod: "auto"
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
                           if (!bounds.contains(loc)) {
                               alerts.show("You are outside " + config.regionName,
                                           "error");
                               return loc;
                           }

                           self.set({
                               lat: loc[0],
                               lng: loc[1],
                               altitude: loc[2],
                               setMethod: "geolocate"
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
                       if (!bounds.contains(loc)) {
                           alerts.show("That address is outside " + config.regionName,
                                       "error");
                           return loc;
                       }

                       self.set({
                           lat: loc[0],
                           lng: loc[1],
                           altitude: null,
                           setMethod: "address",
                           address: addr
                       });

                       $(document).trigger("showMain");

                       return loc;
                   }).fail(function() {
                       alert.show("I couldn't find that address.");
                   }).always(function() {
                       self.set("geolocating", false);
                   });
               }
           });

           return new LocationModel();
       });
