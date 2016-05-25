define(["backbone", "app-state", "jquery", "utils"],
       function(B, appState, $, $u) {
           var ImageView = B.View.extend({
               template: $u.templateWithUrl(
                   "/static/template/imageBox.html",
                   {variable: "image"}),

               events: {
                   "click": "onClick"
               },

               initialize: function() {
                   appState.onStateKeyChange("image",
                                             this.onImageChange,
                                             this);
               },

               onClick: function(e) {
                   if (!$(e.target).closest("img").length) {
                       appState.clearHashKey("image");
                   }
               },

               onImageChange: function(id) {
                   if (id) {
                       var self = this;
                       $.getJSON("/proposal/image", {pk: id})
                           .done(function(image) {
                               self.render(image);
                           })
                           .error(function() {
                               appState.clearHashKey("image");
                           });
                   } else {
                       this.hide();
                   }
               },

               hide: function() {
                   this.$el.hide();
               },

               render: function(image) {
                   var $el = this.$el;
                   this.template(image,
                                 function(html) {
                                     $el.html(html).show();
                                 });

                   return this;
               }
           });

           return ImageView;
       });
