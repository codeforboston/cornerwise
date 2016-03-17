/*
 * ProposalsCollection
 */
define(
    ["backbone", "jquery", "underscore", "leaflet", "proposal", "ref-location",
     "selectable", "config", "utils"],
    function(B, $, _, L, Proposal, refLocation, Selectable, config, $u) {
        window.$u = $u;
        return Selectable.extend({
            model: Proposal,

            initialize: function(options) {
                Selectable.prototype.initialize.apply(this, arguments);
                this.appState = options && options.appState;
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

            // Contains the query parameters corresponding to the active filters:
            query: {},

            // The last query to be sent to the server.  Use this to determine
            // whether a change in filters can be satisfied from local data alone.
            lastQuery: {},

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

            filterProjectTypes: function(includeProjects, includeProposals) {
                if (includeProjects && includeProposals) {
                    this.removeFilter("projectTypes");
                    delete this.query.project;
                } else if (includeProjects) {
                    this.addFilter("projectTypes", function(proposal) {
                        return !!proposal.getProject();
                    });
                    this.query.project = "all";
                } else if (includeProposals) {
                    this.addFilter("projectTypes", function(proposal) {
                        return !proposal.getProject();
                    });
                    this.query.project = "null";
                }
                this._includeProjects = includeProjects;
                this._includeProposals = includeProposals;
            },

            includeProjects: function(shouldInclude) {
                this.filterProjectTypes(shouldInclude, this._includeProposals);
            },

            includeProposals: function(shouldInclude) {
                this.filterProjectTypes(this._includeProjects, shouldInclude);
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
            }
        });
    });
