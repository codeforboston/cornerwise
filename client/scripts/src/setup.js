define(
    ["jquery", "permits", "permits-view", "map-view",
     "filters-view", "collapsible-view", "layers-view",
     "config", "details-view", "routes"],
    function($, Permits, PermitsView, MapView, FiltersView,
             CollapsibleView, LayersView, config, DetailsView,
             routes) {
        return {
            start: function() {
                var permitsCollection = new Permits();

                // The views
                var permitsView = new PermitsView({
                    collection: permitsCollection
                });

                var mapView = new MapView({
                    collection: permitsCollection
                });

                var filtersView = new FiltersView({
                    collection: permitsCollection
                });

                var layersView = new CollapsibleView({
                    el: $("#layers")[0],
                    title: "Layers",
                    shown: true,
                    view: new LayersView()
                });
                layersView.render();

                permitsCollection.fetch({dataType: "jsonp"});

                // For testing:
                window.permits = permitsCollection;

                var detailsView = new DetailsView();
                routes.getRouter().on("route", function(name, args) {
                    if (name == "details" && args[0]) {
                        var proposal = permitsCollection.get(args[0]);

                        if (proposal) {
                            detailsView.show(proposal);
                        } else {
                            detailsView.hide();
                        }
                    } else {
                        detailsView.hide();
                    }
                });

                return {
                    filtersView: filtersView,
                    permits: permitsView,
                    layersView: layersView,
                    mapView: mapView
                };
            }
        };
    });
