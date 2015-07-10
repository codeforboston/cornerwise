define(["backbone", "config", "leaflet", "jquery", "underscore", "ref-location"],
       function(B, config, L, $, _, refLocation) {
    function getMarkerPng(isHovered, isSelected) {
        if(isSelected){
            return "images/marker-active";
        } else if(isHovered){
            return "images/marker-hover";
        } else {
            return "images/marker-normal";
        }

    }

    function getIcon(permit) {
        // Generate an L.icon for a given permit's parameters
        var isHovered = permit.get("hovered"),
            isSelected = permit.get("selected");

        png = getMarkerPng(isHovered, isSelected);

        return L.icon({iconUrl: png + "@1x.png",
                       iconRetinaUrl: png + "@2x.png"});
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

        // The Layer Group containing permit markers
        zoningLayer: null,

        // The layer group containing
        uiLayer: null,

        el: function() {
            return document.getElementById(config.mapId);
        },

        // Callbacks:
        permitAdded: function(permit) {
            // What is the actual signature for callbacks??
            var loc = permit.get("location");

            if (!loc)
                return;

            var normalIcon = getIcon(permit);
            var marker = L.marker(loc, {icon: normalIcon,
                                        riseOnHover: true});

            marker.addTo(this.zoningLayer);

            this.caseMarker[permit.get("caseNumber")] = marker;

            marker
                .on("mouseover", function(e) {
                    permit.set({hovered: true});
                })
                .on("mouseout", function(e) {
                    permit.set({hovered: false});
                })
                .on("click", function(e) {
                    permit.set("selected", true);
                });

            this.listenTo(permit, "change", this.permitChangd);
        },

        // permitChanged: function(permit) {
        //     styleMarker(this.getMarkerForPermit(permit), permit);
        // },

        permitRemoved: function(permit) {
            this.getMarkerForPermit(permit)
                .done(function(marker) {
                    this.zoningLayer.removeLayer(marker);
                });

            delete this.caseMarker[permit.get("caseNumber")];
        },

        // Triggered when a child permit changes
        changed: function(change) {
            var self = this,
                excluded = change.get("excluded");

            this.getMarkerForPermit(change)
                .done(function(marker) {
                    if (excluded) {
                        self.zoningLayer.removeLayer(marker);
                    } else {
                        marker.setIcon(getIcon(change));
                        marker.addTo(self.zoningLayer);
                    }

                    if (change.changed.selected) {
                        self.map.setView(marker.getLatLng());
                    }
                });
        },

        /* Getting information about the markers. */
        getMarkerForPermit: function(permit) {
            var marker = this.caseMarker[permit.get("caseNumber")],
                promise = $.Deferred();

            return marker ? promise.resolve(marker) : promise.fail();
        },

        // Store a reference to the reference marker
        _refMarker: null,
        _hideRefMarker: false,
        placeReferenceMarker: function(change) {
            var loc = refLocation.getPoint();

            if (!this._hideRefMarker) {
                if (!this._refMarker) {
                    this._refMarker = L.circle(loc, refLocation.getRadiusMeters(),
                                               {
                                                   stroke: true,
                                                   color: config.refMarkerColor
                                               }).addTo(this.zoningLayer);
                } else {
                    this._refMarker.setLatLng(loc);
                    this._refMarker.setRadius(refLocation.getRadiusMeters());
                }

                // If the radius has changed, fit the map bounds to the
                // filtered area.
                if (change && change.changed.hasOwnProperty("radius")) {
                    if (change.get("radius")) {
                        this.zoomToRefLocation();
                    } else {
                        // If the radius has been cleared, fit the map
                        // bounds to the feature group:
                        this.map.fitBounds(this.collection.getBounds(),
                                           {padding: [5, 5]});
                    }
                } else {
                    // Recenter
                    this.map.setView(loc, this.map.getZoom(), {animate: true});
                }
            }
        },

        zoomToRefLocation: function() {
            var bounds = this._refMarker.getBounds();
            this.map.fitBounds(bounds, {padding: [5, 5]});
        }
    });
});
