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
                   var params = $u.encodeQuery(this._fetchQuery || this.query);
                   return config.backendURL + "/parcel/find?" + params;
               },

               _loading: {},
               _loadFailed: {},

               fetch: function(query, options) {
                   this._fetchQuery = query;
                   options = options || {remove: false};
                   var result = Selectable.prototype.fetch.call(this, options);
                   this._fetchQuery = null;
                   return result;
               },

               /**
                  The active query determines which parcels are selected. If
                  necessary, it will also attempt to load them. If `loadOnly` is
                  true, load the parcels that match the query, but do not change
                  the active query and do not set the selection.
                */
               updateQuery: function(newQuery, loadOnly) {
                   // TODO: Merge queries
                   var deferred = $.Deferred();

                   if (_.isEqual(newQuery, this.query)) {
                       deferred.resolve();
                   } else if (_.isEmpty(newQuery)) {
                       this.set([]);
                   } else {
                       var self = this;
                       // TODO: Instead of doing 'all or nothing', only load
                       // unknown ids.

                       // This code crudely implements the idea that if the
                       // query is only selecting parcels by ID, check if the
                       // IDs have already been loaded locally. This may be
                       // generalizable on Selectable.
                       if (newQuery.id) {
                           if (_.size(newQuery) === 1) {
                               if (_.all(newQuery.id, function(id) {
                                   return self.get(id) ||
                                       self._loading[id] ||
                                       self._loadFailed[id];
                               })) {

                                   if (!loadOnly)
                                       self.setSelection(newQuery.id);
                                   return deferred;
                               }
                           }

                           newQuery.id = newQuery.id.join(",");
                       }
                       if (!loadOnly) this.query = newQuery;

                       return this.fetch(newQuery).then(function(response) {
                           if (!loadOnly)
                               self.setSelection([response.properties.id]);

                           return response;
                       }, function(err) {
                           if (!loadOnly)
                               self.setSelection([]);
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
               },

               setParcelIds: function(ids, loadOnly) {
                   if (!_.isArray(ids))
                       ids = [ids];

                   this.updateQuery({id: ids}, loadOnly);
               }
           });
       });
