define(["backbone", "underscore", "app-state", "utils"],
       function(B, _, appState, $u) {
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
            *   Triggered when the entire selection is loaded (meaning that
            *   there is local data for id in the selection).
            *   ids: ids of all selected children
            *
            * - selectionRemoved (collection, ids, selectedIds)
            *   ids: ids of all deselected children
            *   selectedIds: ids of selected children
            *
            * - selectionAdded (collection, ids)
            *
            * - filtered (collection, models)
            *   Triggered when filters are applied
            *
            * - addedFiltered (model, collection)
            *   A model was added that matches the active filters
            *
            * - removedFiltered (model, collection)
            *
            * NOTE: Selection ids are always stored as strings.
            */
           var SelectableCollection = B.Collection.extend({

               initialize: function(models, options) {
                   B.Collection.prototype.initialize.call(this, models, options);

                   // The ids of the selected members that are loaded
                   // and available.
                   if (options && options.selection)
                       this.selection = options.selection;
                   else
                       this.selection = [];

                   // The ids of selected members that are not loaded
                   // yet.
                   this.pending = [];

                   this.on("add", this.onAdd, this)
                       .on("remove", this.onRemove, this);

                   if (this.hashParam) {
                       var self = this;
                       appState.onStateChange(this.hashParam, function(ids, oldIds) {
                           ids = ids ? ids.split(",") : [];
                           self._setSelection(ids);
                       });
                   }
               },

               fetch: function() {
                   this.trigger("fetching");
                   var xhr = B.Collection.prototype.fetch.apply(this, arguments);
                   var self = this;
                   xhr.done(function() {
                       self.trigger("fetchingComplete");
                   });
                   return xhr;
               },

               getModelName: function() {
                   return this.model.modelName || "model";
               },

               getAll: function(ids) {
                   return _.map(ids, this.getAll, this);
               },

               setSelection: function(selection) {
                   if (!this.hashParam)
                       return this._setSelection(selection);

                   if (!_.isArray(selection))
                       selection = [selection];

                   appState.setHashKey(this.hashParam,
                                       selection.join(","));
                   return null;
               },

               /**
                * @param {number|number[]} selection An id or ids of the
                * model(s) to select.
                * @param {?boolean} add
                */
               _setSelection: function(selection, add) {
                   if (!_.isArray(selection))
                       selection = [selection];

                   if (add)
                       selection = _.union(this.selection, selection);
                   else
                       this.pending = [];

                   var deselect = _.difference(this.selection, selection);
                   _.each(deselect,
                          function(id) {
                              var member = this.get(id);
                              if (member)
                                  member.set("_selected", false);
                          },
                          this);
                   var select = _.difference(selection, this.selection),
                       pending = [];
                   _.each(select,
                          function(id) {
                              var member = this.get(id);
                              if (member)
                                  member.set("_selected", true);
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
                   // Check if the added model is one we're waiting for:
                   var id = "" + model.id;
                   if (_.contains(this.pending, id)) {
                       this.pending = _.without(this.pending, id);
                       this.selection.push(id);
                       this.trigger("selection", this, this.selection);

                       if (!this.pending.length)
                           this.trigger("selectionLoaded", this, this.selection,
                                        [id]);

                       model.set("_selected", true);
                   }

                   if (this.matchesFilters(model))
                       this.trigger("addedFiltered", model, coll);
               },

               onRemove: function(model, coll) {
                   if (this.matchesFilters(model))
                       this.trigger("removedFiltered", model, coll);

                   var idx = _.indexOf(this.selection, model.id);
                   if (idx > -1)
                       this.selection.splice(idx, 1);
               },

               getSelectedIndex: function() {
                   var id = this.selection[0];

                   return id ?
                       _.findIndex(this.models, $u.idIs(id)) : -1;
               },

               selectRelative: function(dir) {
                   var fs = _.values(this.activeFilters), idx, model;

                   if (fs.length) {
                       var models = this.getFiltered(fs),
                           id = this.selection[0];

                       idx = _.findIndex(models, $u.idIs(id));

                       model = models[idx+dir] ||
                           dir < 0 ? _.last(models) : _.first(models);
                   } else {
                       idx = this.getSelectedIndex();

                       model = this.at(idx+dir) || this.at(dir < 0 ? -1 : 0);
                   }

                   if (model)
                       this.setSelection("" + model.id);
                   return model;
               },

               /*
                * @returns {?Model}
                */
               selectNext: function() {
                   return this.selectRelative(1);
               },

               /*
                * @returns {?Model}
                */
               selectPrev: function() {
                   return this.selectRelative(-1);
               },

               /**
                * @return {Proposal[]}
                */
               getSelection: function() {
                   return $u.keep(this.selection, this.get, this);
               },

               getSelectionIds: function() {
                   return this.selection;
               },

               // Filters:

               /**
                * Applies each of the functions in the array fs to the
                * proposals in the collection. If any of the functions
                * returns false, the Proposal will be updated: its "_excluded"
                * attribute will be set to true.
                *
                * @param {Array} fs
                */
               applyFilters: function(fs) {
                   return this.filter(function(model) {
                       var excluded = model.get("_excluded"),
                           shouldExclude = !$u.everyPred(fs, model);

                       // Is the model already excluded, and should it be?
                       if (excluded !== shouldExclude) {
                           model.set("_excluded", shouldExclude);
                       }

                       return !shouldExclude;
                   });
               },

               matchesFilters: function(model) {
                   var fs = _.values(this.activeFilters);

                   return $u.everyPred(fs, model);
               },

               getFiltered: function() {
                   return this.where({_excluded: false});
               },

               getVisible: function() {
                   return this.where({_excluded: false,
                                      _visible: true});
               },

               // A map of string filter names to functions
               activeFilters: {},

               // Reapply all of the active filters.
               refresh: function() {
                   var ms = this.applyFilters(_.values(this.activeFilters));
                   this.trigger("filtered", this, ms);
               },

               addFilter: function(name, f) {
                   this.activeFilters[name] = f;
                   this.refresh();
               },

               addFilters: function(filterMap) {
                   _.extend(this.activeFilters, filterMap);
                   this.refresh();
               },

               removeFilter: function(name) {
                   delete this.activeFilters[name];
                   this.refresh();
               },

               // Sorting

               /**
                * A map of fieldName -> comparator function
                * 
                */
               comparators: {},
               
               /**
                * @param {String} name
                * @param {Boolean} desc true to sort descending
                */
               sortByField: function(name, desc) {
                   var order = desc ? -1 : 1;
                   this.sortField = name;
                   this.desc = desc;

                   if (!name) {
                       this.comparator = false;
                   } else if (this.comparators[name]) {
                       var cmp = this.comparators[name];
                       this.comparator = desc ?
                           (function(v1, v2) { return -cmp(); }) : cmp;
                       this.sort();
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
