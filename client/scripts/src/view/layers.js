define(["backbone", "underscore", "jquery", "collection/layers", "utils",
        "appState"],
       function(B, _, $, layers, $u, appState) {
           var LayerItemView = B.View.extend({
               template: $u.templateWithUrl("/static/template/layerItem.html",
                                            {variable: "layer"}),

               tagName: "a",

               attributes: function() {
                   return {href: "#"};
               },

               className: function() {
                   var attrs = this.model.attributes;
                   return ("layer-button" +
                           (attrs.shown ? " selected" : "") +
                           (attrs._loading ? " loading" : ""));
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
                   var self = this;
                   this.template(this.model,
                                 function(html) {
                                     self.$el.addClass(this.className)
                                         .html(html);
                                 });

                   return this;
               },

               onClick: function(e) {
                   this.model.collection.toggleLayer(this.model.id);
                   e.preventDefault();
               },

               onMouseover: function(e) {
                   var info = this.model.get("info");

                   if (info) {
                       var offset = this.$el.offset(),
                           bottom = $(window).height() - offset.top;

                       if (!this.$popup)
                           this.$popup = $("<div class='layer-info-popup'/>");

                       this.$popup.text(info)
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

               render: function() {
                   var $el = this.$el.html("");
                   this.collection.forEach(function(layer) {
                       var view = new LayerItemView({model: layer});
                       $el.append(view.render().el);
                   }, this);

                   return this;
               }
           });
       });
