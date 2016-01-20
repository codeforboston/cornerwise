define(["backbone", "chartjs", "utils"],
       function(B, Chart, $u) {
           return {
               colors: [],

               makeData: function(budgets, years, options) {
                   options = options || {};
                   var colors = options.colors || this.colors,
                       grouper = options.grouper,
                       groups, datasets;

                   if (grouper) {
                       groups = _.groupBy(budgets, grouper);
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
                   } else {
                       datasets = [{
                           label: "Budget",
                           fillColor: "rgba(0,0,128,0.5)",
                           strokeColor: "rgba(0,0,128,0.8)",
                           highlightFill: "rgba(220,220,220,0.75)",
                           data: _.map(years, function(year) {
                               var b = budgets[year];
                               return b && b.budget || 0;
                           })
                       }];
                   }

                   return {
                       labels: _.map(years,
                                     function(y) { return "FY" + y; }),
                       datasets: datasets
                   };
               },

               drawChart: function(budgets, canvas, options) {
                   var ctx = canvas.getContext("2d"),
                       start = $u.currentYear()+1,
                       years = _.range(start, start+8),
                       data = this.makeData(budgets, years, options);

                   return new Chart(ctx).Bar(data, {
                       animationSteps: 20,
                       barStrokeWidth: 1,
                       bezierCurve: false,
                       scaleLabel: function(o) {
                           return $u.prettyAmount(o.value);
                       },
                       tooltipTemplate: function(o) {
                           return o.label +
                               ": $" + $u.commas(o.value);
                       }
                   });
               }
           };
       });
