define(["backbone", "underscore", "config", "utils"],
       function(B, _, config, $u) {
           var appState =
                   {
                       /** @private */
                       _cachedState: null,

                       defaults: {
                           // Region:
                           "r": "somerville",
                           // Filters:
                           "f": {
                               "projects": ""
                           },
                           "ref": {
                               "lat": config.refPointDefault.lat,
                               "lng": config.refPointDefault.lng
                           }
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

                       getState: function() {
                           if (this._cachedState)
                               return this._cachedState;

                           return $u.deepMerge(
                               $u.decodeQuery(B.history.getHash()),
                               this.defaults);
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

                       triggerHashState: function(o) {
                           o = o || $u.decodeQuery(B.history.getHash());
                           this.trigger("hashState", o);
                       },

                       watchers: [],

                       startWatch: function() {
                           var lastState = null,
                               watchers = this.watchers,
                               defaults = this.defaults;
                           this.on("hashState", function(state) {
                               _.each(watchers, function(watcher) {
                                   var callback = watcher[0],
                                       key = watcher[1];

                                   if (key) {
                                       var defval = $u.getIn(defaults, key),
                                    oldVal = $u.getIn(lastState, key) || (lastState && defval),
                                           newVal = $u.getIn(state, key) || defval;
                                       if (lastState && _.isEqual(newVal, oldVal))
                                           return;
                                       callback(newVal, oldVal);
                                   } else {
                                       callback(state, lastState || {});
                                   }
                               });
                               lastState = state;
                           });
                       },

                       /**
                        * @param {String|Function} arg1 If arg2 is present, the key to
                        * watch for changes. Otherwise, callback function.
                        * @param {Function} [arg2] Used as the callback if a key is
                        * provided.
                        *
                        * @callback
                        * @param {Object} newState If a key is provided, the
                        * key's value
                        * @param {Object} oldState
                        */
                       onStateChange: function(arg1, arg2) {
                           var watcher = arg2 ? [arg2, _.isArray(arg1) ? arg1 : arg1.split(".")] : [arg1];
                           this.watchers.push(watcher);
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
                               if (e.currentTarget != e.target)
                                   return true;

                               var goto = $(this).data("goto");

                               if (goto) {
                                   appState.setHashKey("view", goto);

                                   return false;
                               } else {
                                   var href = $(this).attr("href"),
                                       hash = href && href[0] == "#" && href.slice(1);

                                   if (hash) {
                                       appState.extendHash($u.decodeQuery(hash));

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
                           this._setupLinks();

                           var self = this;
                           B.history.start({hashChange: true});
                           B.history.handlers.push({
                               route: {test: _.constant(true)},
                               callback: function(fragment) {
                                   var o = $u.decodeQuery(fragment);
                                   self._cachedState = o;
                                   self.triggerHashState(o);
                               }
                           });
                       }
                   };

           _.extend(appState, B.Events);

           return appState;

       });
