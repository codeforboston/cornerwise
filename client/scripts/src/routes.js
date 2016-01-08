define(["backbone", "underscore", "utils"],
       function(B, _, $u) {
           var dispatcher = _.clone(B.Events);

           var appRouter;

           return {
               getRouter: function() {
                   return appRouter || this.init();
               },

               /**
                * Returns an event dispatcher that is shared by the entire
                * application.
                */
               getDispatcher: function() {
                   return dispatcher;
               },

               setHashState: function(o, quiet) {
                   var query = $u.encodeQuery(o);

                   // No change:
                   if (query === B.history.getHash())
                       return o;

                   window.location.hash = query;

                   if (!quiet)
                       this.triggerHashState(o);

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

               changeHash: function(f, quiet) {
                   return this.setHashState(f(this.getState()), quiet);
               },

               /**
                * @param {Object} o
                */
               extendHash: function(o, quiet) {
                   return this.setHashState(_.extend(this.getState(), o), quiet);
               },

               setHashKey: function(k, v, quiet) {
                   var hashObject = this.getState(),
                       ks = _.isArray(k) ? k : k.split(".");

                   $u.setIn(hashObject, ks, v);
                   return this.setHashState(hashObject, quiet);
               },

               clearHashKey: function(k, quiet) {
                   var hashObject = $u.decodeQuery(B.history.getHash()),
                       ks = _.isArray(k) ? k : k.split(".");

                   $u.setIn(hashObject, ks, undefined);
                   return this.setHashState(hashObject, quiet);
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
                               callback(state, lastState);
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

               init: function() {
                   this.startWatch();
                   this.triggerHashState();

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

                   return appRouter;
               }
           };

       });
