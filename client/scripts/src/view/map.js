define(["backbone", "config", "leaflet", "ref-location"],
       function(B, config, L, refLocation) {
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
            this.listenTo(this.collection, "change", this.changed);

            // Place the reference location marker:
            this.placeReferenceMarker();
            // ... and subscribe to updates:
            this.listenTo(refLocation, "change", this.placeReferenceMarker);

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

            var normalIcon = L.icon({iconUrl: "images/marker-normal.png"})
            var marker = L.marker(loc, {icon: normalIcon});

            marker.addTo(this.zoningLayer);

            this.caseMarker[permit.get("caseNumber")] = marker;

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
            console.log("changed")
            styleMarker(this.getMarkerForPermit(permit), permit);
        },

        permitRemoved: function(permit) {
            var marker = this.getMarkerForPermit(permit);

            if (marker)
                this.zoningLayer.removeLayer(marker);

            delete this.caseMarker[permit.get("caseNumber")];
        },

        // Triggered when a child permit changes
        changed: function(change) {
            var marker = this.getMarkerForPermit(change);

            if (marker) {
                if (change.get("excluded")) {
                    this.zoningLayer.removeLayer(marker);
                } else {
                    marker.addTo(this.zoningLayer);
                }
            }
        },

        /* Getting information about the markers. */
        getMarkerForPermit: function(permit) {
            return this.caseMarker[permit.get("caseNumber")];
        },

        // Store a reference to the reference marker
        _refMarker: null,
        _hideRefMarker: false,
        placeReferenceMarker: function() {
            var loc = [refLocation.get("lat"),
                       refLocation.get("lng")];
            if (!this._hideRefMarker) {
                if (!this._refMarker) {
                    this._refMarker = L.circle(loc, config.refMarkerRadius,
                                               {
                                                   stroke: true,
                                                   color: config.refMarkerColor
                                               }).addTo(this.zoningLayer);
                } else {
                    this._refMarker.setLatLng(loc);
                }

                // Recenter
                this.map.setView(loc, this.map.getZoom(), {animate: true});
            }
        }
    });
});
