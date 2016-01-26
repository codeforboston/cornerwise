define(
    ["jquery", "proposals", "proposals-view", "map-view", "projects",
     "projects-view", "info-view", "proposal-info-view",
     "project-info-view", "layers-view", "filters-view", "glossary",
     "collapsible", "config", "routes", "view-manager", "ref-location",
     "legal-notice"],
    function($, Proposals, ProposalsView, MapView,
             Projects, ProjectsView, InfoView, ProposalInfoView,
             ProjectInfoView, LayersView, FiltersView,
             glossary, collapsible, config, routes, ViewManager,
             refLocation) {
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

                    $(document.body).toggleClass("main", !showIntro);
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
                                       {collection: projects}]
                });

                new InfoView({
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


                appViews.mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                appViews.layers = new LayersView({
                    el: "#layers .contents"
                }).render();

                proposals.fetch({dataType: "jsonp"});
                projects.fetch({dataType: "jsonp"});

                collapsible.init();
                routes.init();
                glossary.init();

                appViews.filtersView = new FiltersView();

                return appViews;
            }
        };
    });
