define(
    ["jquery", "collection/proposals", "collection/parcels", "view/map",
     "view/proposalInfo", "view/proposal", "glossary", "config", "appState",
     "viewManager", "refLocation", "view/layers", "view/alerts", "view/filters",
     "view/image", "view/subscribe", "view/parcelInfo", "legalNotice", "leaflet/patch",
     "view/modal", "view/list", "view/info"],
    function($, Proposals, Parcels, MapView, ProposalInfoView,
             ProposalItemView, glossary, config, appState, ViewManager,
             refLocation, LayersView, alerts, FiltersView, ImageView,
             SubscribeView, ParcelInfoView) {
        return {
            start: function() {
                var parcels = new Parcels({appState: appState}),
                    proposals = new Proposals({parcels: parcels}),
                    appViews = {
                        alerts: alerts,
                        parcels: parcels,
                        proposals: proposals,
                        glossary: glossary
                    },
                    loading = {proposals: true};

                function markLoaded(what) {
                    if (!loading[what]) return;

                    delete loading[what];
                    if ($.isEmptyObject(loading))
                        appState.trigger("initialized");
                }

                proposals
                    .on("fetching",
                        function() {
                            $(document.body)
                                .removeClass("loading-failed")
                                .addClass("loading-proposals");
                        })
                    .on("fetchingComplete",
                        function() {
                            markLoaded("proposals");
                            $(document.body)
                                .removeClass("loading-proposals");
                        })
                    .on("fetchingFailed",
                        function() {
                            markLoaded("proposals");
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
                    "contact": ["view/modal",
                                {url: "/static/template/contact.html",
                                 context: {config: config}}],
                    "list": ["view/list",
                             {collection: proposals,
                              subview: ProposalItemView}],
                    "info": ["view/info", {collection: proposals,
                                           subview: new ProposalInfoView()}]
                });

                appViews.layers = new LayersView({
                    el: "#layers"
                }).render();


                appViews.mapView = new MapView({
                    collection: proposals,
                    parcels: parcels,
                    el: "#map"
                });

                appViews.parcelInfoView = new ParcelInfoView({
                    el: "#parcel-info",
                    collection: parcels
                });

                appViews.filtersView = new FiltersView({
                    collection: proposals,
                    mapView: appViews.mapView
                });

                appViews.subscribeView = new SubscribeView({
                    collection: proposals,
                    el: "#subscribe",
                    mapView: appViews.mapView,
                    refLocation: refLocation,
                    distanceSubscription: !!(config.minSubscribeRadius || config.maxSubscribeRadius),
                    circleStyle: config.subscribeCircleStyle,
                    instructions: config.subscribeInstructions
                });

                appViews.imageView = new ImageView({
                    el: "#image-view",
                    step: function(id, dir) {
                        var sel = proposals.getSelection(),
                            next;

                        for (var i = 0, l = sel.length; i < l; i++) {
                            if ((next = sel[i].stepImage(id, dir)))
                                break;
                        }

                        return next && next.id;
                    }
                });

                appViews.appState = appState;
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
