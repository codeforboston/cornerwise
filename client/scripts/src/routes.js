define(["backbone", "underscore", "utils"], function(B, _, $u) {
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
                this.dispatchEvents(o);

            return o;
        },

        changeHash: function(f, quiet) {
            var hashObject = $u.decodeQuery(B.history.getHash());

            return this.setHashState(f(hashObject), quiet);
        },

        setHashKey: function(k, v, quiet) {
            var hashObject = $u.decodeQuery(B.history.getHash());

            hashObject[k] = v;
            return this.setHashState(hashObject, quiet);
        },

        clearHashKey: function(k, quiet) {
            var hashObject = $u.decodeQuery(B.history.getHash());

            delete hashObject[k];
            return this.setHashState(hashObject, quiet);
        },

        triggerHashState: function(o) {
            o = o || $u.decodeQuery(B.history.getHash());
            dispatcher.trigger("hashState", o);
        },

        watchers: [],

        startWatch: function() {
            var lastState = {},
                watchers = this.watchers;
            this.getDispatcher().on("hashState", function(state) {
                _.each(watchers, function(watcher) {
                    var callback = watcher[0],
                        key = watcher[1];

                    if (key) {
                        if (lastState && lastState[key] === state[key])
                            return;
                        callback(state[key], lastState[key]);
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
         */
        onStateChange: function(arg1, arg2) {
            var watcher = arg2 ? [arg2, arg1] : [arg1];
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
                    self.triggerHashState(o);
                }
            });

            return appRouter;
        }
    };

});
