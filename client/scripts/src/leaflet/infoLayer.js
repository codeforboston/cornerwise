define(["leaflet", "underscore"], function(L, _) {

    function popupOpened(infoLayer, feature, e) {
        var tstring = infoLayer.get("template"),
            template = tstring && _.template(tstring);

        if (template) {
            e.popup.setContent(template(feature.properties));
        }
    }

    return {
        styleFeature: function(infoLayer, feature) {
            return {
                color: infoLayer.get("color")
            };
        },

        eachFeature: function(infoLayer, feature, layer) {
            layer.bindPopup("");
            layer.on("popupopen", _.partial(popupOpened, infoLayer, feature));
        },

        makeInfoLayer: function(infoLayer, features) {
            var layer = L.geoJson(features,
                                  {
                                      style: _.bind(this.styleFeature, this, infoLayer),
                                      onEachFeature: _.bind(this.eachFeature, this, infoLayer)
                                  });
            return layer;
        }
    };
});
