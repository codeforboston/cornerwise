define(["backbone", "underscore"],
       function(B, _) {
           return B.Model.extend({
               urlRoot: "/project/view",

               getType: function() {
                   return "project";
               },

               parse: function(attrs) {
                   _.each(attrs.budget, function(item) {
                       item.budget = parseFloat(item.budget);
                   });

                   return attrs;
               },

               getThumbnail: function() {
                   return this.get("thumbnail") ||
                       "/static/images/cityhall.jpg";
               },

               totalBudget: function() {
                   var budgets = this.get("budget");

                   return _.reduce(budgets,
                                   function(acc, b) {
                                       return acc+b.budget;
                                   }, 0);
               },

               yearRange: function() {
                   var years = _.map(parseInt, _.keys(this.get("budget")));
                   return [_.min(years), _.max(years)];
               }
           });
       });
