define(["backbone", "utils"],
       function(B, $u) {
           var MiniListView = B.View.extend({
               template: $u.templateWithUrl("/static/template/minilist.html"),
               initialize: function(options) {
                   var coll = this.collection = options.collection;

                   if (!coll)
                       throw new Error("Expected a collection");

                   this.listenTo(coll, "filtered", this.render)
                       .listenTo(coll, "addedFiltered", this.render)
                       .listenTo(coll, "removedFiltered", this.render);
               },

               onSelection: function(collection, ids) {
                   this.loading = true;
                   this.render();
               },

               onSelectionLoaded: function(collection, ids) {
                   this.loading = false;
                   this.render();
               },

               render: function() {
                   var $el = this.$el;

                   this.template({
                       collection: this.collection,
                       name: name},
                            function(html) {
                                $el.html(html);
                            });
               }
           });

           return MiniListView;
       });
