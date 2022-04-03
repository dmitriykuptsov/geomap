function getUrlVars() {
	var vars = {};
    var parts = window.location.href.replace(/[?&]+([a-z0-9]+)=([0-9\w%]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

function showMessageWindow(message) {
	$("#message-window").html(message);
	$("#message-window").css("left", "calc(50% - 300px)");
	$("#message-window").css("top", "calc(50% - 150px)");
	$("#message-window").show();

	$("#message-window-close-button").show();
	$("#message-window-close-button").css("left", "calc(50% + 276px)");
	$("#message-window-close-button").css("top", "calc(50% - 174px)");
}

function hideMessageWindow() {
	$("#message-window").hide();
	$("#message-window-close-button").hide();				
}

hideMessageWindow();

function hideForms() {
	$("#resource-info").hide();
	$("#image-pane").hide();
	$("#contours-pane").hide();
	$("#close_contours_pane").hide();
	$("#help-info").hide();
	$("#login-info").hide();
	$(".login-message").hide();
	$("#clustered-resources-info").hide();
	$("#help-close-button").hide();
	$("#login-window-close-button").hide();
	$("#clustered-resources-close-button").hide();
	$(".resource-info-button").hide();
	$(".resource-print-button").hide();
	$("#close_image_pane").hide();
	$("#magnify_image_pane").hide();
	$("#magnify_contours_pane").hide();
	$("#resources").hide();
	$("#distances_label").hide();
	$("#distances").hide();
	$("#extended-search-form").hide();
	$("#extended-search-form-close-button").hide();
	$("#registration-form").hide();
	$("#registration-form-close-button").hide();
}

hideForms();

Handlebars.registerHelper("ifCond", function (v1, operator, v2, options) {
	switch (operator) {
	case "and":
		return (v1 && v2) ? options.fn(this) : options.inverse(this);
	case "or":
		return (v1 || v2) ? options.fn(this) : options.inverse(this);
	default:
		return options.inverse(this);
	}
});

Handlebars.registerHelper("ifCond3", function (v1, operator, v2, v3, options) {
	switch (operator) {
	case "and":
		return (v1 && v2 && v3) ? options.fn(this) : options.inverse(this);
	case "or":
		return (v1 || v2 || v3) ? options.fn(this) : options.inverse(this);
	default:
		return options.inverse(this);
	}
});

Handlebars.registerHelper("ifEq", function (operator1, operator2, options) {
	if(operator1 == operator2)
        return options.fn(this);
    else
        return options.inverse(this);
});

function showSpinner() {
	$("#spinner").show();
}

function hideSpinner() {
	$("#spinner").hide();
}

function showHideControls() {
	if (regionId == -1 || regionId == "") {
		$("#areas").hide();
		$("#areas_label").hide();
	} else {
		$("#areas").show();
		$("#areas_label").show();
	}
	if (resourceKind == -1 || resourceKind == "") {
		$("#resource_groups").hide();
		$("#resource_groups_label").hide();
	} else {
		$("#resource_groups").show();
		$("#resource_groups_label").show();
	}
	console.log(resourceGroup);
	if (resourceGroup == -1 || resourceGroup == "") {
		$("#resource_types").hide();
		$("#resource_types_label").hide();
	} else {
		$("#resource_types").show();
		$("#resource_types_label").show();
	}
}

function fillDdValues() {
	regionId = $("#regions").val();
	areaId = $("#areas").val();
	resourceKind = $("#resource_kinds").val();
	resourceGroup = $("#resource_groups").val();
	resourceType = $("#resource_types").val();
	if (regionId == -1) {
		areaId = "";
	}
	if (resourceKind == -1) {
		resourceGroup = "";
		resourceType = "";
	}
	if (resourceGroup == -1) {
		resourceType = "";
	}
}

$(document).on("click","#message-window-close-button", function() {
	hideMessageWindow();
});

$(document).on("click", "#registration-form-close-button", function() {
	$("#registration-form-close-button").hide();
	$("#registration-form").hide();
});


$(document).on("click", "#request_registration", function() {
	$("#registration-form").css("left", "calc(50% - 300px)");
	$("#registration-form").css("top", "calc(50% - 150px)");
	$("#registration-form").show();
	$("#registration-form-close-button").show();
	$("#registration-form-close-button").css("left", "calc(50% + 276px)");
	$("#registration-form-close-button").css("top", "calc(50% - 174px)");
});


$(document).ready(function() {
	
	language = getUrlVars()["language"];
	
	if (!language) {
		language = "ru";
	}

	$("body").tooltip({ 
		selector: "[data-toggle=tooltip]",
		tooltipClass: "ui-tooltip"
	});

	$.get("templates/templates.html", function (data) {
		$("#templates").html(data);

		var source = document.getElementById("header-template").innerHTML;
		var template = Handlebars.compile(source);
		
		$("#header").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("print-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$(".resource-print-button").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("resource-info-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$(".resource-info-button").html(template(
			{
				"language": language
			}
		));

		
		var source = document.getElementById("clustered-resources-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#clustered-resources-close-button").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("image-pane-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#close_image_pane").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("magnify-image-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#magnify_image_pane").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("contours-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#close_contours_pane").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("magnify-conotours-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#magnify_contours_pane").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("login-info-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#login-window-close-button").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("registration-form-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#registration-form-close-button").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("extended-search-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#extended-search-form-close-button").html(template(
			{
				"language": language
			}
		));


		var source = document.getElementById("help-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#help-close-button").html(template(
			{
				"language": language
			}
		));

		var source = document.getElementById("message-window-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#message-window-close-button").html(template(
			{
				"language": language
			}
		));

		var source   = document.getElementById("registration-form-template").innerHTML;
		var template = Handlebars.compile(source);
		
		$("#registration-form").html(template(
			{
				"language": language
			}
		));
		
		var source   = document.getElementById("extended-search-template").innerHTML;
		var template = Handlebars.compile(source);
		$("#extended-search-form").html(template(
			{
				"language": language
			}
		));
		
		var source   = document.getElementById("registration-form-template").innerHTML;
		var template = Handlebars.compile(source);
		
		$("#registration-form").html(template(
			{
				"language": language
			}
		));

		geomap.checkToken(function(result) {
			if (result.authenticated) {
				$(document).find("#login").attr("src","images/logout.png");
			} else {
				$(document).find("#login").attr("src","images/login.png");	}
		}, function() {
			hideForms();
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		hideForms();

		geomap.getListOfRegions(function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var regions = result.data;
			var source   = document.getElementById("control-regions-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#regions").html(template(
				{
					regions: regions,
					language: language
				}
			));
		}, function () {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		geomap.getDepositStatuses(function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var statuses = result.data;
			var source   = document.getElementById("control-statuses-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#statuses").html(template(
				{
					statuses: statuses,
					language: language
				}
			));
		}, function() {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		geomap.getListOfAreas(regionId, function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var areas = result.data;
			var source   = document.getElementById("control-areas-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#areas").html(template(
				{
					areas: areas,
					language: language
				}
			));
		}, function() {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		geomap.getListOfResourceKinds( 
			function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var resourceKinds = result.data;
			var source   = document.getElementById("control-resource-kinds-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#resource_kinds").html(template(
				{
					resource_kinds: resourceKinds,
					language: language
				}
			));
		}, function() {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		geomap.getListOfResourceGroups(resourceKind, 
			function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var resourceGroups = result.data;
			var source   = document.getElementById("control-resource-groups-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#resource_groups").html(template(
				{
					resource_groups: resourceGroups,
					language: language
				}
			));
		}, function() {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		geomap.getListOfResourceTypes(resourceKind, resourceGroup,
			function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var resourceTypes = result.data;
			var source   = document.getElementById("control-resource-types-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#resource_types").html(template(
				{
					resource_types: resourceTypes,
					language: language
				}
			));
		}, function() {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});
		
		showHideControls();
		var itemsToLoad = 2;
		showSpinner();
		
		geomap.getRegionDecorations(regionId, function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var decorations = result.data;
			geomap.getRegionBorders(regionId, function(result) {
				if (!result.authenticated) {
					verificationFailed = true;
					$(document).find("#login").attr("src","images/login.png");
				}
				var coords = result.data;
				createRegionBorders(coords, decorations);
				if (--itemsToLoad == 0) {
					hideSpinner();
				}
			}, function(error) {
				hideSpinner();
				showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
			});
		}, function(error) {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		geomap.getResources(regionId, areaId, 
			language, resourceKind, resourceGroup,
			resourceType, 
			$("#resource_name").val(), 
			//numClusters,
			"All",
			$("#statuses").val(),
			$("#remainder").val(),
			function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var resources = result.data;
			doFillResources(resources);
			if (--itemsToLoad == 0) {
				hideSpinner();
			}
		}, function(error) {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});
	}, "html");

	$("#resource_name").val("");
	$("#remainder").val($("#remainder option:first").val());
	showSpinner();
	setInterval(function() {
		geomap.checkToken(function(result) {
			if (!result.authenticated) {
				if (!verificationFailed)	{
					hideForms();
					if (enableSearchFromPoint) {				
						$("#distances").show();
						$("#distances_label").show();
					}
					searchParamtersChanged = true;
					verificationFailed = true;
					$(document).find("#login").attr("src","images/login.png");
					$(document).find("#extended_search_submit")[0].click();
				}
			} else {
				if (verificationFailed)	{
					hideForms();
					if (enableSearchFromPoint) {				
						$("#distances").show();
						$("#distances_label").show();
					}
					searchParamtersChanged = true;
					verificationFailed = false;
					$(document).find("#login").attr("src","images/logout.png");
					$(document).find("#extended_search_submit")[0].click();
				}
			}
		}, function() {
			hideForms();
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});
	}, tokenVerificationInterval);

	$(document).on("click", "#request_registration_submit", function(event) {
		var first_name = $("#r_first_name").val();
		var last_name = $("#r_last_name").val();
		var email_address = $("#r_email").val();
		var phone_number = $("#r_phone").val();
		var description = $("#r_description").val();
		event.preventDefault();
		if (!new RegExp("^[a-z\u0430-\u044f]{1,99}$", "i").exec(first_name)) {
			showMessageWindow("Неверное имя (имя должно содержать только буквы)");
			return;
		}
		if (!new RegExp("^[a-z\u0430-\u044f]{1,99}$", "i").exec(last_name)) {
			showMessageWindow("Неверная фамилия (фамилия должна содержать только буквы)");
			return;
		}
		if (!new RegExp("^[a-zA-Z0-9._-]+@[a-zA-Z]+\.[a-zA-Z]{2,4}$").exec(email_address)) {
			showMessageWindow("Неверный адрес эл. почты");
			return;
		}
		if (!new RegExp("^\\+[0-9]{1,3}-?[0-9]{2,3}-?[0-9]{5,7}$").exec(phone_number)) {
			showMessageWindow("Неверный телефон");
			return;
		}
		if (!new RegExp("^[\u0430-\u044f\s0-9,.\\sa-z]{1,1000}$", "i").exec(description)) {
			showMessageWindow("Неверное описание");
			return;
		}
		showSpinner();
		geomap.requestRegistration(
			first_name, 
			last_name, 
			phone_number, 
			email_address, 
			description, function(result) {
				hideSpinner();
				if (result.status === "success") {
					showMessageWindow("Запрос принят. Ждите сообщение от модератора.");
				} else {
					showMessageWindow(result.reason);
				}
			}, function(error) {
				hideSpinner();
				showMessageWindow("Возникла системная ошибка. Повторите запрос позже.");
			}
		);
	});

	$(document).on("click", "#login", function(event) {
		event.preventDefault();
		showSpinner();
		geomap.checkToken(function(result) {
			hideSpinner();
			if (!result.authenticated) {
				var source   = document.getElementById("login-template").innerHTML;
				var template = Handlebars.compile(source);
				output       = template({language: language});
				$("#login-info").html(output);
				$("#login-info").css("left", "calc(50% - 300px)");
				$("#login-info").css("top", "calc(50% - 150px)");
				$("#login-info").show();
				$("#login-window-close-button").show();
				$("#login-window-close-button").css("left", "calc(50% + 276px)");
				$("#login-window-close-button").css("top", "calc(50% - 174px)");
				$(document).on("click","#login-window-close-button", function() {
					$("#login-info").hide();
					$("#login-window-close-button").hide();
				});
				$(document).on("click", "#login-button", function(event) {
					geomap.authenticate($("#username").val(), $("#password").val(), function(result) {
						if (result.status === "success") {
							//$("#login").attr("src","images/logout.png");
							$(document).find("#login").attr("src","images/logout.png");
							searchParamtersChanged = true;
							$(".login-message").show();
							$(".login-message").html("<p>Вход выполнен успешно</p>");
							$(".login-message").fadeOut(1000);
							$(document).find("#extended_search_submit")[0].click();
							verificationFailed = false;
							setTimeout(function() {
								$(".login-message").hide();
								$("#login-info").hide();
								$("#login-window-close-button").hide();
							}, 2000);
						} else {
							showMessageWindow("Неверное имя пользователя или пароль");
						}
					}, function(error) {
						showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
					});
					
					event.preventDefault();
				});
			} else {
				geomap.logout(function(result) {
					if (result.status === "success") {
						searchParamtersChanged = true;
						//$(document).find("#login").attr("src","images/login.png");
						$(document).find("#login").attr("src","images/login.png");
						$(document).find("#extended_search_submit")[0].click();
					} else {
						showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
					}
				}, function(error) {
					hideSpinner();
					showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
				});
			}
		}, function() {
			hideForms();
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});
	});
	$(document).on("click", "#settings", function() {
		window.open("admin.html");
	});
	$(document).on("click", "#fold", function() {
		if (sidePanelFolded) {
			$("#resources").show();
		} else {
			$("#resources").hide();
		}
		sidePanelFolded = !sidePanelFolded;
		google.maps.event.trigger(map, "resize");
	});

	$(document).on("click", "#search_by_location", function() {
		if (enableSearchFromPoint) {
			$("#search_by_location").attr("src","images/disabled_location.png");
			searchParamtersChanged = true;
			$(document).find("#extended_search_submit")[0].click();
			$("#distances").hide();
			$("#distances_label").hide();
		} else {
			$("#search_by_location").attr("src","images/enabled_location.png");
			$("#distances").show();
			$("#distances_label").show();
			var source = document.getElementById("control-distances-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#distances").html(template({
				distances: config.distances 
			}));
			$(document).find("#extended_search")[0].click();
		}
		enableSearchFromPoint = !enableSearchFromPoint;
	});

	$(document).on("click", "#extended_search", function() {
		$("#extended-search-form").css("left", "calc(50% - 300px)");
		$("#extended-search-form").css("top", "calc(50% - 150px)");
		$("#extended-search-form").show();
		$("#extended-search-form-close-button").show();
		$("#extended-search-form-close-button").css("left", "calc(50% + 276px)");
		$("#extended-search-form-close-button").css("top", "calc(50% - 174px)");
		$(document).on("click","#extended-search-form-close-button", function() {
			$("#extended-search-form").hide();
			$("#extended-search-form-close-button").hide();
		});
	});

	$(document).on("click", "#help", function() {
		var source   = document.getElementById("help-info-template").innerHTML;
		var template = Handlebars.compile(source);
		output       = template({language: language});
		$("#help-info").html(output);
		$("#help-info").css("left", "calc(50% - 300px)");
		$("#help-info").css("top", "calc(50% - 150px)");
		$("#help-info").show();
		$("#help-close-button").show();
		$("#help-close-button").css("left", "calc(50% + 276px)");
		$("#help-close-button").css("top", "calc(50% - 174px)");

		$(document).on("click","#help-close-button", function() {
			$("#help-info").hide();
			$("#help-close-button").hide();
		});
	});

	$("#close_image_pane").on("click", function() {
		$("#image-pane img").attr("src", "");
		$("#image-pane").hide();
		$("#close_image_pane").hide();
		$("#magnify_image_pane").hide();
	});

	$("#close_contours_pane").on("click", function() {
		$("#contours-pane").hide();
		$("#close_contours_pane").hide();
		$("#magnify_contours_pane").hide();
		$(".legend").remove();
	});
});


function createRegionBorders(coords, decorations) {
	var keys = Object.keys(coords);
	clearPolygons();
	if (keys.length === 1) {
		var decoration = decorations[keys[0]];
		var bounds = new google.maps.LatLngBounds(
			new google.maps.LatLng(
				decoration.bounds.southWest.lat,
				decoration.bounds.southWest.lng),
			new google.maps.LatLng(
				decoration.bounds.northEast.lat, 
				decoration.bounds.northEast.lng)
		);
		map.setZoom(getBoundsZoomLevel(
			bounds,
			{
				height: $("#map").height(),
				width: $("#map").width()
			}
		));
		map.setCenter(getBoundsMapCenter(decoration.bounds));
	} else {
		map.setCenter(config.MAP_CENTER);
		map.setZoom(config.DEFAULT_ZOOM_LEVEL);
	}

	for (i=0; i < keys.length; i++) {
		var key = keys[i];
		var region_coords = coords[key];
		var decoration = decorations[key];
		(function(decoration, region_coords, map) {
			var polygon = new google.maps.Polygon({
				paths: region_coords,
				strokeColor: decoration.stroke_color,
				strokeOpacity: decoration.opacity_on_mouse_out,
				strokeWeight: 2,
				fillColor: decoration.fill_color,
				fillOpacity: decoration.opacity_on_mouse_out
			});
			polygon.setMap(map);
			polygons.push(polygon);
			google.maps.event.addListener(polygon, "click", function (e) {
				if (markerClicked) {
					markerClicked = false;
					if (e) {
						if (e.preventDefault) {
							return e.preventDefault();
						} else {
							return false;
						}
					} else {
						return false;
					}
					
				}
				var latLng = e.latLng;
				if (enableSearchFromPoint) {
					showSpinner();
					fillDdValues();
					geomap.getResourcesFromPoint(
						regionId, 
						areaId,
						resourceKind, 
						resourceGroup,
						resourceType, 
						"All",
						latLng.lat(), 
						latLng.lng(), 
						$("#distances").val(),
						$("#statuses").val(),
						$("#remainder").val(),
						function(resources) {
						if (!resources.authenticated) {
							verificationFailed = true;
							$(document).find("#login").attr("src","images/login.png");
							//$(document).find("#login").attr("src","images/login.png");
						}
						doFillResources(resources.data);
						hideSpinner();
					}, function() {
						hideSpinner();
						showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
					});
				}
			});
			google.maps.event.addListener(polygon, "mouseover",
				function(event){
					$("html, body").css("cursor", "pointer");
					this.setOptions({
						fillOpacity: decoration.opacity_on_mouse_over
					});
				}
			);
			google.maps.event.addListener(polygon, "mouseout",
				function(event){
					$("html, body").css("cursor", "");
					this.setOptions({
						fillOpacity: decoration.opacity_on_mouse_out
					});
				}
			);
		})(decoration, region_coords, map);
	}
}

function clearContourPolygons() {
	for (var i = 0; i < contourPolygons.length; i++ ) {
		contourPolygons[i].setMap(null);
	}	
	contourPolygons.length = 0;
}

function clearLicenseContourPolygons() {
	for (var i = 0; i < licensePolygons.length; i++ ) {
		for (var j = 0; j < licensePolygons[i].length; j++) {
			licensePolygons[i][j].setMap(null);
		}
	}	
	licensePolygons.length = 0;	
}

function clearPolygons() {
	for (var i = 0; i < polygons.length; i++ ) {
		polygons[i].setMap(null);
	}	
	polygons.length = 0;
}

function clearOverlays() {
	for (var i = 0; i < markers.length; i++) {
		markers[i].setMap(null);
	}	
	markers.length = 0;
}

function selectedItemStateChanged(resource) {
	if (!resourceViewEnabled) {
		var source   = document.getElementById("resource-info-template").innerHTML;
		var template = Handlebars.compile(source);
		showSpinner();
		geomap.getResource(resource.ID, function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			if (Object.keys(result["data"]).length == 0) {
				hideForms();
				if (enableSearchFromPoint) {				
					$("#distances").show();
					$("#distances_label").show();
				}
				searchParamtersChanged = true;
				verificationFailed = true;
				$(document).find("#extended_search_submit")[0].click();
				return;
			}

			resource_info = result.data;
			geomap.getLicenses(resource.ID, function(result) {
				if (!result.authenticated) {
					verificationFailed = true;
					$(document).find("#login").attr("src","images/login.png");
				}
				resource_info.licenses = result.data;
				resource_info.language = language;
				output       = template(resource_info);
				$("#resource-info").html(output);
				$("#resource-info").css("left", "calc(50% - 300px)");
				$("#resource-info").css("top", "calc(50% - 150px)");
				$("#resource-info").show();
				$(".resource-info-button").show();
				$(".resource-info-button").css("left", "calc(50% + 276px)");
				$(".resource-info-button").css("top", "calc(50% - 174px)");
				$(".resource-print-button").show();
				$(".resource-print-button").css("left", "calc(50% + 208px)");
				$(".resource-print-button").css("top", "calc(50% - 174px)");
				hideSpinner();
			}, function() {
				hideSpinner();
				showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
			});
		}, function() {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});
		
		$(document).off("click", ".resource-print-button");
		$(document).on("click", ".resource-print-button", function() {
			window.open("/api/print_report/?resource_id=" + resource.ID);
		});
		$(document).off("click", ".resource-info-button");
		$(document).on("click", ".resource-info-button", function() {
			selectedItemStateChanged(resource);
			$(".resource-info-button").hide();
			$(".resource-print-button").hide();
		});
		$(document).off("click", "#cut_image");
		$(document).on("click", "#cut_image", function() {
			showSpinner();
			geomap.getResource(resource.ID, function(result) {
				if (!result.authenticated) {
					$(document).find("#login").attr("src","images/login.png");
				}
				if (Object.keys(result["data"]).length == 0) {
					hideForms();
					if (enableSearchFromPoint) {				
						$("#distances").show();
						$("#distances_label").show();
					}
					searchParamtersChanged = true;
					$(document).find("#extended_search_submit")[0].click();
					return;
				}
				resource_info = result.data;
				geomap.getImage(resource_info.image_cut_uuid, function(result) {
					if (!result.authenticated) {
						$(document).find("#login").attr("src","images/login.png");
					}
					if (Object.keys(result["data"]).length == 0) {
						hideForms();
						if (enableSearchFromPoint) {				
							$("#distances").show();
							$("#distances_label").show();
						}
						searchParamtersChanged = true;
						$(document).find("#extended_search_submit")[0].click();
						return;
					}
					image = result.data;
					$("#image-pane img").attr("src", "data:image/jpg;base64," + image.data);
					$("#image-pane").show();
					$("#close_image_pane").show();
					$("#close_image_pane").css("left", "calc(50% + 276px)");
					$("#close_image_pane").css("top", "calc(50% - 174px)");
					$("#magnify_image_pane").css("left", "calc(50% + 208px)");
					$("#magnify_image_pane").css("top", "calc(50% - 174px)");
					$("#magnify_image_pane").show();
					(function(data) {
						$("#magnify_image_pane").off().on("click", function() {
							var img = new Image();
							img.src = "data:image/jpg;base64," + data;
							var w = window.open("");
							w.document.write(img.outerHTML);
						});	
					})(image.data);
					hideSpinner();
				}, function(error) {
					hideSpinner();
					showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
				});
			}, function() {
				hideSpinner();
				showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
			});
		});
		$(document).off("click", "#plan_image");
		$(document).on("click", "#plan_image", function() {
			showSpinner();
			geomap.getResource(resource.ID, function(result) {
				if (!result.authenticated) {
						$(document).find("#login").attr("src","images/login.png");
				}
				if (Object.keys(result["data"]).length == 0) {
					hideForms();
					if (enableSearchFromPoint) {				
						$("#distances").show();
						$("#distances_label").show();
					}
					searchParamtersChanged = true;
					$(document).find("#extended_search_submit")[0].click();
					return;
				}
				resource_info = result.data;
				geomap.getImage(resource_info.image_plan_uuid, function(result) {
					if (!result.authenticated) {
						$(document).find("#login").attr("src","images/login.png");
					}
					if (Object.keys(result["data"]).length == 0) {
						hideForms();
						if (enableSearchFromPoint) {				
							$("#distances").show();
							$("#distances_label").show();
						}
						searchParamtersChanged = true;
						$(document).find("#extended_search_submit")[0].click();
						return;
					}
					image = result.data;
					$("#image-pane img").attr("src", "data:image/jpg;base64," + image.data);
					$("#image-pane").show();
					$("#close_image_pane").show();
					$("#close_image_pane").css("left", "calc(50% + 276px)");
					$("#close_image_pane").css("top", "calc(50% - 174px)");
					$("#magnify_image_pane").css("left", "calc(50% + 208px)");
					$("#magnify_image_pane").css("top", "calc(50% - 174px)");
					$("#magnify_image_pane").show();
					(function(data) {
						$("#magnify_image_pane").off().on("click", function() {
							var img = new Image();
							img.src = "data:image/jpg;base64," + data;
							var w = window.open("");
							w.document.write(img.outerHTML);
						});	
					})(image.data);
					hideSpinner();
				}, function(error) {
					hideSpinner();
					showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
				});
			}, function() {
				hideSpinner();
				showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
			});
		});
		$(document).off("click", "#plan_contours");
		$(document).on("click", "#plan_contours", function() {							
			showSpinner();
			geomap.getDepositContours(resource.ID, function(result) {
				hideSpinner();
				if (!result.authenticated) {
					verificationFailed = true;
					$(document).find("#login").attr("src","images/login.png");
				}
				if (result.data.length != 0) {
					$("#contours-pane").show();
					$("#close_contours_pane").show();
					$("#close_contours_pane").css("left", "calc(50% + 276px)");
					$("#close_contours_pane").css("top", "calc(50% - 174px)");
					$("#magnify_contours_pane").css("left", "calc(50% + 208px)");
					$("#magnify_contours_pane").css("top", "calc(50% - 174px)");
					$("#magnify_contours_pane").show();
					initInlineMap();
					clearContourPolygons();
					clearLicenseContourPolygons();

					var points = result["data"];
					var mass_lat_center = 0.0;
					var mass_lng_center = 0.0;
					for (var i = 0; i < points.length; i++) {
						mass_lat_center += points[i]["lat"];
						mass_lng_center += points[i]["lng"];
					}
					mass_lat_center = mass_lat_center / points.length;
					mass_lng_center = mass_lng_center / points.length;
					var center = {
						"lat": mass_lat_center,
						"lng": mass_lng_center
					};
					var polygon = new google.maps.Polygon({
						paths: points,
						strokeColor: "#FF0000",
						strokeWeight: 3
					});
					inlineMap.setZoom(14);
					inlineMap.setCenter(center);									
					polygon.setMap(inlineMap);
					contourPolygons.push(polygon);

					geomap.getLicenseContours(resource.ID, function(result) {
						// Legend
						var legend = document.createElement("div");
						document.createElement("div");
						legend.className = "legend";

						var licenses = result["data"];
						for (var j = 0; j < Object.keys(licenses).length; j++) {
							var license = Object.keys(licenses)[j];
							var points = licenses[license]["points"];
							
							var center_lat = 0.0;
							var center_lng = 0.0;

							for (var k = 0; k < points.length; k++) {
								center_lat = center_lat + points[k]["lat"];
								center_lng = center_lng + points[k]["lng"];
							}

							center_lat = center_lat / points.length;
							center_lng = center_lng / points.length;

							var polygon = new google.maps.Polygon({
								paths: points,
								strokeColor: polygonColors[j],
								strokeWeight: 3
							});

							polygon.setMap(inlineMap);
							//var latLng = new google.maps.LatLng(center_lat, center_lng);
							//var label = new LabelMarker(latLng, inlineMap, license);

							var label = document.createElement("div");
							var newLine = document.createElement("br");
							label.appendChild(document.createTextNode(license));
							//var color = document.createElement("div");
							//color.className = "legend-info";
							//color.style.backgroundColor = polygonColors[j];
							label.style.backgroundColor = polygonColors[j];
							//legend.appendChild(color);
							legend.appendChild(label)
							//legend.appendChild(newLine);
						}
						
						
						$("#contours-pane").append(legend);
					});
				} else {
					hideForms();
					if (enableSearchFromPoint) {				
						$("#distances").show();
						$("#distances_label").show();
					}
					searchParamtersChanged = true;
					verificationFailed = true;
					$(document).find("#extended_search_submit")[0].click();
					return;
				}
			}, function(error) {
					hideSpinner();
					showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
			});
			$("#magnify_contours_pane").on("click", function() {
				$("#inlinemap div.gm-style button[title='Toggle fullscreen view']").trigger("click");
			});
		});
		currentlySelectedResource = resource;
		resourceViewEnabled = true;
		$("#" + resource.ID).css("background-color", "#666");
	} else {
		if (currentlySelectedResource != null && 
			currentlySelectedResource.ID == resource.ID) {
			resourceViewEnabled = false;
			currentlySelectedResource = null;
			$("#resource-info").hide();
			$("#" + resource.ID).css("background-color", "#FFF");
			$("#" + resource.ID).css("background-color", "#FFF");
		}
	}
}

function doFillResources(resources) {
	clearOverlays();
	if (resources.length === 0) {
		$("#resources").hide();
		google.maps.event.trigger(map, "resize");
	} else {
		if (!sidePanelFolded) {
			$("#resources").show();
		}
	}
	clusters = {};
	for (var i=0; i < resources.length; i++) {
		var resource = resources[i];
		if (!(clusters[resource.cluster])) {
			clusters[resource.cluster] = {
				count: 1,
				centroid: resource.centroid,
				resources: [resource]
			}
		} else {
			clusters[resource.cluster].count++;
			clusters[resource.cluster].resources.push(resource);
		}
	}

	var clusterKeys = Object.keys(clusters);
	for (var i = 0; i < clusterKeys.length; i++) {
		var key = clusterKeys[i];
		var cluster = clusters[key];
		var latLng = new google.maps.LatLng(cluster.centroid.lat, cluster.centroid.lng)
		var marker = new CustomMarker(latLng, map, cluster.count);
		(function(cluster) {
			marker.addListener("click", function(event) {
				markerClicked = true;
				if (cluster.resources.length > 1) {
					var source = document.getElementById("clustered-resources-template").innerHTML;
					var template = Handlebars.compile(source);
					$("#clustered-resources-info").html(template({
						resources: cluster.resources,
						language: language
					}));
					$("#clustered-resources-info").css("left", "calc(50% - 300px)");
					$("#clustered-resources-info").css("top", "calc(50% - 150px)");
					$("#clustered-resources-info").show();
					$("#clustered-resources-close-button").show();
					$("#clustered-resources-close-button").css("left", "calc(50% + 276px)");
					$("#clustered-resources-close-button").css("top", "calc(50% - 174px)");
					$(document).on("click", "#clustered-resources-close-button", function() {
						$("#clustered-resources-info").hide();
						$("#clustered-resources-close-button").hide();
					});

					for (var i = 0; i < cluster.resources.length; i++) {
						//console.log(document.getElementById("clustered-" + cluster.resources[i].ID));
						(function(resource) {
							$(document).off("click", "#clustered-" + resource.ID);
							$(document).on("click",  "#clustered-" + resource.ID, function() {
								selectedItemStateChanged(resource);
							});
						})(cluster.resources[i]);
					}
				} else {
					selectedItemStateChanged(cluster.resources[0]);
				}
				if (event) {
					event.preventDefault();
				}
				
			});
			marker.addListener("mouseover", function() {
				
			});

			marker.addListener("mouseout", function() {
				
			});
		})(cluster);
		markers.push(marker);
	}

	var source = document.getElementById("resource-template").innerHTML;
	var template = Handlebars.compile(source);

	$("#resources").html(template({
		resources: resources,
		language: language
	}));

	if (resources.length === 0) {
		$("#resource-info").hide();
	}

	for (i=0; i < resources.length; i++) {
		var resource = resources[i];
		(function(resource) {
			if (currentlySelectedResource != null) {
				map.setCenter(config.MAP_CENTER);
				resourceViewEnabled = false;
				$("#resource-info").hide();
				$("#" + currentlySelectedResource.ID)
					.css("background-color", "#FFF");
				currentlySelectedResource = null;
			}
			$("#" + resource.ID).click(function() {
				selectedItemStateChanged(resource);
			});
		})(resource);
	}
} 

$(document).on("keypress", "#resource_name", function() {
	searchParamtersChanged = true;
});

$(document).on("change", "#resource_name", function() {
	searchParamtersChanged = true;
});

$(document).on("change", "#statuses", function() {
	searchParamtersChanged = true;
});

$(document).on("change", "#remainder", function() {
	searchParamtersChanged = true;
});

$(document).on("change", "#regions", function() {
	regionId = this.value;
	showHideControls();
	showSpinner();
	geomap.getListOfAreas(regionId, function(result) {
		if (!result.authenticated) {
			verificationFailed = true;
			$(document).find("#login").attr("src","images/login.png");
		}
		var areas = result.data;
		var source   = document.getElementById("control-areas-template").innerHTML;;
		var template = Handlebars.compile(source);
		$("#areas").html(template(
			{
				areas: areas,
				language: language
			}
		));
		hideSpinner();
	}, function(error) {
		hideSpinner();
		showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
	});
	searchParamtersChanged = true;
});

$(document).on("change", "#areas", function() {
	searchParamtersChanged = true;
});

$(document).on("change", "#resource_kinds", function() {
	searchParamtersChanged = true;
	fillDdValues();
	showHideControls();
	showSpinner();
	var itemsToLoad = 2;
	geomap.getListOfResourceGroups(resourceKind,  
		function(result) {
		if (!result.authenticated) {
			verificationFailed = true;
			$(document).find("#login").attr("src","images/login.png");
		}
		var resourceGroups = result.data;
		console.log(resourceGroups);
		var source   = document.getElementById("control-resource-groups-template").innerHTML;
		var template = Handlebars.compile(source);
		$("#resource_groups").html(template(
			{
				resource_groups: resourceGroups,
				language: language
			}
		));
		if (--itemsToLoad == 0) {
			hideSpinner();
		}
	}, function() {
		hideSpinner();
		showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
	});

	geomap.getListOfResourceTypes(resourceKind, resourceGroup, 
		function(result) {
		if (!result.authenticated) {
			verificationFailed = true;
			$(document).find("#login").attr("src","images/login.png");
		}
		var resourceTypes = result.data;
		var source   = document.getElementById("control-resource-types-template").innerHTML;
		var template = Handlebars.compile(source);
		$("#resource_types").html(template(
			{
				resource_types: resourceTypes,
				language: language
			}
		));
		if (--itemsToLoad == 0) {
			hideSpinner();
		}
	}, function() {
		hideSpinner();
		showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
	});
});

$(document).on("change", "#resource_groups", function() {

	searchParamtersChanged = true;
	fillDdValues();
	showSpinner();
	showHideControls();
	var itemsToLoad = 1;
	geomap.getListOfResourceTypes(resourceKind, resourceGroup, 
		function(result) {
		if (!result.authenticated) {
			verificationFailed = true;
			$(document).find("#login").attr("src","images/login.png");
		}
		var resourceTypes = result.data;
		var source   = document.getElementById("control-resource-types-template").innerHTML;
		var template = Handlebars.compile(source);
		$("#resource_types").html(template(
			{
				resource_types: resourceTypes,
				language: language
			}
		));
		if (--itemsToLoad == 0) {
			hideSpinner();
		}
	}, function() {
		hideSpinner();
		showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
	});
});

$(document).on("change", "#resource_types", function() {
	fillDdValues();
	searchParamtersChanged = true;
});

$(document).on("click", "#extended_search_submit", function(event) {
	if (event) {
		event.preventDefault();
	}
	var itemsToLoad = 2;
	$("#extended-search-form").hide();
	$("#extended-search-form-close-button").hide();
	if (searchParamtersChanged) {
		searchParamtersChanged = false;
		console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
		showSpinner();
		fillDdValues();
		geomap.getResources(
			regionId, 
			areaId, 
			language, 
			resourceKind, 
			resourceGroup,
			resourceType, 
			$("#resource_name").val(), 
			//(regionId == -1 || regionId == "") ? numClusters : "All",
			//(regionId == -1 || regionId == "") ? "All" : "All",
			"All",
			$("#statuses").val(),
			$("#remainder").val(),
			function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var resources = result.data;
			doFillResources(resources);
			if (--itemsToLoad == 0) {
				hideSpinner();
			}
		}, function() {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		geomap.getRegionDecorations(regionId, function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var decorations = result.data;
			geomap.getRegionBorders(regionId, function(result) {
				if (!result.authenticated) {
					verificationFailed = true;
					$(document).find("#login").attr("src","images/login.png");
				}
				var coords = result.data;
				createRegionBorders(coords, decorations);
				if (--itemsToLoad == 0) {
					hideSpinner();
				}
			}, function(error) {
				hideSpinner();
				showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
			});
		}, function(error) {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});
	}
});
