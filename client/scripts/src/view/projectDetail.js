define(["backbone", "underscore", "budget", "utils"],
       function(B, _, budget, $u) {
           return B.View.extend({
               template: $u.templateWithUrl("/static/template/projectDetail.html",
                                            {variable: "project"}),

               initialize: function() {
                   this.collection.on("selection", this.onSelection, this);
                   this.collection.on("selectionLoaded", this.onSelectionLoaded, this);
                   this.model = this.collection.getSelection()[0];
               },

               onSelection: function(_coll, _ids) {
                   this.model = null;
               },

               onSelectionLoaded: function(coll, ids) {
                   this.model = coll.get(ids[0]);
                   this.render();
               },

               setShowing: function(isShowing) {
                   this.showing = isShowing;
                   return this.render();
               },

               render: function() {
                   if (!this.showing || !this.model) {
                       this.$el.hide();
                       return this;
                   }

                   this.$el.show();

                   var self = this;
                   this.template(
                       this.model,
                       function(html) {
                           self.$el.html(html);

                           if (self.model.get("budget"))
                               budget.drawChart(self.model.get("budget"),
                                                self.$("canvas")[0]);
                       });

                   return this;
               },

               show: function() {
                   return this.setShowing(true);
               },

               hide: function() {
                   return this.setShowing(false);
               }
           });
       });
