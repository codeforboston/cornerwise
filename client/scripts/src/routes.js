define(["backbone"], function(B) {
    var AppRouter = B.Router.extend({
        routes: {
            "": ""
        },

        showModal: function(pageName) {

        }
    });

    var appRouter;

    return {
        getRouter: function() {
            return appRouter;
        },

        init: function() {
            appRouter = new AppRouter();
            B.history.start();

            return this;
        }
    };

});
