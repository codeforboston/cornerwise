define(["backbone", "underscore", "utils"],
       function(B, _, $u) {
           var svgNS = "http://www.w3.org/2000/svg";

           function transformFn(yt, yb, xl, xr) {
               var h = yb - yt,
                   w = xr - xl;

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
               template: $u.templateWithId("project-preview-template",
                                           {variable: "project"}),

               initialize: function(options) {
                   this.listenTo(this.collection,
                                 "change:selected",
                                 this.selectionChanged);
               },

               selectionChanged: function(project) {
                   if (!project) {
                       this.$el.html("");
                       return;
                   }

                   this.$el.show().html(this.template(project));
                   var year = $u.currentYear()+1,
                       svg = this.$("svg.budget-chart"),
                       width = svg.width(),
                       height = svg.height(),
                       bmap = this.buildBudgetMap(
                           project.get("budget"),
                           _.range(year, year+10)),
                       transform = transformFn(10, height-10,
                                               10, width-10);

                   var pointsGroup = this.chartPoints(bmap, transform[0]),
                       pathGroup = this.chartPath(bmap, transform[0]);

                   svg.append(pathGroup)
                       .append(pointsGroup);
               },

               buildBudgetMap: function(budget, years) {
                   var maxy = -Infinity,
                       bmap = {};

                   _.each(budget, function(item) {
                       if (item.budget > maxy)
                           maxy = item.budget;
                   });

                   // Add missing:
                   var l = years.length;
                   _.each(years, function(year, i) {
                       var b = budget[year] || {};

                       bmap[year] = {
                           x: i/l,
                           y: b.budget ? b.budget/maxy : 0,
                           budget: b.budget || 0,
                           comment: b.comment || ""
                       };
                   });

                   return bmap;
               },

               chartPath: function(bmap, transform) {
                   var path = document.createElementNS(svgNS, "path"),
                       start = transform({x: 0, y: 0}),
                       end = transform({x: 1, y: 0}),
                       pieces = ["M", start[0], start[1]],
                       pos;

                   _.each(bmap, function(budget) {
                       pos = transform(budget);
                       pieces.push("L", pos[0], pos[1]);
                   });

                   pieces.push("L", pos[0], end[1]);

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
                                  "r": "2"})
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
                       if (item.budget > maxy)
                           maxy = item.budget;
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
               }
           });
       });
