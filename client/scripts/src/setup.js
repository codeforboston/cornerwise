define(
    ["jquery", "proposals", "map-view", "projects", "info-view",
    "proposal-info-view", "project-info-view", "proposal-view", "project-view",
     "layers-view", "filters-view", "glossary", "collapsible", "config", "routes",
     "view-manager", "ref-location", "legal-notice"],
    function($, Proposals, MapView, Projects, InfoView, ProposalInfoView,
             ProjectInfoView, ProposalItemView, ProjectItemView, LayersView, FiltersView,
             glossary, collapsible, config, routes, ViewManager, refLocation) {
        return {
            start: function() {
                var proposals = new Proposals(),
                    projects = new Projects(),
                    appViews = {
                        proposals: proposals,
                        projects: projects,
                        glossary: glossary
                    };

                routes.onStateChange("view", function(view, oldView) {
                    $(document.body)
                        .removeClass(oldView)
                        .addClass(view);

                    var showIntro = !view || view === "intro";

                    $(document.body).toggleClass("nointro", !showIntro);
                });

                refLocation.on("change:setMethod", function(_, method) {
                    var view = routes.getKey("view");
                    if (method !== "auto" && (!view || view === "intro")) {
                        routes.setHashKey("view", "main");
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
                              active: "proposals"}]
                });

                var infoView = new InfoView({
                    el: "#info",
                    startExpanded: routes.getKey("x") === "1",
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

                routes.onStateChange("view",
                                     function(newKey) {
                                         infoView.toggle(newKey == "main");
                                     });


                appViews.mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                appViews.layers = new LayersView({
                    el: "#layers .contents"
                }).render();

                appViews.filtersView = new FiltersView({
                    collection: proposals,
                    mapView: appViews.mapView
                });

                proposals.fetch({dataType: "jsonp"});
                projects.fetch({dataType: "jsonp"});

                collapsible.init();
                routes.init();
                glossary.init();


                return appViews;
            }
        };
    });
