define(["backbone", "jquery", "underscore", "selectable", "config"],
       function(B, $, _, SelectableCollection, config) {
           var RegionModel = B.Model.extend({
               loadShape: function() {
                   var shape = this.get("shape");

                   if (shape)
                       return $.Deferred().resolve(shape);

                   var self = this;
                   return $.getJSON(this.get("source"))
                       .done(function(shape) {
                           self.set("shape", shape);
                           self.trigger("regionLoaded", shape);
                       });

               }
           });

           var regions = _.map(config.regions, function(region) {
               return new RegionModel(region);
           });

           var RegionCollection = SelectableCollection.extend({
               selection: ["somerville"],

               model: RegionModel,

               hashParam: "f.region"
           });

           return new RegionCollection(regions);
       });
