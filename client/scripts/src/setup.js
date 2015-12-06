define(
    ["jquery", "permits", "permits-view", "map-view",
     "details-view", "minimap-view", "preview-view",
     "projects", "projects-view", "project-preview-view",
     "preview-manager", "tab-view", "filters-view",
     "glossary", "config"],
    function($, Permits, PermitsView, MapView, DetailsView,
             MinimapView, PreviewView, Projects, ProjectsView,
             ProjectPreview, PreviewManager, TabView,
             FiltersView, glossary, config) {
        return {
            start: function() {
                var proposals = new Permits(),
                    projects = new Projects();

                var showIntro = true;

                // Show introduction?
                $(document.body).toggleClass("main", !showIntro);
                if (showIntro) {

                }

                $("#explore").on("click", function(e) {
                    $(document).trigger("showMain");
                });

                var mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                $(document).one("showMain", function() {
                    $(document.body).addClass("main");
                    new MinimapView({
                        el: "#minimap",
                        linkedMap: mapView.map
                    });
                });

                var detailsView = new DetailsView({
                    collection: proposals,
                    el: "#overlay"
                });

                var proposalPreview = new PreviewView(),
                    projectPreview = new ProjectPreview(),
                    previewManager = new PreviewManager({
                        el: "#preview",
                        collections: [proposals, projects],
                        previewMap: {
                            project: projectPreview,
                            proposal: proposalPreview
                        }
                    });

                var tabView = new TabView({
                    el: "#data",
                    subviews: {
                        "proposals": new PermitsView({
                            collection: proposals
                        }),
                        "projects": new ProjectsView({
                            collection: projects
                        })
                    }
                });

                $(document)
                    .on("click", "#expand-data",
                        function(e) {
                            $("#data").removeClass("collapsed");
                        })
                    .on("click", "#collapse-data",
                        function(e) {
                            $("#data").addClass("collapsed");
                        });

                proposals.fetch({dataType: "jsonp"});
                projects.fetch({dataType: "jsonp"});

                // For testing:
                window.permits = proposals;

                glossary.init();

                return {
                    //permits: permitsView,
                    glossary: glossary,
                    map: mapView,
                    preview: previewManager,
                    details: detailsView,
                    filters: new FiltersView(),
                    exploreView: tabView
                };
            }
        };
    });
