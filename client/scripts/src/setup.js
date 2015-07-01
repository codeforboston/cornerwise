define(
    ["permits", "permits-view", "map-view", "filters-view", "config"],
    function(Permits, PermitsView, MapView, FiltersView, config) {
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
