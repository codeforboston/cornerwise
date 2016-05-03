define(["backbone", "jquery", "utils", "underscore", "app-state"],
       function(B, $, $u, _, appState) {
           var ListView = B.View.extend({
               template: $u.templateWithUrl(
                   "/static/template/list.html",
                   {variable: "collection"}),

               el: "#list-view",

               events: {
                   "click .sort-button": "changeSort",
                   "click a.show-on-map": "showOnMap"
               },

               initialize: function(options) {
                   this.subview = options.subview;
               },

               onFirstShow: function() {
                   var collection = this.collection;
                   this.listenTo(collection, "sort", this.render)
                       .listenTo(collection, "change", this.modelChanged)
                       .listenTo(collection, "add", this.modelAdded)
                       .listenTo(collection, "remove", this.modelRemoved)
                       .listenTo(collection, "update", this.onUpdate);
               },

               changeSort: function(e) {
                   var button = $(e.target),
                       field = button.data("sort"),
                       isDesc = button.is(".sorted.desc");

                   appState.setHashKey("sort", (isDesc ? "" : "-") + field);
                   return false;
               },

               modelChanged: function(name, model) {
                   var activeSort = this.collection.sortField;
                   if (activeSort &&
                       _.contains(_.keys(model.changed), activeSort)) {
                       this.render();
                   } else {
                       var view = this.subviewCache[model.id];

                       if (view) {
                           if (view.modelChanged)
                               view.modelChanged(model);
                           else
                               view.render();
                       }
                   }
               },

               /**
                * @returns {ListView} 
                */
               render: function() {
                   var coll = this.collection,
                       self = this;
                   this.subviewCache = {};

                   this.template(coll,
                                 function(html) {
                                     self.$el.toggleClass("showing",
                                                          self.shouldShow)
                                         .toggleClass("empty", coll.length===0)
                                         .html(html);
                                     coll.each(function(model) {
                                         self.modelAdded(model, coll);
                                     });
                                 });
                   this.onUpdate(coll);

                   return this;
               },

               /**
                * Run when a collection is re-rendered or when a model is added
                * to the active collection.
                *
                * @param {B.Model} model The added model
                * @param {B.Collection} coll The active collection
                */
               modelAdded: function(model, coll) {
                   var view = new this.subview({model: model});
                   this.$el.removeClass("empty");
                   this.$(".contents").append(view.el);
                   this.subviewCache[model.id] = view;
                   view.render();
               },

               modelRemoved: function(model, coll) {
                   var view = this.subviewCache[model.id];

                   if (view) {
                       view.$el.remove();
                       delete this.subviewCache[model.id];
                   }

                   if (coll.length === 0)
                       this.$el.addClass("empty");
               },

               onUpdate: function(coll) {
                   this.$el.toggleClass("empty", coll.length === 0);
                   var info = 
                   this.$(".results-info")
                       .html(coll.length > 0 ?
                             ("Matched " +
                              coll.length + " " +
                              $u.pluralize(coll.length, "proposal")) :
                             "No proposals found.");
               },

               show: function() {
                   this.shouldShow = true;
                   this.render();
               },

               hide: function() {
                   this.shouldShow = false;
                   this.$el.removeClass("showing");
               },

               showOnMap: function(e) {
                   var modelId = e.target.getAttribute("data-model-id"),
                       coll = this.collection;

                   if (!modelId || !coll) return true;

                   var model = coll.get(modelId);

                   if (!model) return true;

                   // This is still incredibly kludgy.
                   coll.setSelection(modelId);
                   appState.setHashKey("view", "main");
                   appState.trigger("shouldFocus", [model], true);
                   return false;
               }
           });

           return ListView;
       });
