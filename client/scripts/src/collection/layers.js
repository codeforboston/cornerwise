define(["backbone", "model/layer", "config", "underscore", "appState"],
       function(B, Layer, config, _, appState ) {
           // Construct a Backbone model for each of the layers:
           var layerModels = _.map(config.layers, function(info) {
               return new Layer(info);
           });

           // Return a singleton collection
           var Layers = B.Collection.extend({
               toggleLayer: function(layer, turnOn) {
                   var layer_id = _.isString(layer) ? layer : layer.id;

                   appState.changeHashKey("lys", function(ids) {
                       var id_list = (ids ? ids.split(",") : []);

                       var in_list = (turnOn === undefined ?
                                      _.contains(id_list, layer_id) :
                                      turnOn);

                       if (_.contains(id_list, layer_id))
                           return _.without(id_list, layer_id);
                       else
                           return id_list.concat([layer_id]);
                   });
               }
           });
           var layers = new Layers(layerModels);

           appState.onStateKeyChange("lys", function(ids) {
               var idList = ids ? ids.split(",") : [];

               layers.each(function(layer) {
                   if (_.contains(idList, layer.id)) {
                       if (!layer.get("shown"))
                           layer.set("shown", true);
                   } else if (layer.get("shown")) {
                       layer.set("shown", false);
                   }
               });
           });

           return layers;
       });
