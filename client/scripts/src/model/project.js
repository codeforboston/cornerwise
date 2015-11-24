define(["backbone"],
       function(B) {
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
               }
           });
       });
