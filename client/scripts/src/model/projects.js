define(["backbone", "project"],
       function(B, Project) {
           return B.Collection.extend({
               model: Project,

               url: "/project/list"
       });
