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
                this.getDistance(attrs.location, refLocation.getLatLng());
            return attrs;
        },

        getDistance: function(fromLoc, toLoc) {
            try {
                return Math.round(L.latLng(fromLoc).distanceTo(toLoc), 0);
            } catch(err) {
                return NaN;
            }
        },

        getDistanceToRef: function() {
            return this.getDistance(this.get("location"), refLocation.getLatLng());
        },

        recalculateDistance: function() {
            var dist = this.set("refDistance", this.getDistanceToRef());
            console.log(dist);
        }
    });
});
