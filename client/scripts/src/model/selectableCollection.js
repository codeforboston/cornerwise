define(["backbone", "underscore"],
       function(B) {
           return B.Collection.extend({
               initialize: function() {
                   this.selection = [];
                   this.fullSelection = [];

                   this.on("add", this.onAdd, this);
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
                       this.trigger("selectionRemoved", this, deselect);

                   if (!pending.length)
                       this.trigger("selectionLoaded", this, pending);

               },

               onAdd: function(model, coll) {
                   if (_.contains(this.pending, model.id)) {
                       this.pending = _.without(this.pending, model.id);
                       this.selection.push(model.id);
                       this.trigger("selection", this, this.selection);

                       if (!this.pending.length)
                           this.trigger("selectionLoaded", this, this.pending);
                   }
               },

               addToSelection: function(id) {
                   this.setSelection(id, true);
               },

               getSelectedIndex: function() {
                   var id = this.selection[0];

                   return id ?
                       $u.findIndex(this.models, function(m) {
                           return m.id == id;
                       }) : -1;
               },

               /*
                * @returns {?Model}
                */
               selectNext: function() {
                   var model = this.at(this.getSelectedIndex()+1) ||
                           this.at(0);

                   if (this.model)
                       this.setSelection(model.id);

                   return model;
               },

               /*
                * @returns {?Model}
                */
               selectPrev: function() {
                   var id = this.getSelectedIndex(),
                       model = this.at(id == -1 ? -1 : id-1);

                   if (model)
                       this.setSelection(model.id);

                   return model;
               },

               /**
                * @return {Proposal[]}
                */
               getSelection: function() {
                   return _.map(this.selection,
                                function(id) { return this.get(id); },
                                this);
               }
           });
       });
