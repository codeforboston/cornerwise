define(["backbone", "underscore", "utils", "app-state"],
       function(B, _, $u, appState) {
           /**
            * - defaultView
            *
            * - threshold: When the info pane is dragged open, it will be
                considered expanded when its height is greater than this value.
            */
           return B.View.extend({
               defaultTemplate: $u.templateWithId("info-template"),

               initialize: function(options) {
                   this.subview = options.subview;
                   this.defaultView = options.defaultView;
                   this.expanded = !!options.startExpanded;
                   this.currentView = null;
                   this.threshold = options.threshold || 250;
                   this.shouldShow = false;

                   var coll = this.collection;
                   this.listenTo(coll, "selection", this.onSelection)
                       .listenTo(coll, "selectionLoaded", this.onSelectionLoaded)
                       .listenTo(coll, "selectionRemoved", this.onSelectionRemoved)
                       .listenTo(coll, "change", this.modelChanged);
               },

               events: {
                   "mousedown .dragarea": "onMousedown",
                   "click .close": "onClick",
                   "click .prev-button": "onPrev",
                   "click .next-button": "onNext"
               },

               render: function() {
                   var coll = this.collection,
                       view = this.subview || this.defaultView,
                       models = coll ? coll.getSelection() : [],
                       $el = this.$el;

                   $el.removeClass("loading empty");

                   if (this.currentView)
                       this.currentView.setElement(null);

                   if (!models.length) {
                       $el.addClass("default");
                       if (this.defaultView) {
                           this.currentView = this.defaultView;
                           this.defaultView.setElement(this.$(".content"));
                           this.defaultView.render();
                       } else if (this.defaultTemplate) {
                           this.$(".content").html(this.defaultTemplate());
                       } else {
                           $el.addClass("empty");
                       }
                   } else {
                       $el.removeClass("default")
                          .addClass("loading");
                       this.currentView = view;
                       view.setElement(this.$(".content"));
                       if (view.showMulti && models.length > 1) {
                           view.showMulti(models, this.expanded);
                       } else {
                           view.show(models[0], this.expanded)
                               .done(function() {
                                   $el.removeClass("loading");
                               });
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

               onSelection: function(coll, ids) {
                   this.active = name;
                   this.$el.addClass("loading").find(".content").html("");
               },

               onSelectionLoaded: function(coll, ids) {
                   this.active = name;
                   this.render();

                   _.each(ids, function(id) {
                       this.listenTo(coll.get(id), "change", this.modelChanged);
                   }, this);
               },

               onSelectionRemoved: function(coll, remIds, ids) {
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
                   this.collection.setSelection([]);
               },

               onClick: function(e) {
                   this.clearSelection();
                   return false;
               },

               onNext: function() { return this.onNav(1); },

               onPrev: function() {return this.onPrev(-1); },

               onNav: function(dir) {
                   var coll = this.collection,
                       model;

                   if (coll) {
                       if (dir < 0) {
                           model = coll.selectPrev();
                       } else if (dir > 0) {
                           model = coll.selectNext();
                       }

                       if (!model) return true;

                       appState.focusModels([model]);

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
