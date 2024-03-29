/*Code is taken from: 
https://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds 
*/
function getBoundsZoomLevel(bounds, mapDim) {
	var WORLD_DIM = { height: 256, width: 256 };
	var ZOOM_MAX = 21;

	function latRad(lat) {
		var sin = Math.sin(lat * Math.PI / 180);
		var radX2 = Math.log((1 + sin) / (1 - sin)) / 2;
		return Math.max(Math.min(radX2, Math.PI), -Math.PI) / 2;
	}

	function zoom(mapPx, worldPx, fraction) {
		return Math.log(mapPx / worldPx / fraction) / Math.LN2;
	}

	var ne = bounds.getNorthEast();
	var sw = bounds.getSouthWest();
	
	var latFraction = (latRad(ne.lat()) - latRad(sw.lat())) / Math.PI;

	var lngDiff = ne.lng() - sw.lng();
	var lngFraction = ((lngDiff < 0) ? (lngDiff + 360) : lngDiff) / 360;

	var latZoom = zoom(mapDim.height, WORLD_DIM.height, latFraction);
	var lngZoom = zoom(mapDim.width, WORLD_DIM.width, lngFraction);
	return Math.min(latZoom, lngZoom, ZOOM_MAX);
}

/*
 Approximates the geometrical center for the map
*/
function getBoundsMapCenter(bounds) {
	var ne = bounds.northEast;
	var sw = bounds.southWest;
	return {
		'lat': (ne.lat + sw.lat) / 2,
		'lng': (ne.lng + sw.lng) / 2
	}
}
