define(
    ["jquery", "proposals", "projects", "collection-manager", "map-view", "proposal-view", "project-view", "glossary", "config", "appState", "view-manager", "ref-location", "legal-notice"],
    function($, Proposals, Projects, CollectionManager, MapView, ProposalItemView, ProjectItemView,
             glossary, config, appState, ViewManager, refLocation) {
        return {
            start: function() {
                var proposals = new Proposals(),
                    projects = new Projects(),
                    cm = new CollectionManager({
                        collections: {
                            proposals: proposals,
                            projects: projects
                        }
                    }),
                    appViews = {
                        proposals: proposals,
                        projects: projects,
                        glossary: glossary
                    };

                appState.onStateChange("view", function(view, oldView) {
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
                    "projectSummary": ["projects-summary-view",
                                       {collection: projects}],
                    "list": ["list-view",
                             {collections: {proposals: proposals,
                                            projects: projects},
                              subviews: {proposals: ProposalItemView,
                                         projects: ProjectItemView},
                              manager: cm,
                              active: "proposals"}]
                });

                require(["info-view", "proposal-info-view", "project-info-view",
                         "minilist-view"],
                        function(InfoView, ProposalInfoView, ProjectInfoView, MiniListView) {
                            var infoView = new InfoView({
                                el: "#info",
                                startExpanded: appState.getKey("x") === "1",
                                defaultView: new MiniListView({
                                    collection: proposals
                                }),
                                views: {
                                    "proposal": new ProposalInfoView(),
                                    "project": new ProjectInfoView()
                                },
                                collections: {
                                    "proposal": proposals,
                                    "project": projects
                                }
                            });
                            appViews.info = infoView;

                            appState.onStateChange("view",
                                                 function(newKey) {
                                                     infoView.toggle(newKey == "main");
                                                 });
                        });


                appViews.mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                require(["layers-view"],
                        function(LayersView) {
                            appViews.layers = new LayersView({
                                el: "#layers .contents"
                            }).render();
                        });

                require(["filters-view"],
                        function(FiltersView) {
                            appViews.filtersView = new FiltersView({
                                collection: proposals,
                                mapView: appViews.mapView
                            });
                        });

                proposals.fetch({dataType: "jsonp"});
                projects.fetch({dataType: "jsonp"});

                appState.init();
                glossary.init();
                $(document).on("click", "a.ref-loc", function(e) {
                    $("#ref-address-form input").focus().select();
                    return false;
                });

                return appViews;
            }
        };
    });
