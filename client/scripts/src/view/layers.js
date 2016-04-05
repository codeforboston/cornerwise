define(["backbone", "underscore", "jquery", "layers", "utils",
       "app-state"],
       function(B, _, $, layers, $u, appState) {
           var LayerItemView = B.View.extend({
               template: $u.templateWithId("layer-item-template",
                                           {variable: "layer"}),

               tagName: "a",

               attributes: function() {
                   return {href: "#"};
               },

               className: function() {
                   return "layer-button" +
                       (this.model.get("shown") ? " selected" : "");
               },

               events: {
                   "click": "onClick"
               },

               initialize: function() {
                   this.listenTo(this.model, "change", this.render);
               },

               render: function() {
                   this.$el
                       .attr("class", this.className())
                       .html(this.template(this.model));

                   return this;
               },

               onClick: function(e) {
                   e.preventDefault();
                   this.model.collection.toggleLayer(this.model.id);
               }
           });

           return B.View.extend({
               collection: layers,
               hashParam: "ly",
               className: function() {
                   return "blorg";
               },

               initialize: function(options) {
                   B.View.prototype.initialize.call(this, options);

                   var self = this;
                   appState.onStateKeyChange(
                       this.hashParam,
                       function(newLy, oldLy) {
                           if (newLy === "1")
                               self._show();
                           else
                               self._hide();
                       });
               },

               events: {
                   "click .toggle-layers": "toggle"
               },

               toggle: function(e) {
                   appState.changeHashKey(this.hashParam,
                                          function(v) {
                                              return v === "1" ? undefined : "1";
                                          });
                   e.preventDefault();
               },

               show: function() {
                   appState.setHashKey(this.hashParam, "1");
               },

               hide: function() {
                   appState.clearHashKey(this.hashParam);
               },

               _show: function() {
                   this.$el.addClass("expanded");
               },

               _hide: function() {
                   this.$el.removeClass("expanded");
               },

               render: function() {
                   var $el = $("#layers"),
                       div = $('<div class="layer-list"></div>').appendTo($el);
                   this.collection.forEach(function(layer) {
                       var view = new LayerItemView({model: layer});
                       div.append(view.render().el);
                   }, this);

                   return this;
               }
           });
       });
