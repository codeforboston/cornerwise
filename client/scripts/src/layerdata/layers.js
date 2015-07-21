define(["utils"], function($u) {
    return [
        {
            "title": "Green Line Extension",
            "tags": ["capital projects", "mbta"],
            "colors": "green",
            "source": "/src/layerdata/glx.geojson",
            "template": '<span>Opens:</span> <%= projectedYear %> (estimate)'
        },

        {
            "title": "Community Path",
            "tags": [],
            "colors": "orange",
            "source": "/src/layerdata/community_path.geojson",
            "template": null
        }
    ];
});
