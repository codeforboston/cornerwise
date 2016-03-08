/*
 * ProposalsCollection
 */
define(
    ["backbone", "jquery", "underscore", "leaflet", "proposal", "ref-location",
     "selectable", "config", "utils"],
    function(B, $, _, L, Proposal, refLocation, Selectable, config, $u) {
        return Selectable.extend({
            model: Proposal,

            initialize: function() {
                Selectable.prototype.initialize.apply(this, arguments);
            },

            url: function() {
                return config.pzURL + "?" +
                    (_.isEmpty(this.query) ? "" : $u.encodeQuery(this.query));
            },

            parse: function(response) {
                return response.proposals;
            },

            comparator: false,

            selection: null,

            // Used by Selectable:
            hashParam: "ps",

            query: {},

            sortFields: [
                {name: "Distance",
                 field: "refDistance",
                 desc: false},
                {name: "Last Updated",
                 field: "updated",
                 desc: true}
            ],

            filterByText: function(s) {
                var re = new RegExp($u.escapeRegex(s), "i");
                this._filterByRegex(re);

                this.query.q = s;
            },

            _filterByRegex: function(regex) {
                if (regex) {
                    this.addFilter("search", function(proposal) {
                        return regex.exec(proposal.get("address")) ||
                            regex.exec(proposal.getAttributeValue("legal_notice"));
                    });
                } else {
                    this.removeFilter("search");
                }
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

                this.query.bounds = [viewBox.getWest(), viewBox.getSouth(),
                                     viewBox.getEast(), viewBox.getNorth()].join(",");
            },

            clearViewBoxFilter: function() {
                this.removeFilter(viewBox);
                delete this.query.bounds;
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


            // Returns a LatLngBounds object for the proposals that are
            // not excluded.
            getBounds: function() {
                return L.latLngBounds(_.map(this.getFiltered(),
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
