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
            var icon = L.icon({iconUrl: "/static/images/cornerwise-owl.png",
                               iconRetinaUrl: "/static/images/cornerwise-owl.png",
                               iconSize: [51, 72]});
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
