define(["backbone", "config", "leaflet", "zoning-layer"], function(B, config, L, ZoningLayer) {

    return B.View.extend({
        // Callbacks:
        permitAdded: function(permit) {
            // What is the actual signature for callbacks??
            var marker = L.marker(permit.location);

            marker.addTo(this.zoningLayer);

            this.caseMarker[permit.caseNumber] = marker;

            marker.permit = permit;
            marker.on("mouseover", function(e) {
                permit.set({hovered: true});
            });
            marker.on("mouseout", function(e) {
                permit.set({hovered: false});
            });
        },

        permitRemoved: function(permit) {
            var marker = this.getMarkerForPermit(permit);

            marker.permit = null;
            marker.removeFrom(this.zoningLayer);

            delete this.caseMarker[permit.caseNumber];
        },

        /* Getting information about the markers. */
        getMarkerForPermit: function(permit) {
            return this.caseMarker[permit.caseNumber];
        },

        initialize: function() {
            var map = L.map(this.el),
                layer = new L.tileLayer("http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"),
                zoningLayer = new ZoningLayer();

            map.addLayer(layer);
            map.addLayer(zoningLayer);

            this.map = map;
            this.zoningLayer = zoningLayer;

            // Map from case numbers to L.Markers
            this.caseMarker = {};

            this.listenTo(this.collection, "add", this.permitAdded);
            this.listenTo(this.collection, "remove", this.permitRemoved);

            return this;
        }
    });
});
