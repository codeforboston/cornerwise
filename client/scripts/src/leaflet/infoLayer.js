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

        pointToLayer: function(infoLayer, feature, latLng) {
            var markerStyle = infoLayer.get("marker"),
                type = markerStyle.type;

            if (type == "circle") {
                return L.circleMarker(latLng, markerStyle);
            }
            return L.marker(latLng, markerStyle);
        },

        makeInfoLayer: function(infoLayer, features) {
            var options = {
                style: _.bind(this.styleFeature, this, infoLayer),
                onEachFeature: _.bind(this.eachFeature, this, infoLayer)
            };

            var markerStyle = infoLayer.get("marker");

            if (markerStyle) {
                options.pointToLayer = _.bind(this.pointToLayer, this, infoLayer);
            }

            return L.geoJson(features, options);
        }
    };
});
