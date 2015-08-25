define(["backbone", "leaflet", "ref-location", "config"], function(B, L, refLocation, config) {
    return B.Model.extend({
        idAttribute: "case",

        initialize: function() {
                 this.listenTo(refLocation, "change", this.recalculateDistance)
                .listenTo(this, "change:hovered", this.loadParcel)
                .listenTo(this, "change:selected", this.loadParcel);
        },

        defaults: function() {
            return {
                hovered: false,
                selected: false,

                // excluded will change to true when the permit fails
                // the currently applied filter(s).
                excluded: false,
                // GeoJSON representing the shape of the corresponding
                // tax parcel, if one is found.
                parcel: null
            };
        },

        parse: function(attrs) {
            attrs.submitted = new Date(attrs.submitted);
            attrs.refDistance =
                this.getDistance(attrs.location, refLocation.getLatLng());
            attrs.caseNumber = attrs.caseNumber || attrs.case_number;
            return attrs;
        },

        loadParcel: function(permit) {
            if (this._parcelLoadAttempted)
                return;

            var loc = this.get("location"),
                self = this;

            this._parcelLoadAttempted = true;

            $.getJSON(config.backendURL + "/parcel/at_point",
                      {lat: loc.lat,
                       lng: loc.lng})
                .done(function(parcel) {
                    console.log(parcel);
                    self.set("parcel", parcel);
                })
                .fail(function(error) {
                    console.log(error);
                });
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
        }
    });
});
