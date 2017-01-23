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
                              this.toggleGeolocating);

                this.buildRegionSelection();

                // Show the filter controls?
                appState.onStateKeyChange("fc", function(fc) {
                    this.toggle(fc === "1");
                }, this, true);

                appState.onStateKeyChange("showmenu", function(show) {
                    this.toggleSideMenu(show == "1");
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
                            if (e.which == 13) {
                                e.preventDefault();
                                input.blur();
                            }
                        });
                    });
            },

            placesSetup: function(ac, input) {
                var self = this;

                google.maps.event.addListener(ac, "place_changed", function() {
                    self.onPlaceChanged(ac, input);
                });

                this.listenTo(
                    regions, "regionBounds",
                    function(bounds) {
                        var gbounds = $u.gBounds(bounds);
                        ac.setBounds(gbounds);
                    });
            },

            toggle: function(shouldShow) {
                $("#filter-controls")
                    .toggleClass("expanded", shouldShow)
                    .toggleClass("collapsed", !shouldShow);
            },

            toggleSideMenu: function(show) {
                $("#side-menu")
                    .toggleClass("expanded", show)
                    .toggleClass("collapsed", !show);
            },

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
