function initMap() {
    var location = new google.maps.LatLng(28.620585, 77.228609)
    mapOptions = {
        zoom: 12,
        center: location,
        mapTypeId: google.maps.MapTypeId.RoadMap
    }
    map = new google.maps.Map(document.getElementById('map'), mapOptions)
    var selectedShape
    var drawingManager = new google.maps.drawing.DrawingManager({
        //drawingMode: google.maps.drawing.OverlayType.MARKER,
        drawingControl: true,
        drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_CENTER,
            drawingModes: [
                google.maps.drawing.OverlayType.MARKER,
                google.maps.drawing.OverlayType.CIRCLE,
                google.maps.drawing.OverlayType.POLYGON,
                google.maps.drawing.OverlayType.RECTANGLE
            ]
        },
        markerOptions: {
            //icon: 'images/beachflag.png'
        },
        circleOptions: {
            fillColor: '#ffff00',
            fillOpacity: 0.2,
            strokeWeight: 3,
            clickable: false,
            editable: true,
            zIndex: 1
        },
        polygonOptions: {
            clickable: true,
            draggable: false,
            editable: true,
            // fillColor: '#ffff00',
            fillColor: '#ADFF2F',
            fillOpacity: 0.5,

        },
        rectangleOptions: {
            clickable: true,
            draggable: true,
            editable: true,
            fillColor: '#ffff00',
            fillOpacity: 0.5,
        }
    });


    drawingManager.setMap(map);

    google.maps.event.addListener(drawingManager, 'overlaycomplete', function(event) {
      var newShape = event.type
      selectedShape = newShape;

        switch (event.type) {
          case google.maps.drawing.OverlayType.MARKER:
            map.data.add(new google.maps.Data.Feature({
              geometry: new google.maps.Data.Point(event.overlay.getPosition())
            }));
            break;
          case google.maps.drawing.OverlayType.RECTANGLE:
            var b = event.overlay.getBounds(),
              p = [b.getSouthWest(), {
                  lat: b.getSouthWest().lat(),
                  lng: b.getNorthEast().lng()
                },
                b.getNorthEast(), {
                  lng: b.getSouthWest().lng(),
                  lat: b.getNorthEast().lat()
                }
              ]
            map.data.add(new google.maps.Data.Feature({
              geometry: new google.maps.Data.Polygon([p])
            }));
            break;
          case google.maps.drawing.OverlayType.POLYGON:
            map.data.add(new google.maps.Data.Feature({
              geometry: new google.maps.Data.Polygon([event.overlay.getPath().getArray()])
            }));
            break;
          case google.maps.drawing.OverlayType.POLYLINE:
            map.data.add(new google.maps.Data.Feature({
              geometry: new google.maps.Data.LineString(event.overlay.getPath().getArray())
            }));
            break;
          case google.maps.drawing.OverlayType.CIRCLE:
            map.data.add(new google.maps.Data.Feature({
              properties: {
                radius: event.overlay.getRadius()
              },
              geometry: new google.maps.Data.Point(event.overlay.getCenter())
            }));
            break;
        }

      });
      google.maps.event.addDomListener(document.getElementById('save'), 'click', function() {
        if (!selectedShape) {
          alert("There are no shape selected");
          return 
        }else{
          map.data.toGeoJson(function(obj) {
            document.getElementById('geojson').value = JSON.stringify(obj);
          });
        }
        
      })
    }

// Apply listeners to refresh the GeoJson display on a given data layer.
function bindDataLayerListeners(dataLayer) {
    dataLayer.addListener('addfeature', savePolygon);
    dataLayer.addListener('removefeature', savePolygon);
    dataLayer.addListener('setgeometry', savePolygon);
}

function savePolygon() {
    map.data.toGeoJson(function (json) {
        //localStorage.setItem('geoData', JSON.stringify(json));
    });
}
