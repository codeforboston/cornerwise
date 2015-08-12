def geojson_data(geom):
    return {
        "type": geom.__class__.__name__,
        "coordinates": geom.coords
    }
