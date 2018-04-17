define(["backbone", "underscore"],
       function(B, _) {
           var propTypes = {
               BLD_AREA: parseFloat,
               LOT_SIZE: parseFloat,
               YEAR_BUILT: parseInt,
               UNITS: parseInt,
               STORIES: parseInt,
               NUM_ROOMS: parseInt,
               STYLE: null,
               USE_CODE: null,
               ZONING: null
           };

           function toPropName(k) {
               return _.map(k.split(/_+/), function(piece, i) {
                   return (i ? piece[0] : "") + piece.substring(i ? 1 : 0).toLowerCase();
               }).join("");
           }

           return B.Model.extend({
               parse: function(response) {
                   var props = response.properties;

                   _.forEach(propTypes, function(fn, k, i) {
                       if (props[k])
                           props[toPropName(k)] = fn ? fn(props[k]) : props[k];
                   });

                   return _.extend(props, {
                       geom: {coordinates: response.coordinates,
                              type: response.type}
                   });
               }
           }, {
               modelName: "parcel"
           });
       });
