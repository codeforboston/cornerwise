define(["backbone", "utils"],
       function(B, $u) {
           var MiniListView = B.View.extend({
               template: $u.templateWithUrl("/static/template/minilist.html"),
               initialize: function(options) {
                   var manager = this.manager = options.manager;
                   var coll = this.collection = options.collection;

                   if (!coll)
                       throw new Error("Expected a collection");

                   this.listenTo(coll, "filtered", this.render)
                       .listenTo(coll, "addedFiltered", this.render)
                       .listenTo(coll, "removedFiltered", this.render)
                       .listenTo(coll, "change:_visible", this.render)
                       .listenTo(window, "resize", this.onWindowResized);
               },

               onWindowResized: function() {

               },

               render: function() {
                   var $el = this.$el,
                       data = {
                           models: this.collection.getVisible(),
                           name: this.collection.getModelName(),
                           param: this.collection.hashParam,
                           showCount: 16
                       };

                   this.template(data, function(html) {
                       $el.html(html);
                   });
               }
           });

           return MiniListView;
       });
