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

            if (query === window.location.hash)
                return;

            window.location.hash = query;

            if (!quiet)
                this.dispatchEvents(o);
        },

        setHashKey: function(k, v, quiet) {
            var hashObject = $u.decodeQuery(window.location.hash);

            hashObject[k] = v;
            this.setHashState(hashObject, quiet);
        },

        triggerHashState: function(o) {
            o = o || $u.decodeQuery(B.history.getHash());
            dispatcher.trigger("hashState", o);
        },

        onStateChange: function(cb) {
            var lastState = null;
            this.getDispatcher().on("hashState", function(state) {
                cb(state, lastState);
                lastState = state;
            });
        },

        init: function() {
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
