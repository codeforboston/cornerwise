define(["jquery", "backbone", "lib/leaflet", "refLocation", "config"], function($, B, L, refLocation, config) {
    return B.Model.extend({
        urlRoot: "/proposal/view",

        /**
           When sorting attributes, display these attributes first, in this
           order:
        */
        promoteAttributes: ["applicant_name", "date", "alderman",
                            "applicant_address", "owner_address",
                            "recommendation"],

        initialize: function() {
            this.listenTo(refLocation, "change", this.recalculateDistance)
                .listenTo(this, "change:_hovered", this.onHovered)
                .listenTo(this, "change:_selected", this.onHovered);
        },

        defaults: function() {
            return {
                _hovered: false,
                _selected: false,

                // _excluded will change to true when the permit fails
                // the currently applied filter(s).
                _excluded: false,

                // GeoJSON representing the shape of the corresponding
                // tax parcel, if one is found.
                parcel: null
            };
        },

        parse: function(attrs) {
            attrs.parcelId = attrs.parcel;
            delete attrs.parcel;

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

            attrs.events = _.map(attrs.events, function(event, _i) {
                event.date = new Date(event.date);
                return event;
            }).sort(function(event1, event2) {
                return event2.date.getTime() - event1.date.getTime();
            });

            attrs.attributes = _.indexBy(attrs.attributes || [], "handle");

            return attrs;
        },

        fetch: function(opts) {
            if (this._fetched) {
                return $.Deferred().resolve(this);
            }

            this._fetched = true;

            opts = opts || {};
            var error = opts.error;
            opts.error = function(m, resp, options) {
                if (error)
                    error(m, resp, options);
                m._fetched = false;
            };

            return B.Model.prototype.fetch.call(this, opts);
        },

        fetchIfNeeded: function() {
            var promise = $.Deferred();
            if (!this._fetched)
                this.fetch({
                    success: function(m) {
                        promise.resolve(m);
                    },
                    error: function() {
                        promise.reject();
                    }
                });
            else
                promise.resolve(this);

            return promise;
        },

        onHovered: function(proposal) {
            if (this._parcelLoadAttempted)
                return;

            var loc = this.get("location"),
                pk = this.get("parcelId"),
                self = this;

            this._parcelLoadAttempted = true;

            var query = pk ? {id: pk} : {lat: loc.lat,
                                         lng: loc.lng,
                                         mode: "or",
                                         address: this.get("address")};
            query.attributes = true;

            $.getJSON(config.backendURL + "/parcel/find", query)
                .done(function(parcel) {
                    self.set("parcel", parcel);
                })
                .fail(function(error) {
                    if (error.status === 404) {
                        // There is no matching parcel:
                    }
                });
        },

        getName: function() {
            return this.get("address");
        },

        getOtherAddresses: function() {
            var others = this.get("other_addresses");
            return others ? others.split(";") : [];
        },

        getThumb: function() {
            var images = this.get("images");

            if (images.length)
                return images[0].thumb || images[0].src;

            return config.defaultProposalThumb;
        },

        getImage: function() {
            var images = this.get("images");

            if (images.length)
                return images[0].src;

            return config.defaultProposalThumb;
        },

        getAttribute: function(handle) {
            return this.get("attributes")[handle];
        },

        /**
         * @param {string} handle
         *
         * @returns {?string}
         */
        getAttributeValue: function(handle) {
            var attr = this.getAttribute(handle);

            return attr && attr.value;
        },

        /**
         * Retrieve attribute values for the specified keys in the specified
         * order.
         *
         * @param {string[]} handles
         *
         * @returns {string[]}
         */
        getAttributeValues: function(handles) {
            return _.map(handles, this.getAttributeValue, this);
        },

        _makeHandlerComparator: function(promoted) {
            var m = _.reduce(promoted, function(o, handle, i) {
                o[handle] = i;
                return o;
            }, {});

            return function(a, b) {
                var aIdx = m[a], bIdx = m[b];

                if (aIdx !== undefined && bIdx !== undefined) {
                    return aIdx - bIdx;
                }

                if (aIdx === undefined) {
                    if (bIdx === undefined)
                        return a < b ? -1 : a == b ? 0 : -1;
                    return 1;
                }

                return -1;
            };
        },

        getHandlerCmp: function() {
            if (!this._handlerCmp) {
                this._handlerCmp = this._makeHandlerComparator(this.promoteAttributes);
            }
            return this._handlerCmp;
        },

        getAttributes: function(handles) {
            if (!handles) {
                handles = _.keys(this.get("attributes")).sort(this.getHandlerCmp());
            }

            return _.map(handles, this.getAttribute, this);
        },

        /**
         * Instantly return the current, locally stored value of the
         * given attribute.  If the attribute is not available locally,
         * fetch it from the server and return null.
         */
        getAttributeValueOrFetch: function(handle) {
            var val = this.getAttributeValue(handle);

            if (!val)
                this.fetchAttribute(handle);

            return val;
        },

        /**
         * Get (from local cache) or fetch (from server) the proposal
         * attribute with the given handle.
         *
         * @param {String} handle
         *
         * @return {$.Deferred} that will resolve to an attribute, or
         * null if the attribute is not found.
         */
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

        getProject: function() {
            return this.get("project");
        },

        projectYearRange: function() {
            var project = this.getProject();

            if (!project) return null;

            var years = _.map(_.keys(project.budget),
                              function(s) { return parseInt(s); }).sort(),
                start = years[0],
                end = years.slice(-1)[0];

            if (start === end)
                return "FY " + start;

            return ["FY ", start, "– ", end].join("");
        },

        recalculateDistance: function() {
            this.set("refDistance", this.getDistanceToRef());
        }
    }, {
        // Class properties:
        modelName: "proposal"
    });
});
