/*
 * ProposalsCollection
 */
define(
    ["backbone", "jquery", "underscore", "leaflet", "proposal", "ref-location",
     "selectable", "config", "utils", "app-state"],
    function(B, $, _, L, Proposal, refLocation, Selectable, config, $u,
             appState) {
        window.$u = $u;
        return Selectable.extend({
            model: Proposal,

            initialize: function(options) {
                Selectable.prototype.initialize.apply(this, arguments);
                // Contains the query parameters corresponding to the active filters:
                this.query = {};

                // The last query to be sent to the server. Could use this to
                // determine whether a change in filters can be satisfied from
                // local data alone.
                this.lastQuery = {};

                this._includeProjects = this._includeProposals = true;

                appState.onStateChange(
                    "f", _.bind(this.onFiltersChange, this));
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

            sortFields: [
                {name: "Distance",
                 field: "refDistance",
                 desc: false},
                {name: "Last Updated",
                 field: "updated",
                 desc: true}
            ],

            queryFilters: {
                projects: "typeFilter",
                text: "textFilter"
            },

            onFiltersChange: function(newFilters, oldFilters) {
                oldFilters = oldFilters || {};
                var query;

                _.each(newFilters, function(val, key) {
                    if (newFilters[key] !== oldFilters[key] &&
                        this.queryFilters[key]) {

                        if (!query) query = _.clone(this.query);

                        var filter = this[this.queryFilters[key]];
                        filter.call(this, query, val, key, newFilters);
                    }
                }, this);

                if (query) {
                    this.lastQuery = this.query;
                    this.query = query;
                    this.fetch();
                }
            },

            textFilter: function(query, s) {
                query.q = s;
            },

            typeFilter: function(query, val) {
                if (val == "all")
                    query.project = "all";
                else if (val == "null")
                    query.project = "null";
                else
                    delete query.project;
            },

            /**
             * @param {L.LatLngBounds} viewBox Proposals that lie within
             * the viewBox will pass the filter.  All others will be
             * hidden.
             */
            filterByViewBox: function(viewBox) {
                this.query.bounds = [viewBox.getWest(), viewBox.getSouth(),
                                     viewBox.getEast(), viewBox.getNorth()].join(",");
                this.fetch();
            },

            clearViewBoxFilter: function() {
                delete this.query.bounds;
                this.fetch();
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
