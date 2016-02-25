define(["backbone", "layer", "config", "underscore", "app-state"],
       function(B, Layer, config, _, appState ) {
           // Construct a Backbone model for each of the layers:
           var layerModels = _.map(config.layers, function(info) {
               return new Layer(info);
           });

           // Return a singleton collection
           var layers = new B.Collection(layerModels);

           appState.onStateChange("lys", function(ids) {
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

               appState.changeHashKey("lys", function(ids) {
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
