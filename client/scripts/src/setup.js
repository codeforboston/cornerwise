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
                    projects = new Projects();

                // Show introduction?
                routes.onStateChange("view", function(view, oldView) {
                    $(document.body)
                        .removeClass(oldView)
                        .addClass(view);

                    var showIntro = !view || view === "intro";

                    $(document.body).toggleClass("main", !showIntro);

                    if (view === "main") {
                        new MinimapView({
                            el: "#minimap",
                            linkedMap: mapView.map
                        });
                    }
                });

                $(document).on("click", "#explore,#modal", function(e) {
                    routes.setHashKey("view", "main");

                    return false;
                });

                var mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                var detailsView = new DetailsView({
                    collection: proposals,
                    el: "#overlay"
                });

                var tabView = new TabView({
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
                proposals.on("selection",
                             function() {
                                 console.log(arguments);
                             });

                var proposalPreview = new PreviewView(),
                    projectPreview = new ProjectPreview(),
                    previewManager = new PreviewManager({
                        el: "#preview",
                        collections: {
                            proposals: proposals,
                            projects: projects
                        },
                        previewMap: {
                            projects: projectPreview,
                            proposals: proposalPreview
                        },
                        viewSelection: tabView
                    });

                var layers = new LayersView({
                    el: "#layers .contents"
                }).render();

                proposals.fetch({dataType: "jsonp"});
                projects.fetch({dataType: "jsonp"});

                // For testing:
                window.proposals = proposals;

                collapsible.init();
                routes.init();
                glossary.init();

                var filtersView = new FiltersView();

                return {
                    glossary: glossary,
                    map: mapView,
                    preview: previewManager,
                    details: detailsView,
                    exploreView: tabView,
                    layersView: layers,
                    filtersView: filtersView
                };
            }
        };
    });
