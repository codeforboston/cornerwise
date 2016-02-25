define(["backbone", "jquery", "utils", "underscore", 
        "app-state"],
       // TODO: Use the collection manager here?
       function(B, $, $u, _, appState) {
           var ListView = B.View.extend({
               template: $u.templateWithUrl(
                   "/static/template/list.html",
                   {variable: "collection"}),

               el: "#list-view",

               events: {
                   "click .sort-button": "changeSort"
               },

               initialize: function(options) {
                   console.assert(
                       _.isEqual(options.manager.getCollectionNames(),
                                 _.keys(options.subviews)),
                       "You must have a matching subview for each " +
                           "collection.");

                   this.manager = options.manager;
                   this.subviews = options.subviews;

                   this.listenTo(this.manager, "activeCollection", this.render);
               },

               onFirstShow: function() {
                   var cm = this.manager;
                   this.listenTo(cm, "sort", this.render)
                       .listenTo(cm, "filtered", this.render)
                       .listenTo(cm, "change", this.modelChanged)
                       .listenTo(cm, "add", this.modelAdded);
               },

               changeSort: function(e) {
                   var button = $(e.target),
                       field = button.data("sort"),
                       isDesc = button.is(".sorted.desc");

                   appState.setHashKey("sort", (isDesc ? "" : "-") + field);
                   return false;
               },

               modelChanged: function(name, model) {
                   var activeSort = this.manager.getCollection().sortField;
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
                   var coll = this.manager.getCollection(),
                       name = this.manager.getCollectionName(),
                       self = this;
                   this.subviewCache = {};
                   this.template(coll,
                                 function(html) {
                                     self.$el.toggleClass("showing",
                                                          self.shouldShow)
                                         .html(html);
                                     _.each(coll.getFiltered(), function(model) {
                                         self.modelAdded(name, model, coll);
                                     });
                                 });

                   return this;
               },

               /**
                * Run when a collection is re-rendered or when a model is added
                * to the active collection.
                *
                * @param {String} name of the active collection
                * @param {B.Model} model The added model
                * @param {B.Collection} coll The active collection
                */
               modelAdded: function(name, model, coll) {
                   var view = new this.subviews[name]({model: model});
                   this.$(".contents").append(view.el);
                   this.subviewCache[model.id] = view;
                   view.render();
               },

               show: function() {
                   this.shouldShow = true;
                   this.render();
               },

               hide: function() {
                   this.shouldShow = false;
                   this.$el.removeClass("showing");
               }
           });

           return ListView;
       });
