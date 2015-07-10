define(["backbone", "leaflet", "ref-location"], function(B, L, refLocation) {
    console.log("Creating Permit model.");

    return B.Model.extend({
        idAttribute: "case",

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
            return attrs;
        },

        toJSON: function() {
            var json = B.Model.prototype.toJSON.apply(this, arguments);

            json.refDistance = this.getDistanceToRef().toFixed(1);

            return json;
        },

        getDistance: function(latLng) {
            return L.latLng(latLng).distanceTo(this.get("location"));
        },

        getDistanceToRef: function() {
            try {
                return refLocation.getLatLng().distanceTo(this.get("location"));
            } catch(err) {
                console.log(err);
                return NaN;
            }
        }
    });
});
