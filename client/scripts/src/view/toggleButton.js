define(["backbone", "app-state"],
       function(B, appState) {
           var ToggleButtonView = B.View.extend({
               tagName: "a",
               className: function() {
                   return "toggle-button " + this.typeClass;
               },

               events: {
                   "click": "onClick"
               },

               initialize: function(options) {
                   B.View.prototype.initialize.apply(this, arguments);

                   var fparam = options.filterParam;

                   this.title = options.title;
                   this.typeClass = options.typeClass || "";

                   if (fparam) {
                       this.selected = appState.getKey(["f", fparam]);
                       this.filterParam = fparam;

                       var self = this;
                       appState.onStateChange(["f", fparam], function(v) {
                           self.selected = v == "1";
                           self.render();
                       });
                   }
                   else if (options.selected !== undefined)
                       this.selected = options.selected;
               },

               onClick: function(e) {
                   if (this.filterParam) {
                       appState.setHashKey(["f", this.filterParam],
                                           this.selected ? "0" : "1");
                   } else {
                       this.selected = !this.selected;
                       this.render();
                   }

                   return false;
               },

               render: function() {
                   this.$el.toggleClass("toggled-on", this.selected)
                       .text(this.title);
               }
           });

           return ToggleButtonView;
       });
