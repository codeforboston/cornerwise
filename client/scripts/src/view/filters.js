/**
 * View responsible for exposing the permit filters to the user.
 */
define(
    ["backbone", "underscore", "jquery", "refLocation", "view/alerts",
     "collection/regions", "utils", "api/arcgis", "api/places", "appState",
     "config"],

    function(B, _, $, refLocation, alerts, regions, $u, arcgis, places, appState,
             config) {
        "use strict";

        return B.View.extend({
            el: document.body,

            initialize: function(options) {
                this.mapView = options.mapView;
                this.listenTo(refLocation, "change:radius",
                              this.updateRadius)
                    .listenTo(refLocation, "change:geolocating",
                              this.toggleGeolocating)
                    .listenTo(refLocation, "change:address",
                              this.maybeUpdateAddress)
                    .listenTo(refLocation, "change:lat change:lng",
                              this.locPositionChanged);

                this.buildConfigFilters(config.filters);
                this.buildRegionSelection();

                /**
                   Filters are all stored in the app state, which is 'persisted'
                   in the location hash. Changes to filters must therefore pass
                   through appState first. Here, we subscribe to filter changes
                   made on appState and update the GUI appropriately.
                 */
                appState.onStateKeyChange("showmenu", function(show, oldValue) {
                    if (_.isString(show))
                        this.toggleFiltersMenu(show === "1");
                }, this, true);

                appState.onStateKeyChange(
                    "fa",
                    this.showAttributeFilters, this);

                $("#filter-text").val(appState.getKey("f.text"));

                appState.onStateKeyChange("f", function(filters) {
                    this.onFiltersChange(filters);
                }, this);

                // Google Places Autocomplete setup:
                var self = this,
                    placesOptions = {types: ["geocode"]},
                    input = $("#ref-address-form input")[0];

                var onSubmit = _.bind(this.onSubmit, this);
                $("#ref-address-form").on("submit", onSubmit);

                places.setup(input, placesOptions)
                    .done(function(ac) {
                        $("#ref-address-form")
                            .off("submit", onSubmit)
                            .submit(function(e) {
                                e.preventDefault();
                            });

                        self.placesSetup(ac, input);

                        var cleared = false;
                        $(input).keyup(function(e) {
                            if (e.key === "Escape") {
                                if (cleared) {
                                    input.blur();
                                } else {
                                    self.resetPlaces();
                                    cleared = true;
                                }
                                e.preventDefault();
                            } else if (e.key === "Enter") {
                                e.preventDefault();
                                input.blur();
                            } else {
                                cleared = false;
                            }
                        }).focusin(function() {
                            cleared = false;
                        });
                    });
            },

            /**
               Callback to complete the setup of the Google Places API once it
               has fully loaded.
             */
            placesSetup: function(ac, input) {
                this.placesAutocomplete = ac;
                this.resetPlaces();

                // Restrict the Places query to the bounds of the currently
                // active region(s).
                this.listenTo(
                    regions, "regionBounds",
                    function(bounds) {
                        var gbounds = $u.gBounds(bounds);
                        ac.setBounds(gbounds);
                    });
            },

            resetPlaces: function(disable) {
                if (this.placesAutocomplete) {
                    if (this._placesListener) {
                        google.maps.event.removeListener(this._placesListener);
                        google.maps.event.clearInstanceListeners(this.placesAutocomplete);
                    }

                    if (!disable) {
                        this._placesListener = google.maps.event.addListener(
                            this.placesAutocomplete, "place_changed",
                            _.bind(this.onPlaceChanged, this, this.placesAutocomplete,
                                $("#ref-address-form input")[0]));
                    }
                }

            },

            toggleFiltersMenu: function(show) {
                $("#show-filters-button").toggle(!show);
                $("#hide-filters-button").toggle(show);
                $("#side-menu")
                    .toggleClass("expanded", show)
                    .toggleClass("collapsed", !show);

                if (show) {
                    var self = this;
                    if (!this._hideHandler) {
                        var handler = _.bind(function(e) {
                            if (!$(e.target).closest("#side-menu").length) {
                                appState.setHashKey("showmenu", "0", true);
                                $(document.body).unbind("click", handler);
                                delete self._hideHandler;
                            }
                        }, this);
                        $(document.body).mousedown(handler);
                        this._hideHandler = null;
                    }
                }
            },

            // NOTE Many of these filters do not appear in the UI at this time.
            // They are preserve here for possible later use, since most or all
            // generate the correct Proposal query and have backend support.
            events: {
                "focus #ref-address-form": "removeGuessClass",
                "click #geolocate": "geolocate",
                "click #reset": "clearInputs",
                "click #reset-filter-bounds": "clearFilterBounds",
                // Should this be preserved for other methods of input?
                // "change #filter-text": "filterText",
                "change .filter-selector": "updateFilter",
                "keyup #filter-text": "filterText",
                "search #filter-text": "filterText",
                "change #filter-private": "updateProjectTypeFilter",
                "change #filter-public": "updateProjectTypeFilter",
                "change #filter-region": "updateRegion",
                "change #filter-lotsize": "updateLotSize",
                "change #filter-status": "updateApplicationStatus",
                "click a.ref-loc": "selectAddress"
            },

            onFiltersChange: function(filters) {
                // Only show the 'Reset' button when there is a bounding box set.
                $("#reset-filter-bounds").toggle(!!filters.box);

                _.each(filters, function(v, key) {
                    $("#filter-" + key).val(v || "");
                });
            },

            /**
               Fallback geocoder, used if Google Places fails to, or is slow to, load
             */
            onSubmit: function(e) {
                if (!refLocation.get("geolocating")) {
                    $(e.target).removeClass("error").blur();
                    this.submitAddress(e.target.elements["address"]);
                    e.preventDefault();
                }

                return false;
            },

            submitAddress: function(field) {
                var addr = field.value;

                $(field).blur();
                refLocation.setFromAddress(addr).fail(function(err) {
                    alerts.showNamed("addressNotFound", "geolocError", {address: addr});
                }).done(function(loc) {
                    alerts.dismissMessage("geolocError");
                    $(field).val(loc[2].ShortLabel || addr);
                });

                return false;
            },

            selectAddress: function(e) {
                $("#ref-address-form input").focus();
                e.preventDefault();
            },

            onPlaceChanged: function(ac, input) {
                var place = ac.getPlace(),
                    geo = place.geometry;

                if (geo) {
                    $(input).removeClass("error");
                    var loc = geo.location,
                        addr = places.shortAddress(place);
                    if (!refLocation.setFromLatLng(loc.lat(), loc.lng(), addr)) {
                        alerts.showNamed("notInBounds", "geolocError", {region: regions.getSelectionDescription()});
                    } else {
                        alerts.dismissMessage("geolocError");
                    }
                } else {
                    this.submitAddress(input);
                    this.onSubmit();
                }
                return false;
            },

            /**
             * Given a [lat, long] array, attempt to retrieve an address and
             * set the value of the address input. If reverse geocoding is
             * successful, the address input will have a 'guess' class
             * added.
             */
            reverseGeocodeAddress: function(loc) {
                return arcgis.reverseGeocode(loc[0], loc[1]).done(function(json) {
                    $("#ref-address-form input")
                        .val(json.address.Address)
                        .addClass("guess");
                });
            },

            removeGuessClass: function(e) {
                $(e.target).removeClass("guess");
            },

            /**
             * When the geolocate button is clicked, set the reference
             * location to the user's current location and update the
             * address input with the reverse-geocoded address for that
             * location.
             */
            geolocate: function(e) {
                refLocation.setFromBrowser().then(this.reverseGeocodeAddress);
                e.preventDefault();
            },

            clearInputs: function(e) {
                // Parse the input and convert from feet to meters:
                // Verify that the value is sensible:

                refLocation.set("radius", null);

                e.preventDefault();
                return false;
            },

            toggleGeolocating: function(loc, isGeolocating) {
                $(document.body)
                    .toggleClass("geolocating", isGeolocating);
            },

            maybeUpdateAddress: function(loc, addr) {
                $("#ref-address-form input:not(:focus)").val(addr);
            },

            locPositionChanged: function(loc) {
                if (loc.get("setMethod") == "map")
                    this.reverseGeocodeAddress([loc.get("lat"), loc.get("lng")]);
            },

            filterText: _.debounce(function(e) {
                this.collection.filterByText(e.target.value);
            }, 500),

            // Event handler for "Fit to Results"
            fitResults: function(e) {
                if (e.target.checked) {
                    appState.setHashKey("ftr", "1");
                } else {
                    appState.clearHashKey("ftr");
                }
            },

            // Display the active attribute filters by constructing UI elements.
            showAttributeFilters: function(attrs) {
                var $con = $("#filter-attributes");

                $con.html("");

                _.each(attrs, function(val, handle) {
                    var name = config.attributeNames[handle] || $u.fromUnder(handle);

                    $("<div class='input-group'>" +
                      "<label>" + _.escape(name) + "</label> " +
                      "<input class='input' type='text' value='" +
                      _.escape(val) + "'/></div>").appendTo($con);
                });
            },

            buildConfigFilters: function(filters) {
                var after = $("#filters .group-header");

                _.each(filters, function(filter) {
                    var group = $("<div/>").addClass("filter-group")
                        .attr("id", filter.key + "-filter-group")
                        .data("key", filter.key);
                    group.append($("<label/>")
                                 .addClass("select")
                                 .attr("for", "filter-" + filter.key)
                                 .text(filter.name));

                    switch(filter.type) {
                    case "select":
                        var select = $("<select/>");
                        select.attr({id: "filter-" + filter.key})
                            .addClass("filter-selector");
                        _.each(filter.options, function(option) {
                            select.append($("<option/>").val(option.value).text(option.name));
                        });
                        group.append(select);
                        break;
                    }

                    group.insertAfter(after);
                });
            },

            buildRegionSelection: function() {
                var html = regions.map(function(region) {
                    return ("<option value='" + region.id +
                        "'>" + _.escape(region.get("name")) +
                            "</option>");
                });

                $("#filter-region").html(html.join(""));

                $("#region-filter-group").toggle(regions.length !== 1);
            },

            updateFilter: function(e) {
                var select = $(e.target),
                    group = select.closest(".filter-group"),
                    key = group.data("key");

                if (!key) return;

                this.collection.filterByKey(key, select.val());
            },

            updateRegion: function(e) {
                regions.setSelection([e.target.value]);
            },

            // Filter the collection to only include models that lie within the
            // visible bounds.
            updateProjectTypeFilter: function() {
                this.collection.filterByProjectType(
                    $("#filter-private").prop("checked"),
                    $("#filter-public").prop("checked"));
            }
        });
    });
