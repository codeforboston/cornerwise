define(["backbone", "routes", "underscore", "config"],
       function(B, routes, _, config) {
           return B.View.extend({
               initialize: function(options) {
                   this.$el.on("click", "a.more",
                               _.bind(this.showDetails, this));

                   this.listenTo(this.collection, "change:selected",
                                 this.selectionChanged);
                   window.routes = routes;
               },

               events: {
                   "click a._details": "showDetails"
               },

               showDetails: function(e) {
                   routes.getDispatcher().trigger("showDetails", this.collection.selected.id);
               },

               selectionChanged: function(proposal) {
                   var attrs = proposal.attributes;
                   if (!attrs.selected) {
                       this.$el.hide();
                       return;
                   }

                   var thumb = proposal.getThumb();

                   this.$("img.thumb")
                       .show(!!thumb)
                       .attr("src", thumb);
                   this.$(".address").text(attrs.address);

                   var self = this;
                   proposal.fetchAttribute("applicant_name")
                       .done(function(applicant) {
                           self.$(".applicant-name")
                               .text(applicant.value);
                           self.$(".applicant").show();
                       })
                       .fail(function() {
                           self.$(".applicant").hide();
                       });

                   this.$el.show();
               }
           });
       });
