/**
 * View responsible for exposing the permit filters to the user.
 */
define(
    ["backbone", "underscore", "ref-location", "utils", "arcgis", "collapsible-view", "spga-filter-view"],

    function(B, _, refLocation, $u, arcgis, CollapsibleView, SPGAFilterView) {
        return B.View.extend({
            el: function() {
                return document.body;
            },

            filterViews: {
                "#spga-filters": { view: SPGAFilterView,
                                   title: "Granting Authority" }
            },

            initialize: function() {
                this.listenTo(refLocation, "change:radius", this.updateRadius)
                    .listenTo(refLocation, "change:geolocating", this.toggleGeolocating);

                var self = this;
                // Construct subview:
                this.subviews = _.map(this.filterViews, function(view, sel) {
                    var subview = new view.view({collection: self.collection});
                    var collapseView =
                            new CollapsibleView({
                                el: self.$(sel)[0],
                                title: view.title,
                                view: subview
                            });
                    return collapseView.render();
                });
            },

            events: {
                "change #desc-filter": "refreshDescriptionFilter",
                "keyup #desc-filter": "descFilterChanged",

                "submit #ref-address-form": "submitAddress",
                "focus #ref-address-form": "removeGuessClass",
                "click #geolocate": "geolocate",
                "change #radius-filter": "updateRadiusFilter",
                "input #radius-filter": "updateRadiusLabel",
                "click #reset": "clearInputs"
            },

            refreshDescriptionFilter: function() {
                var s = ($("#desc-filter").val() || "").trim();
                this.collection.filterByDescriptionString(s);
            },


            descFilterChanged: function(e) {
                var self = this;
                clearTimeout(this._descTimeout);
                this._descTimeout = setTimeout(function() {
                    self.refreshDescriptionFilter();
                }, 200);
            },


            submitAddress: function(e) {
                if (refLocation.get("geolocating"))
                    return false;

                var addr = e.target.elements["address"].value;

                refLocation.setFromAddress(addr).fail(function(err) {
                    // Indicate to the user why geocoding failed.
                });

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
                return refLocation.setFromBrowser().then(this.reverseGeocodeAddress);
            },

            updateRadiusFilter: function(e) {
                // Parse the input and convert from feet to meters:
                var val = parseFloat(e.target.value);

                // Verify that the value is sensible:
                if (!isNaN(val) && val > 0) {
                    refLocation.set("radius", val);
                }
            },

            updateRadiusLabel: function(e) {
                var val = e.target.value;
                $("#radius-value").html("" + val + " ft");
            },

            clearInputs: function(e) {
                // Parse the input and convert from feet to meters:
                // Verify that the value is sensible:

                refLocation.set("radius", null);
            },

            toggleGeolocating: function(loc, isGeolocating) {
                $("#ref-address").toggleClass("geolocating", isGeolocating);
            },

            updateRadius: function(loc, newRadius) {
                $("#radius-filter")
                    .val(newRadius)[newRadius ? "removeClass" : "addClass"]("inactive");
                $("#radius-value").html(newRadius ? ("" + newRadius + " ft") : "");
            }
        });
    });
