define(["leaflet", "jquery"], function(L, $) {
    return L.FeatureGroup.extend({
        /*
         * @param layerInfo
         */
        initialize: function(layerInfo) {
            if (layerInfo.features) {
                this.addFeatures(layerInfo.features);
            } else {
                $.getJSON(layerInfo.source)
                    .done(function(
            }
        }
    });
});
