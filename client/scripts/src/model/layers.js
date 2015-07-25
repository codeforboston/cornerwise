define(["backbone", "layer", "config", "underscore"], function(B, Layer, config, _) {
    // Construct a Backbone model for each of the layers:
    var layerModels = _.map(config.layers, function(info) {
        return new Layer(info);
    });

    // Return a singleton collection
    return new B.Collection(layerModels);
});
