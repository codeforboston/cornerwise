define(
    ["jquery", "proposals", "collection-manager", "map-view", "proposal-view", "glossary", "config", "app-state", "view-manager", "ref-location", "legal-notice"],
    function($, Proposals, CollectionManager, MapView, ProposalItemView, 
             glossary, config, appState, ViewManager, refLocation) {
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

                // Configure modal views here!
                // See viewManager.js for documentation and examples.
                new ViewManager({
                    // Simple view that will load the about page from a
                    // static URL into a modal overlay when the 'view'
                    // parameter in the hash.
                    "about": ["modal-view", {url: "/static/template/about.html"}],
                    "events": ["modal-view",
                               {url: "/static/template/eventBrowser.html"}],
                    "list": ["list-view",
                             {collection: proposals,
                              subview: ProposalItemView}]
                });

                require(["info-view", "proposal-info-view", "layers-view"],
                        function(InfoView, ProposalInfoView, LayersView) {
                            var infoView = new InfoView({
                                el: "#info",
                                startExpanded: appState.getKey("x") === "1",
                                subview: new ProposalInfoView(),
                                collection: proposals
                            });
                            appViews.info = infoView;

                            appState.onStateKeyChange(
                                "view",
                                function(newKey) {
                                    infoView.toggle(newKey == "main");
                                });
                            infoView.render();

                            var layersView = new LayersView({
                                el: "#map-options"
                            }).render();
                        });


                appViews.mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                require(["filters-view"],
                        function(FiltersView) {
                            appViews.filtersView = new FiltersView({
                                collection: proposals,
                                mapView: appViews.mapView
                            });
                        });

                appState.init();
                glossary.init();

                return appViews;
            }
        };
    });
