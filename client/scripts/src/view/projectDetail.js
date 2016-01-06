define(["named-model-view", "underscore", "routes"],
       function(NamedModelView, _, routes) {
           return NamedModelView.extend({
               tagName: "div",
               className: "project-details",
               initialize: function() {
                   var self = this;
                   routes.onStateChange("view", function(view) {
                       self.setShowing(view === "projectDetails");
                   });
               },

               setShowing: function(isShowing) {
                   this.showing = isShowing;
                   return this.render();
               },

               render: function() {

               },

               dismiss: function(e) {
                   routes.clearHashKey("view");
               },

               show: function(project) {
                   this.model = project;

                   return this.setShowing(true);
               }
           });
       });
