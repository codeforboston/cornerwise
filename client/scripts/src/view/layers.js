define(["backbone", "underscore", "jquery", "layers", "utils"],
       function(B, _, $, layers, $u) {
           var LayerItemView = B.View.extend({
               template: $u.templateWithId("layer-item-template",
                                           {variable: "layer"}),

               events: {
                   "change input": "onChange"
               },

               initialize: function() {
                   this.listenTo(this.model, "change", this.render);
               },

               render: function() {
                   this.$el.html(this.template(this.model.toJSON()));
               },

               onChange: function(e) {
                   if (e.target.type == "color") {
                       this.model.set("color", e.target.value);
                   } else {
                       this.model.set("shown", e.target.checked);
                   }
               }
           });

           return B.View.extend({
               collection: layers,

               events: {
                   "click": "toggle"
               },

               initialize: function() {
                   //this.listenTo(this.collection, "change",
               },

               render: function() {
                   this.$el.html("");
                   var ul = $('<ul class="layer-list"></ul>').appendTo(this.el);
                   this.collection.forEach(function(layer) {
                       var li = $('<li class="layer"></li>').appendTo(ul),
                           view = new LayerItemView({el: li[0],
                                                     model: layer});
                       view.render();
                   }, this);

                   return this;
               }
           });
       });
