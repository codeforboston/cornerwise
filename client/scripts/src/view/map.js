define(["backbone", "config", "leaflet", "jquery", "underscore",
        "ref-location", "ref-marker", "proposal-marker", "layers",
        "regions", "info-layer-helper", "app-state", "utils"],
       function(B, config, L, $, _, refLocation, RefMarker,
                ProposalMarker, infoLayers, regions, info, appState, $u) {
    return B.View.extend({
        initialize: function() {
            var state = appState.getState(),
                mapOptions = {minZoom: 13,
                              maxBounds: config.bounds},
                lat = parseFloat(state.lat),
                lng = parseFloat(state.lng),
                zoom = parseInt(state.zoom),
                bounds = null;

            if (_.isFinite(lat) && _.isFinite(lng))
                mapOptions.center = L.latLng(lat, lng);
            else
                mapOptions.center = config.refPointDefault;

            if (_.isFinite(zoom))
                mapOptions.zoom = zoom;
            else 
                mapOptions.zoom = 14;

            var map = L.map(this.el, mapOptions),
                layer = L.tileLayer(config.tilesURL),
                zoningLayer = L.featureGroup(),
                parcelLayer = L.geoJson();

            this.map = map;

            map.addLayer(layer);
            map.addLayer(parcelLayer);
            map.addLayer(zoningLayer);

            this.parcelLayer = parcelLayer;
            this.zoningLayer = zoningLayer;

            map.on("moveend", _.bind(this.updateMarkers, this));
            map.on("moveend", function() {
                var center = map.getCenter();
                appState.extendHash({
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
            // Reference location marker:
                .listenTo(refLocation, "change", this.placeReferenceMarker)
            // Informational overlays:
                .listenTo(infoLayers, "change", this.layersChanged)
            // Region base layers:
                .listenTo(regions, "selectionLoaded", this.showRegions)
                .listenTo(regions, "selectionRemoved", this.removeRegions)
            // App behaviors:
                .listenTo(appState, "shouldFocus", this.onFocused);

            return this;
        },

        getMap: function() {
            return this.map;
        },

        selectionChanged: function(proposals, ids) {
            var models = _.map(ids, proposals.get, proposals),
                bounds = L.latLngBounds(
                    _.map(models,
                          function(model) {
                              return model.get("location");
                          }));
            this.map.setView(bounds.getCenter());
        },

        regionLayers: {},
        showRegions: function(regions, ids) {
            this.map.setMaxBounds(null);

            var self = this,
                bounds = L.latLngBounds([]),
                deferredBounds = $.Deferred(),
                completeCount = 0,
                deferreds = _.map(ids, function(id) {
                    var regionInfo = regions.get(id);

                    if (self.regionLayers[id]) return null;

                    return regionInfo.loadShape()
                        .done(function(shape) {
                            var layer = L.geoJson(shape,
                                                  {style: config.regionStyle});
                            bounds.extend(layer.getBounds());
                            self.regionLayers[id] = layer;
                            self.map.addLayer(layer);

                            if (++completeCount == ids.length)
                                deferredBounds.resolve(bounds);
                        });
                });

            // Fit to visible regions?
            deferredBounds.done(function(bounds) {
                // Need to add padding to the bounds
                // self.map.setMaxBounds(bounds);
            });
        },

        removeRegions: function(_regions, ids) {
            _.each(ids, function(id) {
                var layer = this.regionLayers[id];

                if (layer) {
                    this.map.removeLayer(layer);
                    delete this.regionLayers[id];
                }
            }, this);


            // Refit?
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
                    proposal.set({_hovered: true});
                })
                .on("mouseout", function(e) {
                    proposal.set({_hovered: false});
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
                excluded = change.get("_excluded");

            this.getMarkerForPermit(change)
                .done(function(marker) {
                    if (excluded) {
                        self.zoningLayer.removeLayer(marker);
                    } else {
                        marker.addTo(self.zoningLayer);
                    }
                });

            // Hide or show parcel outlines:
            var parcelLayer = this.parcelLayers[change.get("caseNumber")];
            if (change.get("_selected") || change.get("_hovered")) {
                if (!parcelLayer) {
                    var parcel = change.get("parcel");

                    if (!parcel) return;

                    parcelLayer = L.GeoJSON.geometryToLayer(parcel);
                    parcelLayer.setStyle(config.parcelStyle);
                    this.parcelLayers[change.get("caseNumber")] = parcelLayer;
                }

                this.parcelLayer.addLayer(parcelLayer);
            } else if (parcelLayer &&
                       (change.changed._selected === false ||
                        change.changed._hovered === false)) {
                this.parcelLayer.removeLayer(parcelLayer);
            }
        },

        onFocused: function(models, zoom) {
            var self = this,
                ll = _.map(models, function(model) {
                    var loc = model.get("location");

                    return L.latLng(loc.lat, loc.lng);
                });

            if (models.length == 1) {
                this.map.setView(ll[0], zoom ? 17 : this.map.getZoom());
            } else {
                var bounds = L.latLngBounds(ll);
                this.map.fitBounds(bounds);
            }

        },

        /* Getting information about the markers. */
        getMarkerForPermit: function(permit) {
            var marker = this.caseMarker[permit.get("caseNumber")],
                promise = $.Deferred();

            return marker ? promise.resolve(marker) : promise.fail();
        },

        /**
         * 
         */
        updateMarkers: function() {
            var map = this.map,
                pLayer = this.zoningLayer,
                bounds = map.getBounds(),
                zoom = map.getZoom();

            _.each(this.caseMarker, function(marker) {
                var inBounds = bounds.contains(marker.getLatLng());
                marker.getModel().set("_visible", inBounds);

                if (zoom >= 17) {
                    if (!inBounds)
                        return;
                    marker.setZoomed(zoom - 17);
                } else {
                    marker.unsetZoomed();
                }
            });
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

        resetBounds: function() {
            this.map.fitBounds(config.bounds);
        },

        fitToModels: function(models) {
            var bounds = L.latLngBounds(_.map(models,
                                              function(model) {
                                                  return model.get("location");
                                              }));
            this.map.fitBounds(bounds, {paddingTopLeft: [5, 20],
                                        paddingBottomRight: [5, 40]});
        },

        // Fit the map view to the proposals matching the active filters.
        fitToCollection: function() {
            var coll = this.collection;

            if (!coll.getFiltered) return;
            this.fitToModels(coll.getFiltered());
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
        }
    });
});
