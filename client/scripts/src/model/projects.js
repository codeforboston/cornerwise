define(["backbone", "underscore", "project", "selectable"],
       function(B, _, Project, Selectable) {
           return Selectable.extend({
               model: Project,

               url: "/project/list",

               hashParam: "pj",

               sortFields: [
                   {name: "Department",
                    field: "department"}
               ],

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
