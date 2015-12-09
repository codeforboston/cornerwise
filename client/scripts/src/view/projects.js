define(["backbone", "project-view", "underscore"],
       function(B, ProjectView, _) {
           return B.View.extend({
               title: "Capital Projects",

               initialize: function(options) {
                   // The proposal collection:
                   this.proposals = options.proposals;
               },

               build: function() {
                   if (this._built) return;

                   var projects = this.collection;
                   this.listenTo(projects, "add", this.projectAdded)
                       .listenTo(projects, "reset", this.projectsReset)
                       .listenTo(projects, "change:selected", this.projectSelected);
                   this.$el.html("");
                   this.collection.each(_.bind(this.projectAdded, this));

                   this._built = true;
               },

               projectAdded: function(project) {
                   var view = new ProjectView({model: project}),
                       el = view.render().el,
                       coll = this.collection;

                   this.$el.append(el);
                   view.$el.on("click", function() {
                       coll.setSelection(project.id);
                   });
               },

               projectSelected: function(project, selected) {
                   if (this.selected) {
                       if (this.selected.id == project.id)
                       {
                           if (!selected) {
                               this.selected = null;
                               //this.proposals.setSelection([]);
                           }
                       } else {
                           this.selected.set("selected", false);
                       }
                   }

                   if (selected) {
                       this.selected = project;
                       //this.proposals.setSelection(project.get("proposals"));
                   }
               },

               render: function() {
                   this.build();
               }
           });
       });
