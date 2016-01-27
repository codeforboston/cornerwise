/**
 * View responsible for exposing the permit filters to the user.
 */
define(
    ["backbone", "underscore", "jquery", "ref-location",
     "utils", "arcgis"],

    function(B, _, $, refLocation, $u, arcgis, CollapsibleView) {
        return B.View.extend({
            el: function() {
                return document.body;
            },

            initialize: function() {
                this.listenTo(refLocation, "change:radius",
                              this.updateRadius)
                    .listenTo(refLocation, "change:geolocating",
                              this.toggleGeolocating);
            },

            events: {
                "submit #ref-address-form": "submitAddress",
                "focus #ref-address-form": "removeGuessClass",
                "click #geolocate": "geolocate",
                "click #reset": "clearInputs",
                "change #filter-text": "filterText"
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
                this.collection.filterByText(this.value);
            }
        });
    });
