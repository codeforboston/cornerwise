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

            initialize: function() {
                this.listenTo(refLocation, "change", this.updateRadiusFilter);

                var self = this;
                routes.onStateChange(function(state, lastState) {
                    var ids = state.ps;

                    if (!ids) return;

                    ids = _.map(ids.split(","), $u.parseInt10);
                    self.setSelection(ids);
                });

                this.on("selection", function(_, sel) {
                    routes.setHashKey("ps", sel.join(","), true);
                });

                return Selectable.prototype.initialize.call(this);
            },

            fetch: function(opts) {
                return B.Collection.prototype.fetch.call(this, opts);
            },

            parse: function(results) {
                return _.isArray(results) ? results : results.proposals;
            },

            /**
             * @param {String} name
             * @param {Boolean} desc true to sort descending
             */
            sortByField: function(name, desc) {
                var order = desc ? -1 : 1;
                this.sortField = name;
                this.order = order;

                if (!name) {
                    this.comparator = false;
                } else {
                    this.comparator = function(p1, p2) {
                        var v1 = p1.get(name),
                            v2 = p2.get(name);

                        return order * ((v1 > v2) ? 1 : (v2 > v1) ? -1 : 0);
                    };
                    this.sort();
                }
            },

            /**
             * Applies each of the functions in the array fs to the
             * proposals in the collection. If any of the functions
             * returns false, the Proposal will be updated: its "excluded"
             * attribute will be set to true.
             *
             * @param {Array} fs
             */
            applyFilters: function(fs) {
                var count = this.length;
                this.each(function(proposal) {
                    var excluded = proposal.get("excluded"),
                        shouldExclude = !$u.everyPred(fs, proposal);

                    // Is the proposal already excluded, and should it be?
                    if (excluded !== shouldExclude) {
                        proposal.set("excluded", shouldExclude);
                    }
                    if (shouldExclude) --count;
                });

                this.trigger("filtered", count);
            },

            // A map of string filter names to functions
            activeFilters: {},

            // Reapply all of the active filters.
            refresh: function() {
                this.applyFilters(_.values(this.activeFilters));
            },

            addFilter: function(name, f) {
                this.activeFilters[name] = f;
                this.refresh();
            },

            removeFilter: function(name) {
                delete this.activeFilters[name];
                this.refresh();
            },

            filterByDescription: function(regex) {
                if (regex) {
                    this.addFilter("search", function(proposal) {
                        return !!(regex.exec(proposal.get("description")));
                    });
                } else {
                    this.removeFilter("search");
                }
            },

            filterByDescriptionString: function(s) {
                var r = s && new RegExp(s.replace(/([?.*\\()[])/g, "\\$1"), "i");
                this.filterByDescription(r);
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
