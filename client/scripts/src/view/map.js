define(["backbone", "config", "leaflet", "jquery", "underscore",
        "ref-location", "popup-view", "ref-marker", "layers",
        "info-layer-helper", "recentered-map"],
       function(B, config, L, $, _, refLocation, PopupView, RefMarker,
                infoLayers, info, RecenteredMap) {

    function getMarkerPng(isHovered, isSelected) {
        if(isSelected){
            return "/static/images/marker-active";
        } else if(isHovered){
            return "/static/images/marker-hover";
        } else {
            return "/static/images/marker-normal";
        }
    }

    function getIcon(permit) {
        // Generate an L.icon for a given permit's parameters
        var isHovered = permit.get("hovered"),
            isSelected = permit.get("selected");

        png = getMarkerPng(isHovered, isSelected);

        return L.icon({iconUrl: png + "@1x.png",
                       iconRetinaUrl: png + "@2x.png",
                       iconSize: [48, 55]});
    }

    return B.View.extend({
        initialize: function() {
            var //map = new RecenteredMap(this.el),
                map = L.map(this.el),
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

            // Map from case numbers to L.Markers
            this.caseMarker = {};

            this.listenTo(this.collection, "add", this.permitAdded)
                .listenTo(this.collection, "remove", this.permitRemoved)
                .listenTo(this.collection, "change", this.changed);

            // Place the reference location marker:
            this.placeReferenceMarker();
            // ... and subscribe to updates:
            this.listenTo(refLocation, "change", this.placeReferenceMarker);

            this.listenTo(infoLayers, "change", this.layersChanged);

            zoningLayer.on("popupopen", _.bind(this.popupOpened, this))
                .on("popupclose", _.bind(this.popupClosed, this));

            return this;
        },

        // Layer ordering (bottom -> top):
        // tiles, base layers, parcel layer, permits layer

        // The Layer Group containing permit markers, set during
        // initialization.
        zoningLayer: null,

        // GeoJSON layer group containing parcel shapes
        parcelLayer: null,

        el: function() {
            return document.getElementById(config.mapId);
        },

        popupOpened: function(e) {
            var view = new PopupView({popup: e.popup,
                                      model: this.collection.selected});
            e.popup._view = view;

            view.render();
        },

        popupClosed: function(e) {
            var view = e.popup._view;

            if (view) {
                e.popup._view = null;
                view.destroy();
            }
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
                    permit.selectOrZoom();
                });

            this.listenTo(permit, "change", this.changed);
        },

        permitRemoved: function(permit) {
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
                        marker.setIcon(getIcon(change));
                        marker.addTo(self.zoningLayer);
                    }

                    if (change.changed.selected) {
                        self.map.setView(marker.getLatLng());

                        // The contents are rendered in the popupOpened
                        // callback.
                        marker.unbindPopup().bindPopup("").openPopup();
                    } else if (change.changed.zoomed) {
                        if (self.map.getZoom() < 18)
                            self.map.setZoom(18);
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

        // Store a reference to the reference marker
        _refMarker: null,
        _hideRefMarker: false,
        placeReferenceMarker: function(change) {
            var loc = refLocation.getPoint();

            if (!this._hideRefMarker) {
                if (!this._refMarker) {
                    this._refMarker =
                        (new RefMarker(loc, refLocation.getRadiusMeters()))
                        .addTo(this.zoningLayer);
                } else {
                    this._refMarker.setRadius(loc, refLocation.getRadiusMeters());
                }

                // If the radius has changed, fit the map bounds to the
                // filtered area.
                if (change && change.changed.hasOwnProperty("radius")) {
                    if (change.get("radius")) {
                        this.zoomToRefLocation();
                    } else {
                        // If the radius has been cleared, fit the map
                        // bounds to the feature group:
                        this.map.fitBounds(this.zoningLayer.getBounds(),
                                           {padding: [5, 5]});
                    }
                } else {
                    // Recenter
                    this.map.panTo(loc);
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
