define(["backbone", "routes", "underscore", "config", "utils"],
       function(B, routes, _, config, $u ) {
           return B.View.extend({
               template: $u.templateWithId("proposal-preview-template",
                                           {variable: "proposal"}),

               setElement: function(elt) {
                   B.View.prototype.setElement.call(this, elt);
                   this.$el.on("click", "a.more",
                               _.bind(this.showDetails, this));
               },

               events: {
                   "click a._details": "showDetails"
               },

               showDetails: function(e) {
                   routes.getDispatcher().trigger("showDetails", this.model.id);
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
