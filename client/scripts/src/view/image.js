define(["backbone", "appState", "jquery", "utils"],
       function(B, appState, $, $u) {
           var ImageView = B.View.extend({
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
                           .fail(function() {
                               appState.clearHashKey("image");
                           });
                   } else {
                       this.hide();
                   }
               },

               hide: function() {
                   this.$el.removeClass("displayed");
               },

               render: function(image) {
                   this.$el.html(
                       "<img class='image-zoom' src='" + image.src + "'/>")
                       .addClass("displayed");

                   return this;
               }
           });

           return ImageView;
       });
