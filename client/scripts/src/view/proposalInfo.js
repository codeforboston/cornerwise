define(["backbone", "app-state", "underscore", "config",
        "utils", "budget"],
       function(B, appState, _, config, $u, budget) {
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
                   if (expanded) proposal.fetch();
                   this.model = proposal;

                   if (proposal.getProject())
                       return this.showProject(proposal, expanded);

                   var template = expanded ?
                           this.detailsTemplate : this.previewTemplate,
                       self = this;

                   template(proposal,
                            function(html) {
                                self.$el.html(html);
                            });
                   return this;
               },

               /**
                * Render a proposal with an associated project.
                */
               showProject: function(proposal, expanded) {
                   console.log("Showing project");
                   var project = proposal.getProject(),
                       template = expanded ?
                           this.projectDetailsTemplate : this.projectPreviewTemplate,
                       self = this;

                   template(proposal,
                            function(html) {
                                self.$el.html(html);
                                var canvas = self.$("canvas")[0];
                                if (canvas)
                                    budget.drawChart(project.budget, canvas);
                            });
                   return this;
               }
           });
       });
