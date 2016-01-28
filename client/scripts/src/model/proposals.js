/*
 * ProposalsCollection
 */
define(
    ["backbone", "jquery", "underscore", "leaflet",
     "proposal", "ref-location", "selectable", "routes",
     "config", "utils"],
    function(B, $, _, L, Proposal, refLocation, Selectable, routes, config, $u) {
        return Selectable.extend({
            model: Proposal,

            url: config.pzURL,

            comparator: false,

            selection: null,

            hashParam: "ps",

            initialize: function() {
                this.listenTo(refLocation, "change", this.updateRadiusFilter);

                return Selectable.prototype.initialize.call(this);
            },

            fetch: function(opts) {
                return B.Collection.prototype.fetch.call(this, opts);
            },

            parse: function(results) {
                return _.isArray(results) ? results : results.proposals;
            },

            filterByText: function(s) {
                var re = new RegExp($u.escapeRegex(s), "i");
                this.filterByRegex(re);
            },

            filterByRegex: function(regex) {
                if (regex) {
                    this.addFilter("search", function(proposal) {
                        return regex.exec(proposal.get("address")) ||
                            regex.exec(proposal.getAttributeValue("legal_notice"));
                    });
                } else {
                    this.removeFilter("search");
                }
            },

            filterByRadius: function(refPoint, radius) {
                if (refPoint && radius) {
                    this.addFilter("radius", function(proposal) {
                        var location = proposal.get("location");

                        return location &&
                            L.latLng(location).distanceTo(refPoint) <= radius;
                    });
                } else {
                    this.removeFilter("radius");
                }
            },

            clearRadiusFilter: function() {
                this.removeFilter("radius");
            },


            /**
             * @param {L.LatLngBounds} viewBox Proposals that lie within
             * the viewBox will pass the filter.  All others will be
             * hidden.
             */
            filterByViewBox: function(viewBox) {
                this.addFilter("viewbox", function(proposal) {
                    var location = proposal.get("location");

                    return location && viewBox.contains(location);
                });
            },

            /*
             * @param {Array} spga
             */
            filterByAuthority: function(spga) {
                if (spga) {
                    this.addFilter("spga", function(proposal) {
                        return _.contains(spga, proposal.get("spga"));
                    });
                } else {
                    this.removeFilter("spga");
                }
            },

            filterByTypes: function(types) {
                if (types) {
                    this.addFilter("types", function(proposal) {
                        return _.contains(types, proposal.get("proposal"));
                    });
                } else {
                    this.removeFilter("types");
                }
            },

            updateRadiusFilter: function(loc) {
                var r = loc.getRadiusMeters();
                if (r) {
                    this.filterByRadius(loc.getPoint(), r);
                } else {
                    this.clearRadiusFilter();
                }
            },

            // Returns a LatLngBounds object for the proposals that are
            // not excluded.
            getBounds: function() {
                return L.latLngBounds(_.map(this.where({excluded: false}),
                                            function(p) {
                                                return p.get("location");
                                            }));
            },



            // Called when a child proposal has its "selected" attribute
            // set. Clears the existing selection.
            proposalSelected: function(proposal, selected) {
                if (this.selected && this.selected.id != proposal.id)
                    this.selected.set("selected", false);

                // If the proposal is being deselected, clear selected
                // property.
                this.selected = selected ? proposal : null;
            },

            proposalZoomed: function(proposal, zoomed) {
                if (this.zoomed && this.zoomed.id != proposal.id)
                    this.zoomed.set("zoomed", false);

                this.zoomed = zoomed ? proposal : null;
            }
        });
    });
