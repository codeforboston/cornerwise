define(["backbone", "underscore"],
       function(B, _) {
           var svgNS = "http://www.w3.org/2000/svg";

           function transformFn(yt, yb, xl, xr) {
               var w = yb - yt,
                   h = xr - xl;

               var tform = function(item) {
                   return [item.x*w + xl, yb - item.y*h];
               };

               var itform = function(pos) {
                   var x = pos[0], y = pos[1];
                   return [(x-xl)/w, (yb-y)/h];
               };

               return [tform, itform];
           }

           return B.View.extend({
               render: function() {

               },

               buildBudgetMap: function(budget, years) {
                   var maxy = -Infinity,
                       bmap = {};

                   _.each(budget, function(item) {
                       if (item > maxy)
                           maxy = item;
                   });

                   // Add missing:
                   var l = years.length;
                   _.each(years, function(year, i) {
                       var b = budget[year] || {};

                       bmap[year] = {
                           x: i/l,
                           y: b.budget/maxy,
                           budget: b.budget || 0,
                           comment: b.comment || ""
                       };
                   });

                   return bmap;
               },

               chartPath: function(bmap, transform) {
                   var path = document.createElementNS(svgNS, "path"),
                       pieces = [];

                   _.each(bmap, function(budget) {
                       var pos = transform(budget.x);
                       pieces.push(pieces.length ? "L" : "M",
                                   pos[0], pos[1]);
                   });

                   $(path).attr({"d": pieces.join(" "),
                                 "class": "chart-path"});

                   return path;
               },

               chartPoints: function(bmap, transform) {
                   var g = document.createElementNS(svgNS, "g");

                   _.each(bmap, function(budget) {
                       var pos = transform(budget),
                           c = document.createElementNS(svgNS, "circle");

                       $(c).attr({"class": "chart-point",
                                  "cx": pos[0],
                                  "cy": pos[1],
                                  "r": "5"})
                           .data("budget", budget);

                       g.appendChild(c);
                   });

                   return g;
               },

               chartXLabels: function(labels, yp, transform) {
                   var g = document.createElementNS(svgNS, "g"),
                       l = labels.length;

                   _.each(labels, function(label, i) {
                       var xp = i/l,
                           pos = transform(xp, yp),
                           t = document.createElementNS(svgNS, "text"),
                           l = document.createElementNS(svgNS, "line");

                       $(t).attr({"class": "chart-label",
                                  "x": pos[0],
                                  "y": pos[1],
                                  "text-anchor": "end",
                                  "transform": ("rotate(" + pos[0] + " " +
                                                pos[1] + " -45)")})
                           .text(label);

                       // Tick mark
                       $(l).attr({"class": "chart-x-tick",
                                  "x1": pos[0] + 2,
                                  "y1": pos[1],
                                  "x2": pos[0] - 2,
                                  "y2": pos[1]});

                       g.appendChild(t);
                       g.appendChild(l);
                   });

                   return g;
               },

               chartYLines: function(count, transform) {
                   var g = document.createElementNS(svgNS, "g"),
                       dy = 1/count;

                   _.times(count, function(i) {
                       var pos1 = transform(0, i*dy),
                           pos2 = transform(1, i*dy),
                           line = document.createElementNS(svgNS, "line");

                       $(line).attr({"class": "chart-line",
                                     "x1": pos1[0],
                                     "y1": pos1[1],
                                     "x2": pos2[0],
                                     "y2": pos2[1]});
                       g.appendChild(line);
                   });

                   return g;
               },

               buildMap: function(budget, years) {
                   var maxy = -Infinity,
                       data = {},
                       bmap = {data: data};

                   _.each(budget, function(item) {
                       if (item > maxy)
                           maxy = item;
                   });

                   var l = years.length;
                   _.each(years, function(year, i) {
                       var b = budget[year];

                       if (b)
                           data[year] = {
                               x: i/l,
                               y: 1-b.budget/maxy,
                               comment: b.comment
                           };
                       else
                           data[year] = {x: i/l, y: 1};
                   });

                   return bmap;
               },

               renderChart: function() {
                   var budget = this.model.get("budget"),
                       maxBudget = _.max(_.pluck(budget, "budget")),
                       startYear = new Date().getFullYear(),
                       year = startYear,
                       l = _.keys(budget).length,
                       i = 0,
                       svgNS = "http://www.w3.org/2000/svg",
                       chart = this.$("svg"),
                       height = chart.height(),
                       width = chart.width(),
                       dw = width/l,
                       dh = height/maxBudget,
                       lastX, lastY;

                   chart = chart[0];

                   while (i < l) {
                       var yearBudget = budget[year] || {budget: 0},
                           circle = document.createElementNS(svgNS, "circle"),
                           x = dw*i,
                           y = dh*yearBudget.budget;

                       circle.setAttribute("class", "budget-point");
                       circle.setAttribute("cx", x);
                       circle.setAttribute("cy", y);
                       circle.setAttribute("r", 10);
                       chart.appendChild(circle);

                       if (lastX && lastY) {
                           var line = document.createElementNS(svgNS, "line");
                           line.setAttribute("x1", lastX);
                           line.setAttribute("y1", lastY);
                           line.setAttribute("x2", x);
                           line.setAttribute("y2", y);
                           line.setAttribute("class", "budget-line");
                           chart.appendChild(line);
                       }

                       lastX = x;
                       lastY = y;

                       if (budget[year++]) ++i;
                   }
               }
           });
       });
