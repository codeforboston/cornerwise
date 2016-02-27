define(["backbone", "app-state", "underscore", "config",
        "utils"],
       function(B, appState, _, config, $u) {
           return B.View.extend({
               previewTemplate: $u.templateWithUrl(
                   "/static/template/proposalDetail.html",
                   {variable: "proposal"}),

               detailsTemplate: $u.templateWithUrl(
                   "/static/template/proposalDetail.html",
                   {variable: "proposal",
                    expanded: true}),

               // Used for proposals that have associated 
               projectPreviewTemplate: $u.templateWithUrl(
                   "/static/template/projectProposalDetail.html",
                   {variable: "proposal"}),

               projectDetailsTemplate: $u.templateWithUrl(
                   "/static/template/projectProposalDetail.html",
                   {variable: "proposal",
                    expanded: true}),

               show: function(proposal, expanded) {
                   var project = proposal.getProject(),
                       template = expanded ?
                           (project ? this.projectPreviewTemplate : this.detailsTemplate) :
                       (project ? this.projectDetailsTemplate : this.previewTemplate),
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
