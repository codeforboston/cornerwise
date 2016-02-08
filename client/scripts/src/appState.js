define(["backbone", "underscore", "utils"],
       function(B, _, $u) {
           var dispatcher = _.clone(B.Events),
               appState =
                   {
                       /** @private */
                       _cachedState: null,

                       /**
                        * Returns an event dispatcher that is shared by the entire
                        * application.
                        */
                       getDispatcher: function() {
                           return dispatcher;
                       },

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

                       getState: function() {
                           return $u.decodeQuery(B.history.getHash());
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
                           return this.setHashState(f(this.getState()), replace, quiet);
                       },

                       changeHashKey: function(key, f, replace, quiet) {
                           return this.setHashKey(key, f(this.getKey(key)), replace, quiet);
                       },

                       /**
                        * @param {Object} o
                        */
                       extendHash: function(o, replace, quiet) {
                           return this.setHashState(_.extend(this.getState(), o), replace, quiet);
                       },

                       setHashKey: function(k, v, replace, quiet) {
                           var hashObject = this.getState(),
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
                           dispatcher.trigger("hashState", o);
                       },

                       watchers: [],

                       startWatch: function() {
                           var lastState = null,
                               watchers = this.watchers;
                           this.getDispatcher().on("hashState", function(state) {
                               _.each(watchers, function(watcher) {
                                   var callback = watcher[0],
                                       key = watcher[1];

                                   if (key) {
                                       var oldVal = $u.getIn(lastState, key),
                                           newVal = $u.getIn(state, key);
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

                       setupLinks: function() {
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

                       init: function() {
                           this.startWatch();
                           this.triggerHashState();
                           this.setupLinks();

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

           return appState;

       });
