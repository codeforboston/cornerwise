define(["backbone", "config", "leaflet", "jquery", "underscore",
        "ref-location", "ref-marker", "proposal-marker", "layers",
        "info-layer-helper", "routes", "utils"],
       function(B, config, L, $, _, refLocation, RefMarker,
                ProposalMarker, infoLayers, info, routes, $u) {
    return B.View.extend({
        initialize: function() {
            var map = L.map(this.el,
                            {zoomControl: false,
                             minZoom: 13,
                             maxBounds: config.maxBounds}),
                layer = L.tileLayer(config.tilesURL),
                zoningLayer = L.featureGroup(),
                parcelLayer = L.geoJson();

            window.cwmap = map;

            map.fitBounds(config.bounds);

            map.addLayer(layer);
            map.addLayer(parcelLayer);
            map.addLayer(zoningLayer);

            this.map = map;
            this.addBaseLayers(config.baseLayers);
            this.parcelLayer = parcelLayer;
            this.zoningLayer = zoningLayer;

            map.on("moveend", _.bind(this.updateMarkers, this));
            map.on("moveend", function() {
                var center = map.getCenter();
                routes.extendHash({
                    lat: center.lat,
                    lng: center.lng,
                    zoom: map.getZoom()
                });
            });

            // Map from case numbers to L.Markers
            this.caseMarker = {};

            // Place the reference location marker:
            this.placeReferenceMarker();

            // ... and subscribe to updates:
            this.listenTo(this.collection, "add", this.proposalAdded)
                .listenTo(this.collection, "remove", this.proposalRemoved)
                .listenTo(this.collection, "change", this.changed)
                .listenTo(refLocation, "change", this.placeReferenceMarker)
                .listenTo(infoLayers, "change", this.layersChanged);

            routes.onStateChange(_.bind(this.stateChanged, this));

            return this;
        },

        stateChanged: function(newState) {
            var map = this.map;
            if (!map) return;

            var lat = parseFloat(newState.lat),
                lng = parseFloat(newState.lng),
                zoom = parseInt(newState.zoom);

            var currentCenter = map.getCenter(),
                currentZoom = map.getZoom();

            if (zoom !== currentZoom ||
                !$u.closeTo(lat, currentCenter.lat, 0.0000000000001) ||
                !$u.closeTo(lng, currentCenter.lng, 0.0000000000001)) {

                lat = lat || currentCenter.lat;
                lng = lng || currentCenter.lng;
                zoom = zoom || currentZoom;

                map.setView([lat, lng], zoom);
            }
        },

        // Layer ordering (bottom -> top):
        // tiles, base layers, parcel layer, permits layer

        // The Layer Group containing permit markers, set during
        // initialization.
        zoningLayer: null,

        // GeoJSON layer group containing parcel shapes
        parcelLayer: null,

        // Callbacks:
        proposalAdded: function(proposal) {
            var loc = proposal.get("location");

            if (!loc)
                return;

            var marker = new ProposalMarker(proposal),
                proposals = this.collection;

            marker.addTo(this.zoningLayer);

            this.caseMarker[proposal.get("caseNumber")] = marker;

            marker
                .on("mouseover", function(e) {
                    proposal.set({hovered: true});
                })
                .on("mouseout", function(e) {
                    proposal.set({hovered: false});
                })
                .on("click", function(e) {
                    proposals.setSelection(proposal.id);
                });

            this.listenTo(proposal, "change", this.changed);
        },

        proposalRemoved: function(permit) {
            this.getMarkerForPermit(permit)
                .done(function(marker) {
                    this.zoningLayer.removeLayer(marker);
                });

            delete this.caseMarker[permit.get("caseNumber")];
        },

        // Map of case # -> ILayer objects
        parcelLayers: {},

        // Triggered when a child permit changes
        changed: function(change) {
            var self = this,
                excluded = change.get("excluded");

            this.getMarkerForPermit(change)
                .done(function(marker) {
                    if (excluded) {
                        self.zoningLayer.removeLayer(marker);
                    } else {
                        marker.addTo(self.zoningLayer);
                    }

                    if (change.changed.selected) {
                        // self.map.setView(marker.getLatLng(),
                        //                  {animate: false});
                    } else if (change.changed.zoomed) {
                        if (self.map.getZoom() < 18)
                            self.map.setView(marker.get("location"), 17,
                                             {animate: false});
                    }
                });

            // Hide or show parcel outlines:
            var parcelLayer = this.parcelLayers[change.get("caseNumber")];
            if (change.get("selected") || change.get("hovered")) {
                if (!parcelLayer) {
                    var parcel = change.get("parcel");

                    if (!parcel) return;

                    parcelLayer = L.GeoJSON.geometryToLayer(parcel);
                    parcelLayer.setStyle(config.parcelStyle);
                    this.parcelLayers[change.get("caseNumber")] = parcelLayer;
                }

                this.parcelLayer.addLayer(parcelLayer);
            } else if (parcelLayer &&
                       (change.changed.selected === false ||
                        change.changed.hovered === false)) {
                this.parcelLayer.removeLayer(parcelLayer);
            }
        },

        /* Getting information about the markers. */
        getMarkerForPermit: function(permit) {
            var marker = this.caseMarker[permit.get("caseNumber")],
                promise = $.Deferred();

            return marker ? promise.resolve(marker) : promise.fail();
        },

        updateMarkers: function() {
            var map = this.map,
                pLayer = this.zoningLayer;

            if (map.getZoom() >= 17) {
                var bounds = map.getBounds();

                _.each(this.caseMarker, function(marker) {
                    if (!bounds.contains(marker.getLatLng()))
                        return;

                    marker.setZoomed(map.getZoom() - 17);
                });
            } else {
                _.each(this.caseMarker, function(marker) {
                    marker.unsetZoomed();
                });
            }
        },

        // Store a reference to the reference marker
        _refMarker: null,
        _hideRefMarker: false,
        placeReferenceMarker: function(change) {
            var loc = refLocation.getPoint();

            if (!this._hideRefMarker) {
                if (!this._refMarker) {
                    this._refMarker =
                        (new RefMarker(refLocation))
                        .addTo(this.zoningLayer);
                }

                // Recenter
                if (refLocation.get("setMethod") !== "auto") {
                    this.map.setView(loc, Math.max(this.map.getZoom(), 16),
                                     {animate: false});
                }
            }
        },

        zoomToRefLocation: function() {
            var bounds = this._refMarker.getBounds();
            this.map.fitBounds(bounds, {padding: [5, 5]});
        },

        _infoLayers: {},
        layersChanged: function(infoLayer) {
            var id = infoLayer.get("id"),
                color = infoLayer.get("color"),
                layer = this._infoLayers[id];

            if (infoLayer.changed.shown) {
                if (layer) {
                    this.map.addLayer(layer);
                } else {
                    var self = this;
                    infoLayer.getFeatures()
                        .done(function(features) {
                            var layer = info.makeInfoLayer(infoLayer, features);
                            self._infoLayers[id] = layer;
                            self.map.addLayer(layer);

                        });
                }

                return;
            }

            if (!layer) return;

            if (infoLayer.changed.color)
                layer.style({color: color});

            if (infoLayer.changed.shown === false)
                this.map.removeLayer(layer);
        },

        addBaseLayers: function(layers) {
            var self = this;
            _.each(layers, function(layer) {
                $.getJSON(layer.source)
                    .done(function(features) {
                        self.map.addLayer(L.geoJson(features,
                                                    {style: layer.style}));
                    });
            });
        }
    });
});
