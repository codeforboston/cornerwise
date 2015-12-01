define(
    ["jquery", "permits", "permits-view", "map-view",
     "details-view", "minimap-view", "preview-view",
     "projects", "projects-view", "project-preview-view",
     "preview-manager", "tab-view", "filters-view", "config"],
    function($, Permits, PermitsView, MapView, DetailsView,
             MinimapView, PreviewView, Projects, ProjectsView,
             ProjectPreview, PreviewManager, TabView,
             FiltersView, config) {
        return {
            start: function() {
                var proposals = new Permits(),
                    projects = new Projects();

                var mapView = new MapView({
                    collection: proposals,
                    el: "#map"
                });

                var minimapView = new MinimapView({
                    el: "#minimap",
                    linkedMap: mapView.map
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

                return {
                    //permits: permitsView,
                    map: mapView,
                    minimap: minimapView,
                    preview: previewManager,
                    details: detailsView,
                    filters: new FiltersView(),
                    exploreView: tabView
                };
            }
        };
    });
