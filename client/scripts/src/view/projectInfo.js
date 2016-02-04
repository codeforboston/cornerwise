define(["backbone", "underscore", "budget", "utils"],
       function(B, _, budget, $u) {
           return B.View.extend({
               previewTemplate: $u.templateWithUrl(
                   "/static/template/projectDetail.html",
                   {variable: "project"}),

               detailsTemplate: $u.templateWithUrl(
                   "/static/template/projectDetail.html",
                   {variable: "project",
                    expanded: true}),

               show: function(project, expanded) {
                   var template = expanded ?
                           this.detailsTemplate :
                           this.previewTemplate,
                       self = this;

                   template(project,
                            function(html) {
                                self.$el.show().html(html);

                                budget.drawChart(project.get("budget"),
                                                 self.$("canvas")[0]);
                            });

                   return this;
               }
           });
       });
