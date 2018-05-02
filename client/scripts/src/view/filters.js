/**
 * View responsible for exposing the permit filters to the user.
 */
define(
    ["backbone", "underscore", "jquery", "refLocation", "collection/regions",
     "utils", "api/arcgis", "api/places", "appState", "config"],

    function(B, _, $, refLocation, regions, $u, arcgis, places, appState, config) {
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
                              this.maybeUpdateAddress);

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

                places.setup(input, placesOptions)
                    .done(function(ac) {
                        self.placesSetup(ac, input);
                        $(input).keypress(function(e) {
                            if (e.which === 13) {
                                e.preventDefault();
                                input.blur();
                            }
                        }).keyup(function(e) {
                            if (e.which === 27) {
                                e.preventDefault();
                                input.blur();
                            }
                        });
                    });
            },

            /**
               Callback to complete the setup of the Google Places API once it
               has fully loaded.
             */
            placesSetup: function(ac, input) {
                var self = this;

                google.maps.event.addListener(ac, "place_changed", function() {
                    self.onPlaceChanged(ac, input);
                });

                // Restrict the Places query to the bounds of the currently
                // active region(s).
                this.listenTo(
                    regions, "regionBounds",
                    function(bounds) {
                        var gbounds = $u.gBounds(bounds);
                        ac.setBounds(gbounds);
                    });
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
                //"submit #ref-address-form": "submitAddress",
                "focus #ref-address-form": "removeGuessClass",
                "click #geolocate": "geolocate",
                "click #reset": "clearInputs",
                "click #reset-filter-bounds": "clearFilterBounds",
                // Should this be preserved for other methods of input?
                // "change #filter-text": "filterText",
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
                $("#filter-private").prop("checked", filters.projects != "all");
                $("#filter-public").prop("checked", filters.projects != "null");
                $("#filter-region").val(filters.region);
                if (filters.lotsize)
                    $("#filter-lotsize").val(filters.lotsize);
                if (filters.status)
                    $("#filter-status").val(filters.status);
            },

            submitAddress: function(e) {
                if (refLocation.get("geolocating"))
                    return false;

                $(e.target).removeClass("error");

                var addr = e.target.elements["address"].value;

                refLocation.setFromAddress(addr).fail(function(err) {
                    $(e.target)
                        .addClass("error")
                        .find(".error-reason").text("Could not locate that address!");
                });

                e.preventDefault();
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
                    refLocation.setFromLatLng(loc.lat(),
                                              loc.lng(),
                                              addr);
                } else {
                    $(input)
                        .addClass("error")
                        .find(".error-reason").text("Could not locate that address!");

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
                return false;
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

            buildRegionSelection: function() {
                var html = regions.map(function(region) {
                    return ("<option value='" + region.id +
                        "'>" + _.escape(region.get("name")) +
                            "</option>");
                });

                $("#filter-region").html(html.join(""));
            },

            updateLotSize: function(e) {
                this.collection.filterByLotSize(e.target.value);
            },

            updateApplicationStatus: function(e) {
                this.collection.filterByApplicationStatus(e.target.value);
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
