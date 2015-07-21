define(
    ["jquery", "permits", "permits-view", "map-view",
     "filters-view", "collapsible-view", "layers-view",
     "config"],
    function($, Permits, PermitsView, MapView, FiltersView,
             CollapsibleView, LayersView, config) {
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

                return {
                    permits: permitsView,
                    mapView: mapView,
                    filtersView: filtersView
                };
            }
        };
    });
