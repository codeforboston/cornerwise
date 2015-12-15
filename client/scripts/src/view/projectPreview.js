define(["backbone", "underscore", "chartjs", "utils"],
       function(B, _, Chart, $u) {
           return B.View.extend({
               template: $u.templateWithId("project-preview-template",
                                           {variable: "project"}),

               setModel: function(project) {
                   if (this.model) {
                       this.stopListening(this.model);
                   }

                   this.model = project;

                   if (!project) return;

                   this.listenTo(project, "change", this.render);
               },

               render: function() {
                   var project = this.model;

                   if (!project) {
                       this.$el.html("");
                       return;
                   }

                   this.$el.show().html(this.template(project));

                   this.drawChart(project.get("budget"), this.$("canvas")[0]);
               },

               makeData: function(budget, years) {
                   return {labels: _.map(years,
                                         function(y) { return "FY" + y; }),
                           datasets: [{
                               label: "Budget",
                               fillColor: "rgba(220,220,220,0.5)",
                               strokeColor: "rgba(220,220,220,0.8)",
                               highlightFill: "rgba(220,220,220,0.75)",
                               highlightStroke: "rgba(220,220,220,1)",
                               data: _.map(years, function(year) {
                                   var b = budget[year];
                                   return b && b.budget || 0;
                               })
                           }]};
               },

               drawChart: function(budget, canvas) {
                   var ctx = canvas.getContext("2d"),
                       cyear = $u.currentYear(),
                       years = _.range(cyear, cyear+8),
                       data = this.makeData(budget, years);

                   console.log(data);

                   new Chart(ctx).Bar(data);
               }
           });
       });
