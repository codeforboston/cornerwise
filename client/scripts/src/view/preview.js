define(["backbone", "routes", "underscore", "config", "utils"],
       function(B, routes, _, config, $u ) {
           return B.View.extend({
               template: $u.templateWithId("proposal-preview-template",
                                           {variable: "proposal"}),

               initialize: function() {
                   this.$el.on("click", "a.more",
                               _.bind(this.showDetails, this));

                   window.routes = routes;
               },

               events: {
                   "click a._details": "showDetails"
               },

               showDetails: function(e) {
                   routes.getDispatcher().trigger("showDetails", this.collection.selected.id);
               },

               setModel: function(proposal) {
                   if (this.model) {
                       this.stopListening(this.model);
                   }

                   this.model = proposal;

                   if (!proposal) return;

                   this.listenTo(proposal, "change", this.render);
               },

               render: function() {
                   this.$el.html(this.template(this.model));
               }
           });
       });
