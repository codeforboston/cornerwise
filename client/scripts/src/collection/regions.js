define(["backbone", "jquery", "underscore", "collection/selectable", "utils", "config"],
       function(B, $, _, SelectableCollection, $u, config) {
           var RegionModel = B.Model.extend({
               loadShape: function() {
                   var shape = this.get("shape");

                   if (shape)
                       return $.Deferred().resolve(shape);

                   if (!this._fetchingShape) {

                   var self = this;
                   this._fetchingShape =
                           $.getJSON(this.get("source"))
                           .done(function(shape) {
                               self.set("shape", shape);
                               self.trigger("regionLoaded", shape);
                               self._fetchingShape = null;
                           });
                   }
                   return this._fetchingShape;
               }
           });

           var allowRegions = config.includeRegions,
               filter = _.isArray(allowRegions) ? (function(region) {
                   return _.contains(allowRegions, region.id);
               }) : allowRegions;

               regions = $u.keep(config.regions, function(region) {
                   if (!filter || filter(region))
                       return new RegionModel(region);

                   return null;
               });

           var RegionCollection = SelectableCollection.extend({
               selection: [config.regions[0].id],

               model: RegionModel,

               hashParam: "f.region"

           });

           return new RegionCollection(regions);
       });
