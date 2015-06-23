define(["permits", "permits-view", "map-view"], function(Permits, PermitsView, MapView) {
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

            permitsCollection.fetch();

            return {
                permits: permitsView,
                mapView: mapView
            };
        }
    };
});
