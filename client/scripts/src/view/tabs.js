define(["backbone", "underscore", "jquery", "app-state"],
       function(B, _, $, appState) {
           return B.View.extend({
               initialize: function(options) {
                   // Object mapping titles -> views
                   var tabId = this.$el.attr("id");
                   this.tabId = tabId;
                   this.subviews = options.subviews || {};
                   this.selected =
                       tabId && appState.getKey(["tab", tabId]) ||
                       _.keys(this.subviews)[0];
                   this.panes = this.findPanes();
                   this.renderTabs();
                   this.render();

                   if (tabId) {
                       var self = this;
                       appState.onStateChange(["tab", tabId],
                                            function(newTab) {
                                                if (newTab &&
                                                    newTab !== self.selected) {
                                                    self.selectTab(newTab);
                                                }
                                            });
                   }
               },

               renderTabs: function() {
                   var tabBar = this.$(".tabs").html(""),
                       selected = this.selected;

                   _.each(this.subviews, function(view, k) {
                       var title = view.title || k,
                           tab =
                               $("<a/>")
                               .text(title)
                               .attr("href", "#")
                               .data("key", k)
                               .addClass("tab")
                               .toggleClass("selected", k === selected)
                               .appendTo(tabBar);
                   });

                   tabBar.on("click", _.bind(this.clickedTab, this));
               },

               selectTab: function(keyOrTab) {
                   var key, tab;

                   if (_.isString(keyOrTab)) {
                       if (keyOrTab == this.selected) return;
                       key = keyOrTab;
                       tab = this.$el.filter(function(elt) {
                           return $(elt).data("key") == key;
                       });
                   } else {
                       tab = keyOrTab;
                       key = tab.data("key");
                   }

                   if (key === this.selected || !tab)
                       return;

                   this.selected = key;
                   if (this.tabId)
                       appState.setHashKey(["tab", this.tabId], key);
                   this.$(".tab.selected").removeClass("selected");
                   tab.addClass("selected");
                   this.render();

                   this.trigger("viewSelected", key);
               },

               clickedTab: function(e) {
                   var tab = $(e.target).closest(".tab");

                   this.selectTab(tab);

                   return false;
               },

               findPanes: function() {
                   var panes = {}, self = this;
                   this.$(".pane").each(function(i, pane) {
                       pane = $(pane);
                       var key = pane.data("key");

                       if (key) {
                           panes[key] = pane;

                           var view = self.subviews[key];
                           if (view)
                               view.setElement(pane);
                       }
                   });

                   return panes;
               },

               pane: function(key) {
                   var pane = this.panes[key];

                   if (!pane) {
                       pane = $("<div/>")
                           .addClass("pane")
                           .data("key", key)
                           .appendTo(this.$(".tab-pane"));

                       var view = this.subviews[key];
                       view.setElement(pane);
                       view.trigger("paneCreated", pane);
                       this.panes[key] = pane;
                   }

                   return pane;
               },

               render: function() {
                   var view = this.subviews[this.selected],
                       pane = this.pane(this.selected),
                       showing = this.$(".pane.showing"),
                       showingView = showing && this.subviews[showing.data("key")];

                   if (showing)
                       showing.removeClass("showing");
                   if (showingView)
                       showingView.trigger("hidden");

                   pane.addClass("showing");
                   view.render();
               }
           });
       });
