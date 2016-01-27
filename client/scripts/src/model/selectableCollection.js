define(["backbone", "underscore", "routes", "utils"],
       function(B, _, routes, $u) {
           /**
            * @constructor
            * A collection that keeps track of which items are selected.
            *
            * Events:
            * - selection (collection, ids)
            *   Triggered when the selection changed
            *   ids: ids of all selected children, including those
            *   that have not yet been loaded.
            *
            * - selectionLoaded (collection, ids, loadedIds)
            *   Triggered when the entire selection is loaded
            *   ids: ids of all selected children
            *
            * - selectionRemoved (collection, ids, selectedIds)
            *   ids: ids of all deselected children
            *   selectedIds: ids of selected children
            *
            * - selectionAdded (collection, ids)
            */
           var SelectableCollection = B.Collection.extend({
               initialize: function() {
                   // The ids of the selected members that are loaded
                   // and available.
                   this.selection = [];
                   // The ids of selected members that are not loaded
                   // yet.
                   this.pending = [];

                   this.on("add", this.onAdd, this);

                   if (this.hashParam) {
                       var self = this;
                       routes.onStateChange(this.hashParam, function(ids, oldIds) {
                           if (!ids) return;

                           ids = _.map(ids.split(","), $u.parseInt10);
                           self.setSelection(ids);
                       });

                       this.on("selection", function(self, sel) {
                           routes.setHashKey(self.hashParam, sel.join(","), true);
                       });
                   }
               },

               /**
                * @param {number|number[]} selection An id or ids of the
                * model(s) to select.
                * @param {?boolean} add
                */
               setSelection: function(selection, add) {
                   if (!_.isArray(selection))
                       selection = [selection];
                   if (add)
                       selection = _.union(this.selection, selection);

                   var deselect = _.difference(this.selection, selection);
                   _.each(deselect,
                          function(id) {
                              var member = this.get(id);
                              if (member)
                                  member.set("selected", false);
                          },
                          this);
                   var select = _.difference(selection, this.selection),
                       pending = [];
                   _.each(select,
                          function(id) {
                              var member = this.get(id);
                              if (member)
                                  member.set("selected", true);
                              else
                                  pending.push(id);
                          },
                          this);

                   pending = _.union(pending, this.pending);
                   this.pending = pending;
                   this.selection = _.difference(selection, pending);

                   if (select.length || deselect.length)
                       this.trigger("selection", this, selection);
                   if (select.length)
                       this.trigger("selectionAdded", this, select);
                   if (deselect.length)
                       this.trigger("selectionRemoved", this, deselect, select);

                   if (!pending.length)
                       this.trigger("selectionLoaded", this, selection, pending);

               },

               onAdd: function(model, coll) {
                   if (_.contains(this.pending, model.id)) {
                       this.pending = _.without(this.pending, model.id);
                       this.selection.push(model.id);
                       this.trigger("selection", this, this.selection);

                       if (!this.pending.length)
                           this.trigger("selectionLoaded", this, this.selection,
                                        [model.id]);

                       model.set("selected", true);
                   }
               },

               addToSelection: function(id) {
                   this.setSelection(id, true);
               },


               getSelectedIndex: function() {
                   var id = this.selection[0];

                   return id ?
                       _.findIndex(this.models, function(m) {
                           return m.id == id;
                       }) : -1;
               },

               selectRelative: function(dir) {
                   var fs = _.values(this.activeFilters);

                   if (fs.length) {
                       var models = this.getFiltered(fs),
                           id = this.selection[0],
                           idx = _.findIndex(models, $u.idIs(id));

                       model = models[idx+dir] ||
                           dir < 0 ? _.last(models) : _.first(models);
                   } else {
                       var idx = this.getSelectedIndex();

                       model = this.at(idx+dir) || this.at(dir < 0 ? -1 : 0);
                   }

                   if (model)
                       this.setSelection(model.id);
                   return model;
               },

               /*
                * @returns {?Model}
                */
               selectNext: function() {
                   this.selectRelative(1);
               },

               /*
                * @returns {?Model}
                */
               selectPrev: function() {
                   this.selectRelative(-1);
               },

               /**
                * @return {Proposal[]}
                */
               getSelection: function() {
                   return _.map(this.selection, this.get, this);
               },

               getSelectionIds: function() {
                   return this.selection;
               },

               // Filters:

               /**
                * Applies each of the functions in the array fs to the
                * proposals in the collection. If any of the functions
                * returns false, the Proposal will be updated: its "excluded"
                * attribute will be set to true.
                *
                * @param {Array} fs
                */
               applyFilters: function(fs) {
                   return this.filter(function(model) {
                       var excluded = model.get("excluded"),
                           shouldExclude = !$u.everyPred(fs, model);

                       // Is the model already excluded, and should it be?
                       if (excluded !== shouldExclude) {
                           model.set("excluded", shouldExclude);
                       }

                       return !shouldExclude;
                   });
               },

               getFiltered: function(fs) {
                   if (!fs) fs = _.values(this.activeFilters);

                   return this.filter(function(model) {
                       return $u.everyPred(fs, model);
                   });
               },

               // A map of string filter names to functions
               activeFilters: {},

               // Reapply all of the active filters.
               refresh: function() {
                   var ms = this.applyFilters(_.values(this.activeFilters));
                   this.trigger("filtered", ms.length);
               },

               addFilter: function(name, f) {
                   this.activeFilters[name] = f;
                   this.refresh();
               },

               removeFilter: function(name) {
                   delete this.activeFilters[name];
                   this.refresh();
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
               }
           });

           return SelectableCollection;
       });
