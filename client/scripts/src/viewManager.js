/**
 * Set up simple primary views to appear and disappear based on the
 * current value of the application's 'view' key.
 *
 * Usage:
 *  manager.add({ about: ["modal-view", {url: "/path/to/about.html"}] })
 */
define(["routes", "underscore", "jquery"],
       function(routes, _, $) {
           return {
               add: function(views) {
                   _.extend(this.views, views);
                   this.init();
               },

               init: function() {
                   if (this._initialized) return;
                   this._initialized = true;

                   var self = this,
                       key = routes.getKey("view");
                   routes.onStateChange(
                       "view",
                       function(newKey, oldKey) {
                           key = newKey;
                           if (oldKey) {
                               var old = self.constructedViews[oldKey];
                               if (old) {
                                   if (!old.onDismiss || old.onDismiss !== false) {
                                       if (old.hide)
                                           old.hide();
                                       old.trigger("wasHidden");
                                   }
                               }
                           }

                           self.getOrConstructView(newKey)
                               .then(function(newView) {
                                   // If it took too long to load
                                   // the module, the key may have
                                   // changed:
                                   if (newView && key == newKey) {
                                       if (!newView.onPresent || newView.onPresent() !== false) {
                                           if (newView.show)
                                               newView.show();
                                           newView.trigger("wasShown");
                                       }
                                   }
                               });
                       });
               },

               getOrConstructView: function(name) {
                   var promise = $.Deferred();

                   if (!this.constructedViews[name]) {
                       var view = this.views[name];

                       if (!view)
                           promise.reject({reason: "No view for key:" + name});

                       var modName = _.isString(view) ? view :
                               (_.isArray(view) && _.isString(view[0])) ? view[0] : null;

                       if (_.isFunction(view)) {
                           this.constructedViews[name] = new view();
                       } else if (modName) {
                           var self = this;
                           require(["optional!" + modName], function(mod) {
                               if (_.isString(view)) {
                                   self.views[name] = mod;
                                   promise.resolve(new mod());
                               } else {
                                   self.views[name] = [mod, view[1]];
                                   promise.resolve(new mod(view[1]));
                               }
                           });
                           return promise;
                       } else if (_.isArray(view)) {
                           this.constructedViews[name] = new view[0](view[1]);
                       } else if (_.isObject(view)) {
                           this.constructedViews[name] = view;
                       } else {
                           return promise.reject({reason: "Invalid view configuration"});
                       }
                   }

                   return promise.resolve(this.constructedViews[name]);
               },

               views: {},
               constructedViews: {}
           };
       });
