/**
 * View responsible for exposing the permit filters to the user.
 */
define(
    ["backbone", "underscore", "jquery", "ref-location", "utils", "arcgis",
     "app-state", "config"],

    function(B, _, $, refLocation, $u, arcgis, appState, config) {
        return B.View.extend({
            el: document.body,

            initialize: function(options) {
                this.mapView = options.mapView;
                this.listenTo(refLocation, "change:radius",
                              this.updateRadius)
                    .listenTo(refLocation, "change:geolocating",
                              this.toggleGeolocating);

                // Show the filter controls?
                appState.onStateKeyChange("fc", function(fc) {
                    this.toggle(fc === "1");
                }, this, true);

                appState.onStateKeyChange(
                    "fa",
                    this.showAttributeFilters, this);

                $("#filter-text").val(appState.getKey("f.text"));

                appState.onStateKeyChange("f", function(filters) {
                    this.onFiltersChange(filters);
                }, this);
            },

            render: function() {

            },

            toggle: function(shouldShow) {
                $("#filter-controls")
                    .toggleClass("expanded", shouldShow)
                    .toggleClass("collapsed", !shouldShow);
            },

            events: {
                "submit #ref-address-form": "submitAddress",
                "focus #ref-address-form": "removeGuessClass",
                "click #geolocate": "geolocate",
                "click #reset": "clearInputs",
                "click #reset-filter-bounds": "clearFilterBounds",
                // Should this be preserved for other methods of input?
                // "change #filter-text": "filterText",
                "keyup #filter-text": "filterText",
                "click #filter-bounds": "filterBounds",
                "change #filter-private": "updateProjectTypeFilter",
                "change #filter-public": "updateProjectTypeFilter",
                "click a.ref-loc": "selectAddress"
            },

            onFiltersChange: function(filters) {
                // Only show the 'Reset' button when there is a bounding box set.
                $("#reset-filter-bounds").toggle(!!filters.box);
                $("#filter-private").prop("checked", filters.projects != "all");
                $("#filter-public").prop("checked", filters.projects != "null");
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

            // Filter the collection to only include models that lie within the
            // visible bounds.
            filterBounds: function() {
                this.collection.filterByViewBox(
                    this.mapView.getMap().getBounds()); 
            },

            updateProjectTypeFilter: function() {
                this.collection.filterByProjectType(
                    $("#filter-private").prop("checked"),
                    $("#filter-public").prop("checked"));
            },

            clearFilterBounds: function() {
                this.collection.filterByViewBox(null);
            }
        });
    });
