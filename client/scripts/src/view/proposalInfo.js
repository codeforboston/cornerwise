/**
 * Defines the 'info view' overlay for a proposal.
 */
define(["jquery", "backbone", "appState", "underscore", "config", "utils",
        "view/budget"],
       function($, B, appState, _, config, $u, budget) {
           return B.View.extend({
               template: $u.templateWithUrl(
                   "/static/template/proposalDetail.html",
                   {variable: "proposal"}),

               show: function(proposal) {
                   proposal.fetch();
                   this.model = proposal;

                   if (proposal.getProject())
                       return this.showProject(proposal);

                   var self = this,
                       promise = $.Deferred();

                   this.template(proposal,
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

                   this.template(proposal,
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
