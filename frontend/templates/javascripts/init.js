var resourceViewEnabled = false;
var currentlySelectedResource = null;
var map = null, inlineMap = null;
var markers = [];
var polygons = [];
var contourPolygons = [];
var licensePolygons = [];
var mapWasInitialized = false;
var resourceType = "";
var regionId = "", areaId = "";
var resourceKind = "";
var resourceGroup = "";
var language = "ru";
var resourceKind = "";
var resourceGroup = ""
var resourceType = "";
var initialNumClusters = 4;
var numClusters = 13;
var clusters = {};
var tokenVerificationInterval = 2*60*1000;
var sidePanelFolded = true;
var defaultDistance = 100 * 1000; //in meters
var enableSearchFromPoint = false;
var markerClicked = false;
var searchParamtersChanged = false;
var verificationFailed = false;
var polygonColors = ["#00cc99", "#ff0066", "#ffff00", "#ff9900", "#99ccff", "#666699", "#009900", "#666633", "#cc00ff"];

function CustomMarker(latlng, map, value) {
	this.latlng_ = latlng;
	this.setMap(map);
	this.value_ = value;
}

function LabelMarker(latlng, map, value) {
	this.latlng_ = latlng;
	this.setMap(map);
	this.value_ = value;
}

function initInlineMap() {
	inlineMap = new google.maps.Map(document.getElementById("inlinemap"), {
		zoom: 10,
		center: config.MAP_CENTER,
		mapTypeId: google.maps.MapTypeId.SATELLITE,
		scaleControl: true,
		scrollwheel: false,
		draggable: true,
		fullscreenControl: true,
		zoomControl: true,
		mapTypeControl: true,
		streetViewControl: false,
		zoomControlOptions: {
			position: google.maps.ControlPosition.LEFT_BOTTOM
		}
	});
}

function initMap() {
	map = new google.maps.Map(document.getElementById("map"), {
		zoom: config.DEFAULT_ZOOM_LEVEL,
		center: config.MAP_CENTER,
		mapTypeId: google.maps.MapTypeId.TERRAIN,
		scaleControl: false,
		scrollwheel: false,
		draggable: true,
		fullscreenControl: false,
		zoomControl: true,
		mapTypeControl: true,
		streetViewControl: false,

		mapTypeControlOptions: {
			position: google.maps.ControlPosition.RIGHT_BOTTOM
		},
		zoomControlOptions: {
			position: google.maps.ControlPosition.LEFT_BOTTOM
		}
	});

	google.maps.event.trigger(map, "resize");

	LabelMarker.prototype = new google.maps.OverlayView();
	LabelMarker.prototype.draw = function() {
		var self = this;
		var div = this.div_;
		if (!div) {
			div = this.div_ = document.createElement("div");
			div.className = "label";
			var span = document.createElement("div");
			span.appendChild(document.createTextNode(this.value_));
			span.className = "centered small";
			div.appendChild(span);
			var panes = this.getPanes();
			panes.overlayImage.appendChild(div);
		}
		var point = this.getProjection().fromLatLngToDivPixel(this.latlng_);
		if (point) {
			div.style.left = (point.x) + "px";
			div.style.top = (point.y - 24) + "px";
		}
	}

	LabelMarker.prototype.remove = function() {
		if (this.div_) {    
			this.div_.parentNode.removeChild(this.div_);
			this.div_ = null;
		}
	}

	LabelMarker.prototype.getPosition = function() {
		return this.latlng_;
	}

	CustomMarker.prototype = new google.maps.OverlayView();
	CustomMarker.prototype.draw = function() {
		var self = this;
		var div = this.div_;
		if (!div) {
			div = this.div_ = document.createElement("div");
			div.className = "marker";
			var span = document.createElement("div");
			regionId = $("#regions").val();
			areaId = $("#areas").val();
			if (this.value_ != "1")
				span.appendChild(document.createTextNode(this.value_));
			span.className = "centered";
			var img = document.createElement("img");
			img.src = "images/circle.png";
			//if (this.value_ != "1" || (regionId == -1 || regionId == "")) {
				img.height = "24";
				img.width = "24";
			//} else {
			//	img.width = "24";
			//	img.height = "24";
			//}
			div.appendChild(img);
			div.appendChild(span);
			google.maps.event.addDomListener(div, "click", function(event) {
				google.maps.event.trigger(self, "click");
			});
			var panes = this.getPanes();
			panes.overlayImage.appendChild(div);
		}
		var point = this.getProjection().fromLatLngToDivPixel(this.latlng_);
		if (point) {
			div.style.left = (point.x) + "px";
			//if (this.value_ != "1" || (regionId == -1 || regionId == ""))
			//	div.style.top = (point.y - 48) + "px";
			//else
				div.style.top = (point.y - 24) + "px";
		}
	}

	CustomMarker.prototype.remove = function() {
		if (this.div_) {    
			this.div_.parentNode.removeChild(this.div_);
			this.div_ = null;
		}
	}

	CustomMarker.prototype.getPosition = function() {
		return this.latlng_;
	}
};
