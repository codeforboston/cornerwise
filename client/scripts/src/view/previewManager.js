"use strict";

define(["backbone", "jquery", "underscore"],
       function(B, $, _) {
           return B.View.extend({
               initialize: function(options) {
                   // Map of keys to Views
                   this.previewMap = options.previewMap;
                   // Map of keys to Backbone collections.  Must
                   // implement getSelection() and emit 'selection'
                   // events.
                   this.collections = options.collections;
                   // Object that emits 'viewSelected' events:
                   this.viewSelection = options.viewSelection;
                   // The key of the currently selected view, if any:
                   this.selectedView = options.viewSelection.selected;

                   var el = this.el;
                   _.each(options.previewMap, function(view) {
                       view.setElement(el);
                   });

                   var self = this;
                   _.each(options.collections, function(coll, name) {
                       self.listenTo(coll, "selectionLoaded", self.render);
                   });

                   this.listenTo(options.viewSelection, "viewSelected",
                                 function(key) {
                                     self.selectedView = key;
                                     self.render();
                                 });

                   this.$el.hide();
               },

               getSelection: function() {
                   if (!this.selectedView) return [];

                   return this.collections[this.selectedView].getSelection();
               },

               render: function() {
                   var sel = this.getSelection();

                   if (!sel.length) {
                       this.$el.hide();
                       return this;
                   }

                   var view = this.previewMap[this.selectedView];
                   view.setModel(sel[0]);
                   this.$el.show();
                   view.render();

                   return this;
               }
           });
       });
