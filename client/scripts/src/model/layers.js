define(["backbone", "layer", "config", "underscore", "routes"],
       function(B, Layer, config, _, routes ) {
           // Construct a Backbone model for each of the layers:
           var layerModels = _.map(config.layers, function(info) {
               return new Layer(info);
           });

           // Return a singleton collection
           var layers = new B.Collection(layerModels);

           routes.onStateChange("lys", function(ids) {
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

           layers.on("change:shown", function(layer, isShown) {
               if (!layer.id) return;

               routes.changeHashKey("lys", function(ids) {
                   var idList = ids ? ids.split(",") : [],
                       inList = _.contains(idList, layer.id);

                   if (isShown && !inList) {
                       idList.push(layer.id);
                   } else if (!isShown && inList) {
                       idList = _.without(idList, layer.id);
                   }

                   return idList.join(",") || undefined;
               }, true);
           });

           return layers;
       });
