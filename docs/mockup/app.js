App = {
    setupMinimap: function(map, minimap) {
        var rectLayer = L.rectangle(map.getBounds(),
                                    {stroke: true,
                                     weight: 2,
                                     color: "#ff0000",
                                     fill: true});
        minimap.addLayer(rectLayer);
        map.on("drag moveend resize zoomend", function(e) {
            rectLayer.setBounds(map.getBounds());
        });
        minimap.on("click", function(e) {
            map.setView(e.latlng);
        });

        $(minimap.getContainer()).on("mousedown", function(e) {
            var offset = $(this).offset();
            console.log(offset);

            function move(e) {
                var pointX = e.pageX - offset.left,
                    pointY = e.pageY - offset.top,
                    point = L.point(pointX, pointY),
                    latLng = minimap.unproject(L.point(pointX, pointY)),
                    currentCenter = rectLayer.getBounds().getCenter(),
                    dLat = latLng.lat - currentCenter.lat,
                    dLng = latLng.lng - currentCenter.lng;

                map.setView(latLng);
            }
            function mouseup(e) {
                $(document)
                    .off("mousemove", move)
                    .off("mouseup", mouseup);
            }

            $(document)
                .on("mousemove", move)
                .on("mouseup", mouseup);
        });
    },

    init: function() {
        var source = "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
            bounds = [[42.4190212708995, -71.07150077819824],
                      [42.372305415983895, -71.13570213317871]];

        var map = L.map("map"),
            proposals = L.featureGroup();

        window.map = map;

        map.addLayer(L.tileLayer(source));
        map.addLayer(proposals);
        map.fitBounds(bounds);
        //map.zoomControl.setPosition("bottomleft");

        var minimap = L.map("minimap",
                            {attributionControl: false,
                             dragging: false,
                             touchZoom: false,
                             scrollWheelZoom: false,
                             boxZoom: false,
                             zoomControl: false});
        minimap.setView(map.getCenter());
        minimap.setZoom(11);
        minimap.addLayer(L.tileLayer(source));
        App.setupMinimap(map, minimap);

        $.getJSON("https://raw.githubusercontent.com/cityofsomerville/geodata/master/somerville.geojson")
            .done(function(features) {
                map.addLayer(
                    L.geoJson(features,
                              {style: {
                                  stroke: true,
                                  weight: 2,
                                  color: "#EB4E12",
                                  fill: false
                              }}));
                minimap.addLayer(
                    L.geoJson(features,
                              {style: {
                                  stroke: true,
                                  weight: 2,
                                  fill: false
                              }}));

            });

        $.getJSON("http://localhost:3000/proposal/list")
            .done(function(response) {
                $(response.proposals).each(function(i, feature) {
                    if (feature.location) {
                        var marker = L.marker(feature.location).addTo(proposals);

                        marker.proposal = feature;

                        marker.on("click", function(e) {
                            map.setView(feature.location);
                            $(document).trigger("proposalSelected",
                                                [{proposal: feature,
                                                  marker: marker,
                                                  how: "click",
                                                  originalEvent: e}]);
                        });
                    }
                });
            });

        // var detailsMinimap = L.map("details-minimap",
        //                            {attributionControl: false,
        //                             dragging: false,
        //                             touchZoom: false,
        //                             boxZoom: false,
        //                             zoomControl: false});
        // detailsMinimap.addLayer(L.tileLayer(source));
        // detailsMinimap.setZoom(17);

        $(document).on("proposalSelected",
                       function(e, info) {
                           if (!info || !info.proposal) {
                               // Hide the viewer
                               $("#details").hide();
                               return;
                           }

                           var proposal = info.proposal,
                               image = proposal.images.length ?
                                   "http://localhost:3000" + proposal.images[0].src : "";

                           $("#details")
                               .find(".address").text(proposal.address)
                               .end()
                               .find("img.thumb").attr("src", image)
                               .end()
                               .show();

                           // detailsMinimap.setView(proposal.location);
                       });

        map.locate();

        function updateMarkers() {
            if (map.getZoom() >= 17) {
                var bounds = map.getBounds();
                proposals.eachLayer(function(marker) {
                    var images = marker.proposal.images;
                    if (!images || !images.length ||
                        !bounds.contains(marker.getLatLng()))
                        return;

                    marker._unzoomedIcon =
                        marker.icon || new L.Icon.Default();
                    var factor = Math.pow(2, (map.getZoom() - 17)),
                        size = L.point(100*factor, 75*factor);
                    marker.setIcon(L.divIcon({
                        className: "zoomed-proposal-marker",
                        iconSize: size,
                        html: "<img src='http://localhost:3000" +
                            images[0].thumb + "'/>"
                    }));
                });
            } else {
                proposals.eachLayer(function(marker) {
                    if (marker._unzoomedIcon) {
                        marker.setIcon(marker._unzoomedIcon);
                        delete marker._unzoomedIcon;
                    }
                });
            }
        }

        map.on("zoomend", updateMarkers)
            .on("moveend", updateMarkers);

        $("#main_activated").on("change", function(e) {
            if (this.checked) {
                $(document.body).addClass("main");
            } else {
                $(document.body).removeClass("main");
            }
        });

        if ($(document.body).hasClass("main")) {
            $("#main_activated").prop("checked", true);
        }

        $("a.toggler").click(function(e) {
            var parent = $(this).parent(),
                collapsed = parent.hasClass("collapsed");
            parent.toggleClass("collapsed", !collapsed)
                .toggleClass("expanded", collapsed);
        });


        // projects:
        var container = $("#data .content"),
            template = container.find(".project");

        $.getJSON("http://localhost:3000/project/list")
            .done(function(json) {
                var projects = json.projects.slice(0, 10);

                container.html("");

                projects.forEach(function(project) {
                    var div = template.clone();

                    div.find(".name").text(project.name).end()
                        .find(".category").text(project.category).end()
                        .find(".department").text(project.department).end()
                        .appendTo(container);

                    div.on("click", function(e) {
                        updateChart(project);
                    });

                });
            });

        function createChart(elt, w, h, data) {
            // Data:
            // {y: {max, min, values, labels}
            //  x: {max, min, values, labels}}
            var yMax = data.y.max,
                xMin = data.x.min,
                xRange = data.x.max - xMin,

                svgNS = "http://www.w3.org/2000/svg",
                g = document.createElementNS(svgNS, "g"),
                pieces = ["M"];

            var i = -1, len = x.values.length;

            for(; ++i < len;) {
                var x = (data.x.values[i] - xMin)/xRange,
                    y = data.y.values[i]/yMax;

                pieces.push("L", Math.floor(x*w), Math.floor(y*h));
            }

            var path = pieces.join(" "),
                pathElement = document.createElementNS(svgNS, "path");


            var budget = proj.budget,
                maxBudget = Math.max.apply(null,
                                           $.map(budget,
                                                 function(b) { return b.budget; })),
                startYear = new Date().getFullYear(),
                l = 10,
                svgNS = "http://www.w3.org/2000/svg",
                chart = $("#preview svg"),
                height = chart.height(),
                width = chart.width(),
                minY = 10,
                maxY = 90,
                dw = width/l,
                dh = height/maxBudget,
                lastX, lastY;

            $("#preview").show();

            chart = chart[0];

            for (var i = 0; i < l; i++) {
                var year = startYear + i,
                    yearBudget = budget[year] || { budget: 0 },
                    circle = document.createElementNS(svgNS, "circle"),
                    x = dw*i,
                    y = maxY - dh*yearBudget.budget;

                circle.setAttribute("class", "budget-point");
                circle.setAttribute("cx", x);
                circle.setAttribute("cy", y);
                circle.setAttribute("r", 3);
                chart.appendChild(circle);

                if (lastX !== undefined) {
                    var line = document.createElementNS(svgNS, "line");
                    line.setAttribute("x1", lastX);
                    line.setAttribute("y1", lastY);
                    line.setAttribute("x2", x);
                    line.setAttribute("y2", y);
                    line.setAttribute("class", "budget-line");
                    chart.appendChild(line);
                }

                lastX = x;
                lastY = y;
            }
        }

        function updateChart(proj) {
            var budget = proj.budget,
                maxBudget = Math.max.apply(null,
                                           $.map(budget,
                                                 function(b) { return b.budget; })),
                startYear = new Date().getFullYear(),
                l = 10,
                svgNS = "http://www.w3.org/2000/svg",
                chart = $("#preview svg"),
                height = chart.height(),
                width = chart.width(),
                minY = 10,
                maxY = 90,
                dw = width/l,
                dh = height/maxBudget,
                lastX, lastY;

            $("#preview").show();

            chart = chart[0];

            for (var i = 0; i < l; i++) {
                var year = startYear + i,
                    yearBudget = budget[year] || { budget: 0 },
                    circle = document.createElementNS(svgNS, "circle"),
                    x = dw*i,
                    y = maxY - dh*yearBudget.budget;

                circle.setAttribute("class", "budget-point");
                circle.setAttribute("cx", x);
                circle.setAttribute("cy", y);
                circle.setAttribute("r", 3);
                chart.appendChild(circle);

                if (lastX !== undefined) {
                    var line = document.createElementNS(svgNS, "line");
                    line.setAttribute("x1", lastX);
                    line.setAttribute("y1", lastY);
                    line.setAttribute("x2", x);
                    line.setAttribute("y2", y);
                    line.setAttribute("class", "budget-line");
                    chart.appendChild(line);
                }

                lastX = x;
                lastY = y;
            }
        }
    }
};
