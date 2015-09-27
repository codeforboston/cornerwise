define(["backbone"], function(B) {
    var dispatcher = _.clone(B.Events);

    var AppRouter = B.Router.extend({
        routes: {
            "details/:id": "details"
        }
    });

    var appRouter;

    return {
        getRouter: function() {
            return appRouter || this.init();
        },

        getDispatcher: function() {
            return dispatcher;
        },

        init: function() {
            appRouter = new AppRouter();

            B.history.start();

            return appRouter;
        }
    };

});
