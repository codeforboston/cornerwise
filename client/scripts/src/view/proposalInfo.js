/**
 * Defines the 'info view' shown at the bottom of the map.
 */
define(["jquery", "backbone", "appState", "underscore", "config", "utils",
        "view/budget"],
       function($, B, appState, _, config, $u, budget) {
           return B.View.extend({
               detailsTemplate: $u.templateWithUrl(
                   "/static/template/proposalDetail.html",
                   {variable: "proposal"}),

               projectDetailsTemplate: $u.templateWithUrl(
                   "/static/template/projectProposalDetail.html",
                   {variable: "proposal"}),

               show: function(proposal) {
                   proposal.fetch();
                   this.model = proposal;

                   if (proposal.getProject())
                       return this.showProject(proposal);

                   var self = this,
                       promise = $.Deferred();

                   this.detailsTemplate(proposal,
                            function(html) {
                                self.$el.html(html);
                                promise.resolve();
                            });

                   return promise;
               },

               /**
                * Render a proposal with an associated project.
                */
               showProject: function(proposal) {
                   var project = proposal.getProject(),
                       self = this,
                       promise = $.Deferred();

                   this.projectDetailsTemplate(proposal,
                            function(html) {
                                self.$el.html(html);
                                var canvas = self.$("canvas")[0];
                                if (canvas)
                                    budget.drawChart(project.budget, canvas,
                                                     {yearCount: 10});
                                promise.resolve();
                            });
                   return promise;
               }
           });
       });
