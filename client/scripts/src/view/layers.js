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
                   "click": "onClick",
                   "mouseover": "onMouseover",
                   "mouseout": "onMouseout"
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
               },

               onMouseover: function(e) {
                   var info = this.model.get("info");

                   if (info) {
                       var offset = this.$el.offset(),
                           bottom = $(window).height() - offset.top;
                       this.$popup =
                               $("<div/>")
                               .addClass("layer-info-popup")
                               .text(info)
                           .css({bottom: bottom,
                                 left: offset.left})
                           .appendTo(document.body);
                   }
               },

               onMouseout: function(e) {
                   if (this.$popup) {
                       this.$popup.remove();
                       delete this.$popup;
                   }
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

                   appState.onStateKeyChange(
                       this.hashParam,
                       function(newLy, oldLy) {
                           if (newLy === "1")
                               this._show();
                           else
                               this._hide();
                       }, this);
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
