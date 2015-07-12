define(["backbone", "leaflet", "ref-location"], function(B, L, refLocation) {
    console.log("Creating Permit model.");

    return B.Model.extend({
        idAttribute: "case",

        initialize: function() {
            this.listenTo(refLocation, "change", this.recalculateDistance);
        },

        defaults: function() {
            return {
                hovered: false,
                selected: false,

                // excluded will change to true when the permit fails
                // the currently applied filter(s).
                excluded: false
            };
        },

        parse: function(attrs) {
            attrs.submitted = new Date(attrs.submitted);
            attrs.refDistance =
                attrs.location && (refLocation.getLatLng()
                                   .distanceTo(attrs.location)
                                   .toFixed(0));
            return attrs;
        },

        getDistance: function(latLng) {
            try {
                return L.latLng(latLng).distanceTo(this.get("location")).toFixed(0);
            } catch(err) {
                console.log(err);
                return NaN;
            }
        },

        getDistanceToRef: function() {
            return this.getDistance(refLocation.getLatLng());
        },

        recalculateDistance: function() {
            this.set("refDistance", this.getDistanceToRef());
        }
    });
});
