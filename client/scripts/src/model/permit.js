define(["backbone", "leaflet", "ref-location", "config"], function(B, L, refLocation, config) {
    return B.Model.extend({
        urlRoot: "/proposal/view",

        getType: function() {
            return "proposal";
        },

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

            if (!attrs.address)
                attrs.address = [attrs.number, attrs.street].join(" ");

            // TODO: Remove this once the migration to the Python
            // backend is complete
            attrs.caseNumber = attrs.caseNumber || attrs.case_number;

            if (!attrs.documents)
                attrs.documents = [];
            if (!attrs.attributes)
                attrs.attributes = [];

            return attrs;
        },

        fetch: function(opts) {
            this._fetched = true;

            opts = opts || {};
            var error = opts && opts.error;
            opts.error = function(m, resp, options) {
                if (error)
                    error(m, resp, options);
                m._fetched = false;
            };

            return B.Model.prototype.fetch.call(this, opts);
        },

        fetchIfNeeded: function() {
            return !this._fetched && this.fetch();
        },

        loadParcel: function(permit) {
            if (this._parcelLoadAttempted)
                return;

            var loc = this.get("location"),
                self = this;

            this._parcelLoadAttempted = true;

            $.getJSON(config.backendURL + "/parcel/find",
                      {lat: loc.lat,
                       lng: loc.lng,
                       attributes: true,
                       mode: "or",
                       address: this.get("address")})
                .done(function(parcel) {
                    self.set("parcel", parcel);
                })
                .fail(function(error) {
                    if (error.status === 404) {
                        // There is no matching parcel:
                    }
                });
        },

        getThumb: function() {
            var images = this.get("images");

            if (images.length)
                return images[0].thumb || images[0].src;

            return null;
        },

        getAttribute: function(handle) {
            var found = null;

            $.each(this.get("attributes"), function(idx, attr) {
                if (attr.handle === handle) {
                    found = attr;
                    return false;
                }

                return true;
            });

            return found;
        },

        getAttributeValue: function(handle) {
            var attr = this.getAttribute(handle);

            return attr && attr.value;
        },

        fetchAttribute: function(handle) {
            var found = this.getAttribute(handle),
                deferred = $.Deferred();

            if (found) {
                deferred.resolve(found);
            } else {
                var self = this;
                this.fetch()
                    .done(function(model) {
                        found = self.getAttribute(handle);
                        if (found)
                            deferred.resolve(found);
                        else
                            deferred.reject();
                    })
                    .fail(function() {
                        deferred.reject();
                    });
            }

            return deferred;
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
        },

        select: function() {
            this.set({selected: true});
        },

        selectOrZoom: function() {
            if (this.get("selected")) {
                if (!this.get("zoomed"))
                    return this.set("zoomed", true);
            } else {
                return this.set("selected", true);
            }

            return this;
        }
    });
});
