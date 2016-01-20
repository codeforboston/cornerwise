define(["backbone", "underscore", "budget", "utils"],
       function(B, _, budget, $u) {
           return B.View.extend({
               template: $u.templateWithId("project-preview-template",
                                           {variable: "project"}),

               setModel: function(project) {
                   if (this.model) {
                       this.stopListening(this.model);
                   }

                   this.model = project;

                   if (!project) return;

                   //this.listenTo(project, "change", this.render);
               },

               render: function() {
                   var project = this.model;

                   if (!project) {
                       this.$el.html("");
                       return this;
                   }

                   this.$el.show().html(this.template(project));

                   budget.drawChart(project.get("budget"), this.$("canvas")[0]);

                   return this;
               }
           });
       });
