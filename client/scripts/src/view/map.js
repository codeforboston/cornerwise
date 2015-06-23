define(["backbone", "config", "leaflet"], function(B, config, L) {

    function styleMarkerForState(marker, isHovered, isSelected) {

    }

    function styleMarker(marker, permit) {
        // Apply the appropriate styles for the marker's current hovered
        // and selection state.
        var isHovered = permit.get("hovered"),
            isSelected = permit.get("selected");

        styleMarkerForState(marker, isHovered, isSelected);
    }

    return B.View.extend({
        initialize: function() {
            var map = L.map(this.el),
                layer = L.tileLayer("http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"),
                zoningLayer = L.layerGroup();

            map.fitBounds(config.bounds);

            map.addLayer(layer);
            map.addLayer(zoningLayer);

            this.map = map;
            this.zoningLayer = zoningLayer;

            // Map from case numbers to L.Markers
            this.caseMarker = {};

            this.listenTo(this.collection, "add", this.permitAdded);
            this.listenTo(this.collection, "remove", this.permitRemoved);

            return this;
        },

        el: function() {
            return document.getElementById(config.mapId);
        },

        // Callbacks:
        permitAdded: function(permit) {
            // What is the actual signature for callbacks??
            var loc = permit.get("location");

            if (!loc)
                return;

            var marker = L.marker(loc);

            marker.addTo(this.zoningLayer);

            this.caseMarker[permit.caseNumber] = marker;

            marker.on("mouseover", function(e) {
                permit.set({hovered: true});
                styleMarker(marker, permit);
            });
            marker.on("mouseout", function(e) {
                permit.set({hovered: false});
                styleMarker(marker, permit);
            });

            this.listenTo(permit, "change", this.permitChangd);
        },

        permitChanged: function(permit) {
            styleMarker(this.caseMarker[permit.get("caseNumber")], permit);
        },

        permitRemoved: function(permit) {
            var marker = this.getMarkerForPermit(permit);

            marker.removeFrom(this.zoningLayer);

            delete this.caseMarker[permit.get("caseNumber")];
        },

        /* Getting information about the markers. */
        getMarkerForPermit: function(permit) {
            return this.caseMarker[permit.get("caseNumber")];
        }
    });
});
