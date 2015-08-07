define(["leaflet", "config"], function(L, config) {
    return L.FeatureGroup.extend({
        initialize: function(loc, radius) {
            var fg = L.FeatureGroup.prototype.initialize.call(this, []);
            this.trackResize = true;
            this.circle = L.circle(loc, radius,
                                  {
                                      stroke: true,
                                      color: config.refMarkerColor
                                  }).addTo(this);
            var icon = L.icon({iconUrl: "images/ref-marker@1x.png",
                               iconRetinaUrl: "images/ref-marker@2x.png",
                               iconSize: [15, 15]});
            this.marker = L.marker(loc, {icon: icon}).addTo(this);
            return fg;
        },

        setRadius: function(loc, r) {
            this.circle.setLatLng(loc);
            this.marker.setLatLng(loc);
            this.circle.setRadius(r);
        }
    });
});
