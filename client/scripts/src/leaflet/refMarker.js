// This file is probably no longer necessary
define(["leaflet", "config"], function(L, config) {
    return L.FeatureGroup.extend({
        initialize: function(refLoc) {
            var fg = L.FeatureGroup.prototype.initialize.call(this, []);
            var icon = L.icon({iconUrl: "/static/images/cornerwise-owl.png",
                               iconRetinaUrl: "/static/images/cornerwise-owl.png",
                               iconSize: [51, 68]});
            this.marker = L.marker(refLoc.getPoint(),
                                   {icon: icon}).addTo(this);
            refLoc.on("change", this.locationChange, this);

            return fg;
        },

        locationChange: function(refLoc) {
            this.marker.setLatLng(refLoc.getPoint());
        }
    });
});
