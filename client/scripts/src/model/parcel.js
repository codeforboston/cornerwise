define(["backbone", "underscore"],
       function(B, _) {
           return B.Model.extend({
               initialize: function() {

               },

               parse: function(response) {
                   return _.extend(response.properties, {
                       geom: {coordinates: response.coordinates,
                              type: response.type}
                   });
               }
           }, {
               modelName: "parcel"
           });
       });
