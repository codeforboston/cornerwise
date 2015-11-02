#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import tempfile

def export(city="Somerville",
           out="/client/scripts/src/layerdata/neighborhoods.json",
           shapefile="/data/ZillowNeighborhoods-MA/ZillowNeighborhoods-MA.shp",
           layername="ZillowNeighborhoods-MA"):
    tmpdir = tempfile.mkdtemp()
    tmp = os.path.join(tmpdir, "neighborhood.json")
    print(["ogr2ogr", "-f", "GeoJSON", tmp, shapefile, layername])
    status = subprocess.call(["ogr2ogr", "-f", "GeoJSON", tmp, shapefile, layername])

    if not status:
        with open(tmp, "r") as f:
            data = json.load(f)

            # Filter the feature collection:
            features = data["features"]
            data["features"] = [feature for feature in features \
                                if feature["properties"]["CITY"] == city]

            print("Found features:", len(data["features"]))

        with open(out, "w") as outfile:
            json.dump(data, outfile)


def do_main(args):
    #parser = argparse.ArgumentParser(description="Generate a")
    export()

if __name__ == "__main__":
    do_main(sys.argv)
