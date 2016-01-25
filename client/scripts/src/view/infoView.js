define(["backbone", "underscore", "utils"],
       function(B, _, $u) {
           /**
            * A view that manages other views.
            *
            * Important options:
            *
            * - views: A map of string names to Views.  The View objects
            *    should implement a show() method that accepts a model
            *    object and a boolean indicating if the info bar is
            *    expanded.  An optional showMulti() method will be
            *    called when multiple models are selected.
            */
           return B.View.extend({
               defaultTemplate: $u.templateWithId("info-template"),

               initialize: function(options) {
                   this.views = options.views;
                   this.collections = options.collections;
                   this.defaultView = options.defaultView;
                   this.expanded = !!options.startExpanded;

                   _.each(options.views, function(view) {
                       view.setElement(this.$(".content"));
                   }, this);

                   _.each(options.collections, function(coll, name) {
                       this.listenTo(coll, "selection",
                                     _.bind(this.onSelection, this, name));
                       this.listenTo(coll, "selectionLoaded",
                                     _.bind(this.onSelectionLoaded, this, name));
                       this.listenTo(coll, "selectionRemoved",
                                     _.bind(this.onSelectionRemoved, this, name));
                   }, this);

                   if (this.defaultView)
                       this.defaultView.setElement(this.$(".content"));
                   this.listenTo(
               },

               render: function() {
                   var name = this.active,
                       coll = this.collections[name],
                       view = this.views[name] || this.defaultView,
                       models = coll ? coll.getSelection() : [];

                   this.$el.removeClass("loading");

                   if (!models.length) {
                       if (this.defaultView) {
                           this.defaultView.render();
                       } else {
                           this.$(".content").html(this.defaultTemplate());
                       }
                   } else if (view.showMulti && models.length > 1) {
                       view.showMulti(models, this.expanded);
                   } else {
                       view.show(models[0], this.expanded);
                   }
               },

               setExpanded: function(expanded) {
                   if (this.expanded !== expanded) {
                       this.expanded = expanded;
                       this.render();
                   }
               },

               onMousedown: function(e) {
                   var $el = this.$el,
                       position = $el.offset(),
                       height = $el.size().height,
                       starty = e.pageY;

                   $el.addClass("_disable_height_transition");

                   var onMouseMove = _.bind(function(e) {
                       var newHeight = height + (starty - e.pageY);
                       $el.height(newHeight);

                       this.setExpanded(newHeight/height >= 2);
                   }, this);

                   $(document)
                       .one("mouseup touchend", function() {
                           $(document).off("mousemove touchmove", onMouseMove);
                       })
                       .on("mousemove touchmove", onMouseMove);
               },

               onSelection: function(name, coll, ids) {
                   this.active = name;
                   this.$el.addClass("loading").find(".content").html("");
               },

               onSelectionLoaded: function(name, coll, ids) {
                   this.active = name;
                   this.render();

                   _.each(ids, function(id) {
                       this.listenTo(coll.get(id), "change", this.modelChanged);
                   }, this);
               },

               onSelectionRemoved: function(name, coll, remIds, ids) {
                   if (!ids.length) {
                       // No active selection:
                       this.active = null;
                   }

                   _.each(remIds, function(id) {
                       var model = coll.get(id);
                       if (model)
                           this.stopListening(model, "change", this.modelChanged);
                   }, this);

                   this.render();
               },

               modelChanged: function(model) {
                   if (_.every(_.keys(model.changed),
                               _.partial(_.contains, ["selected", "hovered"])))
                       return;

                   this.render();
               }
           });
       });
