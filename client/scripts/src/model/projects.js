define(["backbone", "underscore", "project", "project-view",
       "selectable"],
       function(B, _, Project, ProjectView, Selectable) {
           return Selectable.extend({
               model: Project,

               url: "/project/list",

               parse: function(results) {
                   return results.projects;
               },

               initialize: function() {
                   this.selection = [];
               },

               projectSelected: function(project, selected) {
                   if (this.selected && this.selected.id !== project.id)
                       this.selected.set("selected", false);

                   this.selected = selected ? project : null;
               }
           });
       });
