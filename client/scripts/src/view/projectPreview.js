define(["backbone", "underscore", "utils"],
       function(B, _, $u) {
           var svgNS = "http://www.w3.org/2000/svg";

           function transformFn(yt, yb, xl, xr) {
               var h = yb - yt,
                   w = xr - xl;

               function scaleX(x) { return x*w; }
               function scaleY(y) { return y*h; }
               function tformX(x) { return x*w + xl; }
               function tformY(y) { return yb - y*h; }
               function tform(item) {
                   return [tformX(item.x), tformY(item.y)];
               };

               function itformX(x) {
                   return (x-xl)/w;
               }

               function itformY(y) {
                   return (yb-y)/h;
               }

               function itform(pos) {
                   return [itformX(pos[0]), itformY(pos[1])];
               }

               return {
                   toX: tformX,
                   toY: tformY,
                   toCanvas: tform,
                   fromX: itformX,
                   fromY: itformY,
                   fromCanvas: itform,
                   scaleX: scaleX,
                   scaleY: scaleY
               };
           }

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
                   var year = $u.currentYear()+1,
                       svg = this.$("svg.budget-chart"),
                       width = svg.width(),
                       height = svg.height(),
                       years = _.range(year, year+7),
                       bmap = this.buildBudgetMap(
                           project.get("budget"), years),
                       t = transformFn(20, height-20, 10, width-10),
                       transform = t.toCanvas;

                   var pointsGroup = this.chartPoints(bmap, transform),
                       //pathGroup = this.chartPath(bmap, transform),
                       barsGroup = this.chartBars(bmap, t),
                       labelsGroup = this.chartXLabels(years, 0, transform);

                   svg .append(barsGroup)
                       .append(labelsGroup);
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

                chartBars: function(bmap, t) {
                    var g = document.createElementNS(svgNS, "g"),
                        w = t.scaleX(0.102),
                        overCallback = _.bind(this.onRectMouseover, this),
                        outCallback = _.bind(this.onRectMouseout, this);

                   _.each(bmap, function(budget) {
                       var bar = document.createElementNS(svgNS, "rect"),
                           pos = t.toCanvas(budget);

                       $(bar).attr({width: w,
                                    height: t.scaleY(budget.y),
                                    x: pos[0] - w/2,
                                    y: pos[1],
                                    "class": "chart-bar"})
                           .on("mouseover", budget, overCallback)
                           .on("mouseout", budget, outCallback);

                       g.appendChild(bar);
                    });

                    return g;
                } ,

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
                       len = labels.length;

                   _.each(labels, function(label, i) {
                       var xp = i/len,
                           pos = transform({x: xp, y: yp}),
                           t = document.createElementNS(svgNS, "text"),
                           l = document.createElementNS(svgNS, "line"),
                           fylabel = "FY" + label.toString().slice(-2);

                       $(t).attr({"class": "chart-label",
                                  "x": pos[0],
                                  "y": pos[1]+20, 
                                  "text-anchor": "middle"})
                           .text(fylabel);

                       // Tick mark
                       $(l).attr({"class": "chart-x-tick",
                                  "x1": pos[0],
                                  "y1": pos[1] + 2,
                                  "x2": pos[0],
                                  "y2": pos[1] + 5});

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
               },

               onRectMouseover: function(e) {
                   if (e.target !== e.currentTarget)
                       return;

                   if (this._label)
                       this._label.remove();

                   var item = e.data,
                       rect = $(e.target),
                       svg = rect.closest("svg"),
                       w = parseInt(rect[0].getAttribute("width")),
                       h = parseInt(rect[0].getAttribute("height")),
                       x = parseInt(rect.attr("x")),
                       y = parseInt(rect.attr("y")),

                       labelGroup = $(document.createElementNS(svgNS, "g")),
                       label = $(document.createElementNS(svgNS, "text"));

                   label.attr({"class": "budget-label",
                               "x": x+w/2,
                               "y": 10,
                               "text-anchor": "middle"})
                       .text("$" + $u.commas(item.budget));

                   var lw = label.width();

                   if (x+lw+10 >= svg.width())
                       label.attr("text-anchor", "end");
                   else if (x-lw-10 <= 0)
                       label.attr("text-anchor", "start");

                   if (y-h-10 >= 0) {
                       $(document.createElementNS(svgNS, "line"))
                           .attr({"class": "budget-label-line",
                                  "x1": x+w/2,
                                  "y1": y-h,
                                  "x2": x+w/2,
                                  "y2": 15})
                           .appendTo(labelGroup);
                   }

                   labelGroup.append(label).appendTo(svg);

                   this._label = labelGroup;
               },

               onRectMouseout: function(e) {
                   if (e.target !== e.currentTarget)
                       return;

                   this._label.remove();
               }
           });
       });
