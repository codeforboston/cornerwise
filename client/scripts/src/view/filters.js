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

                var self = this;

                // Show the filter controls?
                appState.onStateKeyChange("fc", function(fc) {
                    self.toggle(fc === "1");
                });

                // Fit to results?
                appState.onStateKeyChange("ftr", function(ftr, oldFtr) {
                    if (ftr === "1") {
                        self.mapView.resetBounds();
                    } else if (oldFtr === "1") {
                        self.mapView.fitToCollection();
                    }
                });

                appState.onStateKeyChange(
                    "fa",
                    _.bind(this.showAttributeFilters, this));

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
                "change #filter-text": "filterText",
                "change #fit-results": "fitResults"
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

            filterText: function(e) {
                this.collection.filterByText(e.target.value);
            },

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
            filterOnBounds: function() {
                this.collection.filterByViewBox(
                    this.mapView.getMap().getBounds()); 
            },

            clearBoundsFilter: function() {
                this.collection.clearViewBoxFilter();
            }
        });
    });
