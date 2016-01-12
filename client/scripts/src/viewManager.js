define(["routes"],
       function(routes) {
           return {
               init: function(views) {
                   _.extend(this.views, views);
                   var self = this;
                   routes.onStateChange("view",
                                        function(newKey, oldKey) {
                                            if (oldKey) {
q                                                var old = self.constructedViews[oldKey];
                                                if (old) {
                                                    if (old.onDismiss && old.onDismiss !== false) {
                                                        if (old.hide)
                                                            old.hide();
                                                        old.trigger("wasHidden");
                                                    }
                                                }

                                                var newView = self.getOrConstructView(newKey);

                                                if (newView) {
                                                    if (newView.onPresent && newView.onPresent() !== false) {
                                                        if (newView.show)
                                                            newView.show();
                                                        newView.trigger("wasShown");
                                                    }
                                                }
                                            }
                                        });
               },

               getOrConstructView: function(name) {
                   if (!this.constructedViews[name]) {
                       var view = this.views[name];

                       if (!view)
                           return null;

                       if (_.isFunction(view)) {
                           this.constructedViews[name] = new view();
                       } else if (_.isArray(view)) {
                           this.constructedViews[name] = new view[0](view[1]);
                       } else if (_.isObject(view)) {
                           this.constructedViews[name] = view;
                       } else {
                           return null;
                       }
                   }

                   return this.constructedViews[name];
               },

               loadViews: function(views) {
                   _.each(views, function(v, key) {
                       var modName = _.isString(v) ? v :
                               (_.isArray(v) && _.isString(v[0])) ? v[0] : null;
                       if (modName) {
                           require(["optional!" + v], function(mod) {
                               if (_.isString(v))
                                   views[key] = mod;
                               else
                                   views[key] = [mod, v[1]];
                           });
                       }
                   });
               },

               views: {},
               constructedViews: {}
           };
       });
