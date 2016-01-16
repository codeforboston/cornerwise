define(["backbone", "underscore", "project", "project-view",
       "selectable"],
       function(B, _, Project, ProjectView, Selectable) {
           return Selectable.extend({
               model: Project,

               url: "/project/list",

               hashParam: "pj",

               parse: function(results) {
                   return results.projects;
               },

               projectSelected: function(project, selected) {
                   if (this.selected && this.selected.id !== project.id)
                       this.selected.set("selected", false);

                   this.selected = selected ? project : null;
               }
           });
       });
