define(
    ["jquery", "proposals", "proposals-view", "map-view",
     "details-view", "minimap-view", "preview-view",
     "projects", "projects-view", "project-preview-view",
     "preview-manager", "tab-view", "layers-view",
     "filters-view", "glossary", "collapsible", "config", "backbone",
     "routes", "legal-notice"],
    function($, Proposals, ProposalsView, MapView, DetailsView,
             MinimapView, PreviewView, Projects, ProjectsView,
             ProjectPreview, PreviewManager, TabView, LayersView,
             FiltersView, glossary, collapsible, config, B, routes) {
        return {
            start: function() {
                var proposals = new Proposals(),
                    projects = new Projects(),
                    appViews = {
                        glossary: glossary
                    };

                // Show introduction?
                routes.onStateChange("view", function(view, oldView) {
                    $(document.body)
                        .removeClass(oldView)
                        .addClass(view);

                    var showIntro = !view || view === "intro";

                    $(document.body).toggleClass("main", !showIntro);

                    if (view === "main" && !appViews.minimap) {
                        appViews.minimap = new MinimapView({
                            el: "#minimap",
                            linkedMap: appViews.mapView.map
                        });
                    }
                });

                $(document).on("click", "#explore,#modal", function(e) {
                    routes.setHashKey("view", "main");

                    return false;
                });

                appViews.mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                appViews.detailsView = new DetailsView({
                    collection: proposals,
                    el: "#overlay"
                });

                appViews.tabView = new TabView({
                    el: "#data",
                    subviews: {
                        "proposals": new ProposalsView({
                            collection: proposals
                        }),
                        "projects": new ProjectsView({
                            collection: projects,
                            proposals: proposals
                        })
                    }
                });

                appViews.proposalPreview = new PreviewView();
                appViews.projectPreview = new ProjectPreview();
                appViews.previewManager = new PreviewManager({
                    el: "#preview",
                    collections: {
                        proposals: proposals,
                        projects: projects
                    },
                    previewMap: {
                        projects: appViews.projectPreview,
                        proposals: appViews.proposalPreview
                    },
                    viewSelection: appViews.tabView
                });
                appViews.layers = new LayersView({
                    el: "#layers .contents"
                }).render();

                proposals.fetch({dataType: "jsonp"});
                projects.fetch({dataType: "jsonp"});

                collapsible.init();
                routes.init();
                glossary.init();

                //var filtersView = new FiltersView();

                return appViews;
            }
        };
    });
