define(["backbone", "underscore", "utils"],
       function(B, _, $u) {
           /**
            * A view that manages other views.
            *
            * Important options:
            *
            * - views: A map of string names to Views. The View objects should
            *    implement a show() method that accepts a model object and a
            *    boolean indicating if the info bar is expanded. An optional
            *    showMulti() method will be called when multiple models are
            *    selected.
            *
            * - collections: A map of string names to SelectableCollection
            *    objects.
            *
            * Additional options:
            *
            * - defaultView
            *
            * - threshold: When the info pane is dragged open, it will be
                considered expanded when its height is greater than this value.
            */
           return B.View.extend({
               defaultTemplate: $u.templateWithId("info-template"),

               initialize: function(options) {
                   this.views = options.views;
                   this.collectionManager = options.collectionManager;
                   this.collections = options.collections;
                   this.defaultView = options.defaultView;
                   this.expanded = !!options.startExpanded;
                   this.threshold = options.threshold || 250;
                   this.shouldShow = false;

                   // TODO: Need a better way to manage access to the shared element:
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
                       this.listenTo(coll, "change", this.modelChanged);

                   }, this);

                   if (this.defaultView)
                       this.defaultView.setElement(this.$(".content"));
                   
                   this.$el
                       .on("mousedown touchstart", ".dragarea",
                           _.bind(this.onMousedown, this))
                       .on("click", ".close", _.bind(this.onClick, this))
                       .on("click", ".prev-button", _.bind(this.onNav, this, -1))
                       .on("click", ".next-button", _.bind(this.onNav, this, 1));
               },

               render: function() {
                   var name = this.active,
                       coll = this.collections[name],
                       view = this.views[name] || this.defaultView,
                       models = coll ? coll.getSelection() : [];

                   this.$el.removeClass("loading empty");

                   if (!name || !models.length) {
                       this.$el.addClass("default");
                       if (this.defaultView) {
                           this.defaultView.render();
                       } else if (this.defaultTemplate) {
                           this.$(".content").html(this.defaultTemplate());
                       } else {
                           this.$el.addClass("empty");
                       }
                   } else {
                       this.$el.removeClass("default");
                       if (view.showMulti && models.length > 1) {
                           view.showMulti(models, this.expanded);
                       } else {
                           view.show(models[0], this.expanded);
                       }
                   }
               },

               setExpanded: function(expanded) {
                   if (this.expanded === expanded)
                       return;

                   this.expanded = expanded;
                   this.render();
                   this.$el.toggleClass("expanded", expanded);

                   this.$(".dragger").text(expanded ? "LESS" : "MORE");
               },

               onMousedown: function(e) {
                   if (e.touches && e.touches.list !== 1)
                       return true;

                   var $el = this.$el,
                       position = $el.offset(),
                       height = $el.height(),
                       touch = e.touches && e.touches[0],
                       touchId = touch && touch.identifier,
                       starty = touch ? touch.pageY : e.pageY,
                       startTime = new Date().valueOf(),
                       wasExpanded = this.expanded;

                   $el.addClass("_disable_height_transition");

                   var onMouseMove = _.bind(function(e) {
                       var y;
                       if (touchId && e.changedTouches) {
                           if (e.changedTouches.length !== 1 ||
                               e.changedTouches[0].identifier !== touchId)
                               return true;
                           y = e.changedTouches[0].pageY;
                       } else {
                           y = e.pageY;
                       }

                       var newHeight = height + (starty - y);
                       $el.height(newHeight);

                       this.setExpanded(newHeight >= this.threshold);

                       return false;
                   }, this);

                   $(document)
                       .one("mouseup touchend", _.bind(function() {
                           $(document).off("mousemove touchmove", onMouseMove);

                           if (new Date().valueOf() - startTime < 300) {
                               this.setExpanded(!wasExpanded);
                           }

                           $el.removeClass("_disable_height_transition")
                               .css("height", "auto");

                           return false;
                       }, this))
                       .on("mousemove touchmove", onMouseMove);

                   return false;
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

               clearSelection: function() {
                   var coll = this.collections[this.active];

                   if (coll) {
                       coll.setSelection([]);
                   }
               },

               onClick: function(e) {
                   this.clearSelection();
                   return false;
               },

               onNav: function(dir) {
                   var coll = this.collections[this.active];

                   if (coll) {
                       if (dir < 0) {
                           coll.selectPrev();
                       } else if (dir > 0) {
                           coll.selectNext();
                       }

                       return false;
                   }

                   return true;
               },

               modelChanged: function(model) {
                   if (_.every(_.keys(model.changed),
                               function(k) { return k[0] == "_"; }))
                       return;

                   this.render();
               },

               toggle: function(shouldShow) {
                   this.shouldShow = shouldShow;
                   this.$el.toggleClass("collapsed", !shouldShow);

                   if (shouldShow)
                       this.render();
               }
           });
       });
