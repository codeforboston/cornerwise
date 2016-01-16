/**
 * Set up simple primary views to appear and disappear based on the
 * current value of the application's 'view' key.
 *
 * Example Usage:
 *  new ViewManager({ about: ["modal-view", {url: "/path/to/about.html"}] })
 *
 * When the 'view' key in the location hash changes to 'about', the
 * 'modal-view' module will be loaded.  The ModalView constructor will
 * then be called with the specified argument.
 *
 * The views used must implement show and hide methods.
 *
 * @param {Object} view A map of values to view specifications.  A value
 * refers to the value in the URL hash.  A simple view specification can
 * be an instantiated view; a constructor function for a view, which
 * will be called when the view is first needed; or a string, which
 * should be the name of a module that returns a view constructor.  If a
 * view is specified as an array, the first member can be a module name
 * string or a constructor function, and the second member will be
 * passed as an argument to the constructor.
 * @param {String?} name If specified, this is the name of the hash key
 * to observe.
 *
 */
define(["routes", "underscore", "jquery"],
       function(routes, _, $) {
           function ViewManager(views, name) {
               name = name || "view";
               this.views = views || {};
               this.constructedViews = {};

               var self = this,
                   key = routes.getKey(name);
               routes.onStateChange(
                   "view",
                   function(newKey, oldKey) {
                       key = newKey;
                       if (oldKey) {
                           var old = self.constructedViews[oldKey];
                           if (old && old.hide)
                               old.hide();
                       }

                       self.getOrConstructView(newKey)
                           .then(function(newView) {
                               // If it took too long to load
                               // the module, the key may have
                               // changed:
                               if (newView && key == newKey &&
                                   newView.show) {
                                   newView.show();
                               }
                           });
                   });
           }

           _.extend(ViewManager.prototype, {
               add: function(views) {
                   _.extend(this.views, views);
                   this.init();
               },

               getConstructedView: function(name) {
                   return this.constructedViews[name];
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
                           var self = this,
                               arg = _.isString(view) ? undefined : view[1];
                           require([modName], function(mod) {
                               if (!mod)
                                   throw new Error("Could not load module: " + modName);

                               var viewInstance = new mod(arg);
                               self.constructedViews[name] = viewInstance;
                               delete self.views[name];
                               promise.resolve(viewInstance);
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
               }
           });

           return ViewManager;
       });
