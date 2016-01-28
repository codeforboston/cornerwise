define(["backbone", "routes", "underscore", "config",
        "utils"],
       function(B, routes, _, config, $u) {
           return B.View.extend({
               previewTemplate: $u.templateWithUrl(
                   "/static/template/proposalDetail.html",
                   {variable: "proposal"}),

               detailsTemplate: $u.templateWithUrl(
                   "/static/template/proposalDetail.html",
                   {variable: "proposal",
                    expanded: true}),

               show: function(proposal, expanded) {
                   var template = expanded ?
                           this.detailsTemplate :
                           this.previewTemplate,
                       self = this;

                   this.model = proposal;

                   if (expanded) proposal.fetch();
                   template(proposal,
                            function(html) {
                                if (self.model.id == proposal.id)
                                    self.$el.html(html);
                            });
                   return this;
               }
           });
       });
