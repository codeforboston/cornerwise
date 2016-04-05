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

                // Used to store the response from the server corresponding to
                // the last query.
                this.resultCache = [];

                this._includeProjects = this._includeProposals = true;

                appState.onStateKeyChange(
                    "f", _.bind(this.onFiltersChange, this));
            },

            url: function() {
                return config.pzURL + "?" +
                    (_.isEmpty(this.query) ? "" : $u.encodeQuery(this.query));
            },

            fetch: function() {
                var xhr = Selectable.prototype.fetch.apply(this, arguments),
                    query = _.clone(this.query),
                    self = this;

                xhr.done(function(response) {
                    self.lastQuery = query;
                    self.resultCache = response.proposals;
                });

                return xhr;
            },

            parse: function(response) {
                return response.proposals;
            },

            comparator: false,

            selection: null,

            // Used by Selectable:
            hashParam: "ps",
            sortParam: "sort",

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

            /**
             * Used to determine whether the new query can be satisfied from the
             * cached results of a previous query. (TODO: There are actually
             * different relationships that could be interesting, so it might be
             * useful to return something other than a boolean here. Some
             * queries have nonoverlapping results, some queries only widen or
             * narrow, some queries overlap.)
             *
             * @param {Object} newQuery
             * @param {Object} oldQuery
             *
             * @param {boolean} true if the results of oldQuery will contain all
             * the results for newQuery
             */
            isNarrowingQuery: function(newQuery, oldQuery) {
                if (!oldQuery) return false;

                if (!newQuery.projects && oldQuery.projects ||
                    newQuery.projects !== oldQuery.projects)
                    return false;

                // Text queries:
                if (!newQuery.text && oldQuery.text)
                    return false;

                if (newQuery.text && oldQuery.text &&
                    !$u.startsWith(oldQuery.text, newQuery.text))
                    return false;

                // Time queries:
                if (newQuery.range !== oldQuery.range) {
                    if (!newQuery.range || !oldQuery.range)
                        return false;
                    var newRange = $u.strToDateRange(newQuery.range),
                        oldRange = $u.strToDateRange(oldQuery.range);

                    if (!newRange || !oldRange ||
                        newRange[0] < oldRange[0] ||
                        newRange[1] > oldRange[0])
                        return false;
                }

                // TODO: Check geographic query bounds:

                return true;
            },

            makePredicate: function(query) {
                var preds = [];

                if (query.text) {
                    var regexp = $u.wordsRegex(query.text);
                    preds.push(function(proposal) {
                        // For now, just match the address:
                        return regexp.exec(proposal.address);
                    });
                }

                if (query.projects == "all") {
                    preds.push(function(proposal) {
                        return !!proposal.project;
                    });
                } else if (query.projects == "null") {
                    preds.push(function(proposal) {
                        return !proposal.project;
                    });
                }

                if (query.range) {
                }

                return function(proposal) {
                    return $u.everyPred(preds, proposal);
                };
            },

            runQuery: function(query) {
                var lastQuery = this.lastQuery;

                if (this.isNarrowingQuery(query, this.lastQuery)) {
                    // Find the results in the local cache.
                    var pred = this.makePredicate(query),
                        found = _.filter(this.resultCache, pred);
                    this.set(found);
                } else {
                    this.fetch();
                }
            },

            updateQuery: function(filters, old) {
                old = old || {};
                var query;

                _.each(filters, function(val, key) {
                    if (filters[key] !== old[key] &&
                        this.queryFilters[key]) {

                        if (!query) query = {};

                        var filter = this[this.queryFilters[key]];
                        filter.call(this, query, val, key, filters);
                    }
                }, this);

                return query;
            },

            onFiltersChange: function(newFilters, oldFilters) {
                var query = this.updateQuery(newFilters, oldFilters);

                if (query) {
                    this.lastQuery = this.query;
                    this.query = query;
                    this.fetch();
                }
            },

            filterByText: function(text) {
                appState.setHashKey("f.q", text);
            },

            textFilter: function(query, s) {
                query.q = s;
            },

            typeFilter: function(query, val) {
                if (/^(all|null)$/.exec(val))
                    query.project = val.toLowerCase();
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
