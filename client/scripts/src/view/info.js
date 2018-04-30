define(["backbone", "underscore", "utils", "appState"],
       function(B, _, $u, appState) {
           /**
            * - defaultView
            */
           return B.View.extend({
               initialize: function(options) {
                   this.subview = options.subview;
                   this.defaultView = options.defaultView;
                   this.currentView = null;
                   this.shouldShow = false;

                   var coll = this.collection;
                   this.listenTo(coll, "selection", this.onSelection)
                       .listenTo(coll, "selectionLoaded", this.onSelectionLoaded)
                       .listenTo(coll, "selectionRemoved", this.onSelectionRemoved)
                       .listenTo(coll, "change", this.modelChanged);
               },

               el: "#info",

               show: function() {
                   this.toggle(true);
               },

               hide: function() {
                   this.toggle(false);
               },

               render: function() {
                   if (!this.shouldShow)
                       return this;

                   var coll = this.collection,
                       view = this.subview || this.defaultView,
                       models = coll ? coll.getSelection() : [],
                       $el = this.$el;

                   $el.removeClass("loading empty");

                   if (this.currentView)
                       this.currentView.setElement(null);

                   if (!models.length) {
                       $el.addClass("default");
                       if (this.defaultView) {
                           this.currentView = this.defaultView;
                           this.defaultView.setElement(this.$(".content"));
                           this.defaultView.render();
                       } else if (this.defaultTemplate) {
                           this.defaultTemplate(null, function(html) { $el.find(".content").html(html); });
                       } else {
                           $el.addClass("empty");
                       }
                   } else {
                       $el.removeClass("default")
                          .addClass("loading");
                       this.currentView = view;
                       view.setElement(this.$(".content"));
                       if (view.showMulti && models.length > 1) {
                           view.showMulti(models);
                       } else {
                           view.show(models[0])
                               .done(function() {
                                   $el.removeClass("loading");
                               });
                       }
                   }

                   return this;
               },

               onSelection: function(coll, ids) {
                   this.$el.addClass("loading").find(".content").html("");
               },

               onSelectionLoaded: function(coll, ids) {
                   this.active = name;
                   this.render();

                   _.each(ids, function(id) {
                       var model = coll.get(id);
                       this.listenTo(model, "change", this.modelChanged);
                   }, this);
               },

               onSelectionRemoved: function(coll, remIds, ids) {
                   if (this.shouldShow)
                       this.render();
               },

               onNav: function(dir) {
                   var coll = this.collection,
                       model;

                   if (coll) {
                       if (dir < 0) {
                           model = coll.selectPrev();
                       } else if (dir > 0) {
                           model = coll.selectNext();
                       }

                       if (!model) return true;

                       appState.focusModels([model]);

                       return false;
                   }

                   return true;
               },

               modelChanged: function(model) {
                   if (_.every(_.keys(model.changed),
                               function(k) { return k[0] == "_"; }))
                       return;

                   this.render();
               },

               toggle: function(shouldShow) {
                   this.shouldShow = shouldShow;
                   this.$el.toggleClass("displayed", !!shouldShow);

                   if (shouldShow)
                       this.render();
               }
           });
       });
