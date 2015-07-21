define(["backbone", "layer", "underscore"], function(B, Layer, _) {
    var layers = [
        {
            id: "glx",
            title: "Green Line Extension",
            source: "/scripts/src/layerdata/glx.geojson",
            color: "green",
            shown: false,
            features: null
        },
        {
            id: "cp",
            title: "Community Path",
            source: "/scripts/src/layerdata/community_path.geojson",
            color: "orange",
            shown: false,
            features: null
        }
    ];


    // Construct a Backbone model for each of the layers:
    var layerModels = _.map(layers, function(info) {
        return new Layer(info);
    });

    // Return a singleton collection
    return new B.Collection(layerModels);
});
