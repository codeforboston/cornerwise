define(["backbone", "chartjs", "utils"],
       function(B, Chart, $u) {
           return {
               colors: [],

               makeData: function(budgets, years, colors) {
                   colors = colors || this.colors;

                   var groups = _.groupBy(budgets, "department"),
                       datasets = _.map(groups, function(group, category, idx) {
                           var totals = _.reduce(group, function(acc, budget) {
                               _.each(years, function(year, i) {
                                   acc[i] = (acc[i]|| 0) + (budget.budget[year] || 0);
                               });
                               return acc;
                           }, []),
                               color = colors[idx],
                               colorPref = "rgba(" + color[0] + "," + color[1] +
                                   "," + color[2];

                           return {
                               label: category,
                               fillColor: colorPref + "0.5)",
                               strokeColor: colorPref + "0.8)",
                               highlightFill: "rgba(220,220,220,0.75)",
                               data: totals
                           };
                   });

                   return {
                       labels: _.map(years,
                                     function(y) { return "FY" + y; }),
                       datasets: datasets
                   };
               },

               drawChart: function(budgets, canvas) {
                   var ctx = canvas.getContext("2d"),
                       start = $u.currentYear()+1,
                       years = _.range(start, start+8),
                       data = this.makeData(budgets, years);

                   return new Chart(ctx).Line(data, {
                       animationSteps: 20,
                       bezierCurve: false,
                       scaleLabel: function(o) {
                           return $u.prettyAmount(o.value);
                       }
                   });
               }
           };
       });
