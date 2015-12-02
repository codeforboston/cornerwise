define(["backbone", "routes", "underscore", "config",
        "glossary", "utils"],
       function(B, routes, _, config, glossary, $u) {
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
                   var html =
                           glossary.addMarkup(
                               this.template(this.model));

                   this.$el.html(html);
                   return this;
               }
           });
       });
