define(["backbone", "jquery", "utils", "underscore", "appState"],
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
                   if (!_.isEqual(_.keys(options.collections),
                                  _.keys(options.subviews))) {
                       throw new Error("You must have a matching subview " +
                                       "for each collection.");
                   }

                   this.collections = options.collections;
                   this.activeCollection = options.active ||
                       _.keys(options.collections)[0];
                   this.subviews = options.subviews;

                   var self = this;
                   appState.onStateChange("c", function(coll) {
                       self.switchCollection(coll);
                   });
               },

               onFirstShow: function() {
                   _.each(this.collections, function(coll, name) {
                       var callback = _.partial(this.wasSorted, name);
                       this.listenTo(coll, "sort", callback)
                           .listenTo(coll, "filtered", callback);
                   }, this);
               },

               switchCollection: function(name) {
                   if (name !== this.activeCollection &&
                      this.collections[name]) {
                       this.activeCollection = name;
                       this.render();
                   }
               },

               changeSort: function(e) {
                   var button = $(e.target),
                       field = button.data("sort"),
                       isDesc = button.is(".sorted.desc");

                   appState.setHashKey("sort", (isDesc ? "" : "-") + field);
                   return false;
               },

               updateSortButtons: function(newSort) {
                   var desc = newSort[0] == "-",
                       field = desc ? newSort.slice(1) : newSort;

                   this.$(".sort-button")
                       .each(function(button) {
                           if ($(this).data("sort") == field) {
                               $(this)
                                   .addClass("sorted")
                                   .toggleClass("desc", desc);
                           } else {
                               $(this).removeClass("sorted desc");
                           }
                       });
               },

               /*
                * @param {String} name Name of the collection that was sorted. 
                */
               wasSorted: function(name, coll) {
                   if (this.activeCollection !== name)
                       return;

                   this.render();
               },

               /**
                * @returns {ListView} 
                */
               render: function() {
                   var name = this.activeCollection,
                       coll = this.collections[name],
                       self = this;
                   console.log("rendering list");

                   this.template(coll,
                                 function(html) {
                                     self.$el.addClass("showing")
                                         .html(html);
                                     _.each(coll.getFiltered(), function(model) {
                                         self.modelAdded(name, model, coll);
                                     });
                                 });

                   return this;
               },

               modelAdded: function(name, model, coll) {
                   if (name !== this.activeCollection ||
                       !this.shouldShow) {
                       return;
                   }

                   var view = new this.subviews[name]({model: model});
                   this.$(".contents").append(view.el);
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
