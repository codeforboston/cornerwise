define(["backbone", "underscore", "utils", "config", "collection/selectable", "model/parcel"],
       function(B, _, $u, config, Selectable, Parcel) {
           return Selectable.extend({
               model: Parcel,

               initialize: function(options) {
                   Selectable.prototype.initial.apply(this, arguments);

                   this.appState = options.appState;
                   this.query = {};

                   this.appState.onStateKeyChange("p", this.onPointChange, this);
               },

               url: function() {
                   return config.backendURL + "/parcel/find?" + $u.encodeQuery(this.query);
               },

               updateQuery: function(newQuery) {
                   var deferred = $.Deferred();

                   if (_.isEqual(newQuery, this.query)) {
                       deferred.resolve();
                   } else if (_.isEmpty(newQuery)) {
                       this.set([]);
                   } else {
                       this.query = newQuery;
                       var self = this;
                       return this.fetch().then(function(response) {
                           self.setSelection([response.properties.id]);

                           return response;
                       });
                   }

                   return deferred;
               },

               onPointChange: function(point, oldPoint) {
                   var lat, lng, addr;

                   // if (this.)
                   if (!_.isEqual(oldPoint, point)) {
                       if (point) {
                           lat = point.lat;
                           lng = point.lng;
                           // addr = newPoint.addr;
                       } else {
                           this.updateQuery({});
                           return;
                       }
                   }

                   if (lat && lng) {
                       this.updateQuery({lat: lat, lng: lng});
                   }
               }
           });
       });
