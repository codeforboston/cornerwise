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

                var detailsView = new DetailsView({collection: permitsCollection});
                return {
                    filters: filtersView,
                    permits: permitsView,
                    layers: layersView,
                    map: mapView,
                    details: detailsView
                };
            }
        };
    });
