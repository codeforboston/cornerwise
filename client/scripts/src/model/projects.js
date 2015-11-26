define(["backbone", "project", "project-view"],
       function(B, Project, ProjectView) {
           return B.Collection.extend({
               model: Project,

               url: "/project/list",

               parse: function(results) {
                   return results.projects;
               },

               initialize: function() {
                   this.on("change:selected", this.projectSelected);
               },

               projectSelected: function(project, selected) {
                   if (this.selected && this.selected.id !== project.id)
                       this.selected.set("selected", false);

                   this.selected = selected ? project : null;
               }
           });
       });
