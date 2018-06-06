define(["backbone", "appState", "jquery", "utils"],
       function(B, appState, $, $u) {
           var ImageView = B.View.extend({
               events: {
                   "click": "onClick"
               },

               initialize: function(options) {
                   this.options = options;
                   appState.onStateKeyChange("image", this.onImageChange, this);
                   this._selectedId = null;

                   var self = this;
                   $(document).keyup(function(e) {
                       if (self.showing) {
                           self.onKeyUp(e);
                       }
                   });
               },

               onClick: function(e) {
                   if (!$(e.target).closest("img").length) {
                       appState.clearHashKey("image");
                       e.preventDefault();
                   }
               },

               onImageChange: function(id) {
                   this._selectedId = parseInt(id);

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

               step: function(dir) {
                   if (this.options.step) {
                       var id = this.options.step(this._selectedId, dir);
                       if (id) {
                           appState.setHashKey("image", id);
                       }
                   }
               },

               next: function() { this.step(1); },
               prev: function() { this.step(-1); },

               onKeyUp: function(e) {
                   switch (e.keyCode) {
                   case 37: this.prev(); break;
                   case 39: this.next(); break;
                   default: return;
                   }
                   e.preventDefault();
               },

               hide: function() {
                   this.showing = false;
                   this.$el.removeClass("displayed");
               },

               render: function(image) {
                   this.showing = true;
                   this.$el.html(
                       "<a href='#' class='close'>&times</a>" +
                       "<img class='image-zoom' src='" + image.src + "'/>")
                       .addClass("displayed");

                   return this;
               }
           });

           return ImageView;
       });
