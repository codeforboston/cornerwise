define(["backbone", "underscore", "config", "utils"],
       function(B, _, config, $u) {
           var appState =
                   {
                       /** @private */
                       _cachedState: null,

                       getDefaults: function() {
                           return {
                               // Filters:
                               "f": {
                                   "projects": "",
                                   "range": "<60",
                                   // Region:
                                   "region": "somerville"
                               },
                               "ref": {
                                   "lat": config.refPointDefault.lat,
                                   "lng": config.refPointDefault.lng,
                                   "setMethod": "auto"
                               },
                               sort: "-updated"
                           };
                       },

                       getters: {},

                       /**
                        * Replaces the current state of the application with a
                        * new one specified by o.
                        *
                        * @param {Object} o The new state to use
                        * @param {boolean} replace If true, do not create a new
                        * entry in the history.  If the user navigates back, it
                        * will skip over the current state.
                        */
                       setHashState: function(o, replace, quiet) {
                           var query = $u.encodeQuery(o);

                           // No change:
                           if (query === B.history.getHash())
                               return o;

                           if (replace && window.location.replace) {
                               var url = window.location.toString().split("#")[0];
                               window.location.replace(url + "#" + query);
                           } else {
                               window.location.hash = query;
                           }

                           return o;
                       },

                       /**
                        * @returns {Object} An object representing the current
                        * location hash.
                        */
                       getHashState: function() {
                           return $u.decodeQuery(B.history.getHash());
                       },

                       getState: function(o) {
                           if (this._cachedState)
                               return this._cachedState;

                           return $u.deepMerge(
                               this.getDefaults(),
                               o || this.getHashState());
                       },

                       getKey: function(k) {
                           var state = this.getState(),
                               ks = _.isArray(k) ? k : k.split(".");

                           return $u.getIn(state, ks);
                       },

                       /**
                        * @callback stateCallback
                        * @param {Object} state
                        *
                        * @param {stateCallback} f
                        * @param {bool} replace
                        *
                        * @returns {Object}
                        */
                       changeHash: function(f, replace, quiet) {
                           return this.setHashState(f(this.getHashState()), replace, quiet);
                       },

                       changeHashKey: function(key, f, replace, quiet) {
                           return this.setHashKey(key, f(this.getKey(key)), replace, quiet);
                       },

                       /**
                        * @param {Object} o
                        */
                       extendHash: function(o, replace, quiet) {
                           return this.setHashState(_.extend(this.getHashState(), o), replace, quiet);
                       },

                       setHashKey: function(k, v, replace, quiet) {
                           var hashObject = this.getHashState(),
                               ks = _.isArray(k) ? k : k.split(".");

                           $u.setIn(hashObject, ks, v);
                           return this.setHashState(hashObject, replace, quiet);
                       },

                       clearHashKey: function(k, replace, quiet) {
                           var hashObject = $u.decodeQuery(B.history.getHash()),
                               ks = _.isArray(k) ? k : k.split(".");

                           $u.setIn(hashObject, ks, undefined);
                           return this.setHashState(hashObject, replace, quiet);
                       },

                       goBack: function(defaultView) {
                           if (this.lastView || defaultView)
                               this.setHashKey("view", this.lastView || defaultView);
                           return !!this.lastView;
                       },

                       triggerHashState: function(o) {
                           this.trigger("hashState", this.getState(o));
                       },

                       watchers: [],

                       lastView: null,

                       startWatch: function() {
                           var lastState = null,
                               watchers = this.watchers,
                               defaults = this.getDefaults(),
                               self = this;

                           this.on("hashState", function(state) {
                               if (lastState && state.view !== lastState.view) {
                                   self.lastView = lastState.view;
                               }

                               _.each(watchers, function(watcher) {
                                   var callback = watcher[0],
                                       key = watcher[1],
                                       context = watcher[2] || this;

                                   if (key) {
                                       var defval = $u.getIn(defaults, key),
                                           oldVal = ($u.getIn(lastState, key) ||
                                                     (lastState && defval)),
                                           newVal = $u.getIn(state, key) || defval;
                                       if (lastState && _.isEqual(newVal, oldVal))
                                           return;
                                       callback.call(context, newVal, oldVal);
                                   } else {
                                       callback.call(context, state, lastState ||
                                                     {});
                                   }
                               });
                               lastState = state;
                           });
                       },

                       /**
                        * @param {stateChangeCallback} fn - this callback should
                        * not alter the state
                        * @param {} [context] - the value of `this` when
                        * executing the callback
                        *
                        * @callback stateChangeCallback
                        * @param {Object} newState
                        * @param {Object} oldState
                        */
                       onStateChange: function(fn, context) {
                           this.watchers.push([fn, undefined, context]);

                           if (this._initialized)
                               fn.call(context, this.getState(), null);
                       },

                       /**
                        * @param {string} key
                        * @param {keyChangeCallback} fn
                        * @param {} [context]
                        *
                        * @callback keyChangeCallback
                        * @param {} newValue
                        * @param {} [oldValue]
                        */
                       onStateKeyChange: function(key, fn, context) {
                           var ks = _.isArray(key) ? key : key.split(".");

                           this.watchers.push([fn, ks, context]);

                           if (this._initialized) {
                               fn.call(context, this.getKey(ks), null);
                           }
                       },

                       /**
                        * Run at initialization.  Any link with an href of the
                        * form #param=value&... (etc.), when clicked, will cause
                        * the parameters and values to be merged with the
                        * current hash state, and the application will update
                        * accordingly.
                        */
                       _setupLinks: function() {
                           $(document).on("click", "a,._setview", function(e) {
                               // if (e.currentTarget != e.target)
                               //     return true;

                               if ($(this).hasClass("_back") && appState.goBack()) {
                                   e.preventDefault();
                                   return false;
                               }

                               var goto = $(this).data("goto");

                               if (goto) {
                                   if (e.target !== e.currentTarget)
                                       return true;

                                   appState.setHashKey("view", goto);

                                   e.preventDefault();
                                   return false;
                               } else {
                                   var href = $(this).attr("href"),
                                       hash = href && href[0] == "#" && href.slice(1);

                                   if (hash) {
                                       var replace = !!$(this).data("replace-history");
                                       appState.extendHash($u.decodeQuery(hash), replace);

                                       e.preventDefault();
                                       return false;
                                   }

                               }

                               return true;
                           });
                       },

                       // Events that are not properly considered part of the
                       // application state:

                       /**
                        * @param {Object[]} models
                        * @param {boolean} shouldZoom
                        */
                       focusModels: function(models, shouldZoom) {
                           this.trigger("shouldFocus", models, shouldZoom);
                       },

                       init: function() {
                           this.startWatch();
                           this.triggerHashState();
                           this._initialized = true;
                           this._setupLinks();

                           var self = this;
                           B.history.start({hashChange: true});
                           B.history.handlers.push({
                               route: {test: _.constant(true)},
                               callback: function(fragment) {
                                   var o = $u.decodeQuery(fragment);
                                   self._cachedState = null;
                                   self.triggerHashState(o);
                               }
                           });
                       }
                   };

           _.extend(appState, B.Events);

           return appState;

       });
