/*
 * The reference location is used to determine the distance to
 */
define(["backbone", "lib/leaflet", "view/alerts", "config", "api/arcgis",
        "collection/regions", "utils", "appState"],
       function(B, L, alerts, config, arcgis, regions, $u, appState) {
           var bounds;

           var LocationModel = B.Model.extend({
               defaults: {
                   lat: config.refPointDefault.lat,
                   lng: config.refPointDefault.lng,
                   // The search radius, centered on the current latitude and longitude:
                   radius: null,
                   setMethod: "auto"
               },

               initialize: function(attrs, options) {
                   var ref = appState.getKey("ref");

                   B.Model.prototype.initialize.call(
                       this, this.checkedAttrs(ref, attrs), options);
                   this.bounds = null;

                   appState.onStateKeyChange("ref", this.checkedSet, this);
               },

               checkedAttrs: function(ref, attrs) {
                   var lat = parseFloat(ref.lat),
                       lng = parseFloat(ref.lng);

                   if (!isNaN(lat) && !isNaN(lng)) {
                       return _.extend({}, ref, {lat: lat, lng: lng});
                   }

                   return null;
               },

               checkedSet: function(ref, oldRef) {
                   var attrs = this.checkedAttrs(ref);

                   if (attrs) {
                       this.set(attrs);
                   }
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
                           if (bounds && !bounds.contains(loc)) {
                               alerts.show("You are outside " + config.name,
                                           "error");
                               return loc;
                           }

                           self.set({
                               altitude: loc[2]
                           });
                           appState.setHashKey("ref", {
                               lat: loc[0],
                               lng: loc[1],
                               setMethod: "geolocate"
                           });

                           return loc;
                       }, function(err) {
                           alerts.show(err.reason, "error");
                       })
                       .always(function() {
                           self.set("geolocating", false);
                       });
               },

               setFromLatLng: function(lat, long, address) {
                   appState.setHashKey("ref", {
                       lat: lat,
                       lng: long,
                       setMethod: address ? "address" : "map",
                       address: address || ""
                   });
               },

               setFromAddress: function(addr) {
                   var self = this;
                   this.set("geolocating", true);
                   return arcgis.geocode(addr).then(arcgis.getLatLngForFirstAddress).done(function(loc) {
                       if (bounds && !bounds.contains(loc)) {
                           alerts.show("That address is outside " + config.name,
                                       "error");
                           return loc;
                       }

                       self.set({
                           altitude: null
                       });
                       appState.setHashKey("ref", {
                           address: addr,
                           setMethod: "address",
                           lat: loc[0],
                           lng: loc[1]
                       });

                       return loc;
                   }).fail(function() {
                       alerts.show("I couldn't find that address.");
                   }).always(function() {
                       self.set("geolocating", false);
                   });
               }
           });

           var refLocation = new LocationModel();

           // TODO: Update whenever the active regions change:
           refLocation.listenTo(regions, "regionLoaded",
                                function(shape) {})
               .listenTo(regions, "selectionRemoved",
                         function(regions, ids) {});

           return refLocation;
       });
