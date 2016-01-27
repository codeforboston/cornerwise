define(["backbone", "utils", "underscore"],
       function(B, $u, _) {
           return B.View.extend({
               template: $u.templateWithUrl(
                   "/static/template/list.html",
                   {variable: "collection"}),

               el: "#list-view",

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
               },

               onFirstShow: function() {
                   _.each(this.collections, function(coll, name) {
                       this.listenTo(coll, "add", _.partial(this.modelAdded, name))
                           .listenTo(coll, "sort", this.render);
                   }, this);
               },

               switchCollection: function(name) {
                   if (name !== this.activeCollection) {
                       this.activeCollection = name;
                       this.render();
                   }
               },

               render: function() {
                   var name = this.activeCollection,
                       coll = this.collections[name],
                       self = this;

                   this.template(coll,
                                 function(html) {
                                     self.$el.addClass("showing")
                                         .html(html);
                                     coll.each(function(model) {
                                         self.modelAdded(name, model, coll);
                                     });
                                 });
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
       });
