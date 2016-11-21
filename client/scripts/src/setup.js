define(
    ["jquery", "collection/proposals", "collection/manager", "view/map",
     "view/proposalInfo", "view/proposal", "glossary", "config", "appState",
     "viewManager", "refLocation", "view/layers", "view/alerts",
     "view/filters", "view/image", "view/subscribe", "legalNotice",
     "view/modal", "view/list", "view/info"],
    function($, Proposals, CollectionManager, MapView, ProposalInfoView,
             ProposalItemView, glossary, config, appState, ViewManager,
             refLocation, LayersView, alerts, FiltersView, ImageView,
             SubscribeView) {
        return {
            start: function() {
                var proposals = new Proposals(),
                    appViews = {
                        proposals: proposals,
                        glossary: glossary
                    };

                proposals
                    .on("fetching",
                        function() {
                            $(document.body)
                                .removeClass("loading-failed")
                                .addClass("loading-proposals");
                        })
                    .on("fetchingComplete",
                        function() {
                            $(document.body)
                                .removeClass("loading-proposals");
                        })
                    .on("fetchingFailed",
                        function() {
                            $(document.body).addClass("loading-failed");
                        });


                appState.onStateKeyChange("view", function(view, oldView) {
                    $(document.body)
                        .removeClass(oldView)
                        .addClass(view);

                    var showIntro = !view || view === "intro";

                    $(document.body).toggleClass("nointro", !showIntro);
                });

                refLocation.on("change:setMethod", function(_, method) {
                    var view = appState.getKey("view");
                    if (method !== "auto" && (!view || view === "intro")) {
                        appState.setHashKey("view", "main");
                    }
                });

                if (window.ResponseMessages && ResponseMessages.length) {
                    alerts.showResponses(ResponseMessages);
                }

                // Configure modal views here!
                // See viewManager.js for documentation and examples.
                new ViewManager({
                    // Simple view that will load the about page from a
                    // static URL into a modal overlay when the 'view'
                    // parameter in the hash.
                    "about": ["view/modal", {url: "/static/template/about.html",
                                             context: {config: config}}],
                    "events": ["view/modal",
                               {url: "/static/template/eventBrowser.html"}],
                    "list": ["view/list",
                             {collection: proposals,
                              subview: ProposalItemView}],
                    "info": ["view/info", {collection: proposals,
                                           subview: new ProposalInfoView()}]
                });

                appViews.layers = new LayersView({
                    el: "#map-options"
                }).render();


                appViews.mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                appViews.filtersView = new FiltersView({
                    collection: proposals,
                    mapView: appViews.mapView
                });

                appViews.subscribeView = new SubscribeView({
                    collection: proposals,
                    el: "#subscribe"
                });

                appViews.imageView = new ImageView({
                    el: "#image-view"
                });

                appState.init();
                glossary.init();

                ga = console ?
                    function() { console.log(arguments); } :
                _.noop;
                // Load Google Analytics, if it's configured.
                if (config.gAnalyticsID) {
                    (function(i,s,o,g,r,a,m){i["GoogleAnalyticsObject"]=r;i[r]=i[r]||function(){
                        (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
                                             m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
                                            })(window,document,"script","https://www.google-analytics.com/analytics.js",'ga');

                    ga("create", config.gAnalyticsID, "auto");
                    ga("send", "pageview");
                }

                return appViews;
            }
        };
    });
