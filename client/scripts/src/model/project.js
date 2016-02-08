define(["backbone", "underscore"],
       function(B, _) {
           function parse10Int(s) {
               return parseInt(s);
           }


           return B.Model.extend({
               urlRoot: "/project/view",

               deptNames: {
                   "DPW": "Department of Public Works",
                   "T&I": "Transportation and Infrastructure"
               },

               defaults: {
                   excluded: false
               },

               parse: function(attrs) {
                   _.each(attrs.budget, function(item) {
                       item.budget = parseFloat(item.budget);
                   });

                   return attrs;
               },

               getName: function() {
                   return this.get("name");
               },

               categoryIcon: function() {
                   var cat = this.get("category").toLowerCase(),
                       brief = cat.replace(/[&\s\-]+/g, "_");
                   return "/static/images/icon/" + brief + ".png";
               },

               departmentName: function() {
                   var dept = this.get("department");
                   return this.deptNames[dept] || dept;
               },

               thumbnail: function() {
                   return this.get("thumbnail") ||
                       "/static/images/cityhall.jpg";
               },

               totalBudget: function() {
                   if (!this._totalBudget) {
                       var budgets = this.get("budget");

                       // Cache the result of the calculation
                       this._totalBudget =
                           _.reduce(budgets,
                                    function(acc, b) {
                                        return acc+b.budget;
                                    }, 0);
                   }

                   return this._totalBudget;
               },

               yearCount: function() {
                   return _.size(this.get("budget"));
               },

               yearRange: function() {
                   var years = _.map( _.keys(this.get("budget")), parse10Int);
                   return [_.min(years), _.max(years)];
               },

               yearStart: function() {
                   return _.min(_.map(_.keys(this.get("budget")), parse10Int));
               },

               getFundingSourceGroups: function() {
                   return _.groupBy(this.get("budget"), "funding_source");
               },

               getFundingSources: function() {
                   return _.uniq(_.without(_.pluck(this.get("budget"), "funding_source"), ""));
               }
           }, {
               modelName: "project"
           });
       });
