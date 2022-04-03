function getUrlVars() {
	var vars = {};
    /*var parts = window.location.href.replace(/[?&]+([a-z0-9]+)=([0-9\w%]*)/gi, function(m,key,value) {
        vars[key] = value;
    });*/
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    //return vars;
    return urlParams;
}

function showMessageWindow(message) {
	$("#message-window").html(message);
	$("#message-window").css("left", "calc(50% - 300px)");
	$("#message-window").css("top", "calc(50% - 150px)");
	$("#message-window").fadeIn("slow").show();

	$("#message-window-close-button").fadeIn("slow").show();
	$("#message-window-close-button").css("left", "calc(50% + 276px)");
	$("#message-window-close-button").css("top", "calc(50% - 174px)");
}

function hideMessageWindow() {
	$("#message-window").fadeOut("slow");
	$("#message-window-close-button").fadeOut("slow");				
}

hideMessageWindow();

function hideForms() {
	$("#resource-info").fadeOut("slow");
	$("#image-pane").fadeOut("slow");
	$("#contours-pane").fadeOut("slow");
	$("#close_contours_pane").fadeOut("slow");
	$("#help-info").fadeOut("slow");
	$("#login-info").fadeOut("slow");
	$(".login-message").fadeOut("slow");
	$("#clustered-resources-info").fadeOut("slow");
	$("#help-close-button").fadeOut("slow");
	$("#login-window-close-button").fadeOut("slow");
	$("#clustered-resources-close-button").fadeOut("slow");
	$(".resource-info-button").fadeOut("slow");
	$(".resource-print-button").fadeOut("slow");
	$(".investment-info-button").fadeOut("slow");
	$("#investments-search-form-close-button").fadeOut();
	$("#close_image_pane").fadeOut("slow");
	$("#magnify_image_pane").fadeOut("slow");
	$("#magnify_contours_pane").fadeOut("slow");
	$("#resources").fadeOut("slow");
	$("#distances_label").fadeOut("slow");
	$("#distances").fadeOut("slow");
	$("#extended-search-form").fadeOut("slow");
	$("#extended-search-form-close-button").fadeOut("slow");
	$("#registration-form").fadeOut("slow");
	$("#registration-form-close-button").fadeOut("slow");
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
	$("#spinner").fadeIn("slow").show();
}

function hideSpinner() {
	$("#spinner").fadeOut("slow");
}

function showHideControls() {
	if (regionId == -1 || regionId == "") {
		$("#areas").fadeOut("slow");
		$("#areas_label").fadeOut("slow");
	} else {
		$("#areas").fadeIn("slow").show();
		$("#areas_label").fadeIn("slow").show();
	}
	if (investmentsRegionId == -1 || investmentsRegionId == "") {
		$("#investments_areas").fadeOut("slow");
		$("#investments_areas_label").fadeOut("slow");
	} else {
		$("#investments_areas").fadeIn("slow");
		$("#investments_areas_label").fadeIn("slow");	
	}
	if (resourceKind == -1 || resourceKind == "") {
		$("#resource_groups").fadeOut("slow");
		$("#resource_groups_label").fadeOut("slow");
		$("#resource_types").fadeOut("slow");
		$("#resource_types_label").fadeOut("slow");
	} else {
		$("#resource_groups").fadeIn("slow").show();
		$("#resource_groups_label").fadeIn("slow").show();
	}
	if (resourceGroup == -1 || resourceGroup == "") {
		$("#resource_types").fadeOut("slow");
		$("#resource_types_label").fadeOut("slow");
	} else {
		$("#resource_types").fadeIn("slow").show();
		$("#resource_types_label").fadeIn("slow").show();
	}
}

function fillDdValues() {
	regionId = $("#regions").val();
	areaId = $("#areas").val();
	investmentsRegionId = $("#investments_regions").val();
	investmentsAreaId = $("#investments_areas").val();
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
	$("#registration-form-close-button").fadeOut("slow");
	$("#registration-form").fadeOut("slow");
});


$(document).on("click", "#request_registration", function(event) {
	event.preventDefault();
	$("#registration-form").css("left", "calc(50% - 300px)");
	$("#registration-form").css("top", "calc(50% - 150px)");
	$("#registration-form").fadeIn("slow").show();
	$("#registration-form-close-button").fadeIn("slow").show();
	$("#registration-form-close-button").css("left", "calc(50% + 276px)");
	$("#registration-form-close-button").css("top", "calc(50% - 174px)");
});


$(document).ready(function() {
	
	language = getUrlVars().get("language") || "ru";

	regionId = getUrlVars().get("region_id") || "";
	
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

		var source = document.getElementById("investment-info-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$(".investment-info-button").html(template(
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

		var source = document.getElementById("investments-search-close-button-template").innerHTML;
		var template = Handlebars.compile(source);

		$("#investments-search-form-close-button").html(template(
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

		var source   = document.getElementById("investments-search-template").innerHTML;
		var template = Handlebars.compile(source);
		$("#investments-search-form").html(template(
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
			//showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});

		hideForms();

		geomap.getListOfRegions(function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var regions = result.data;
			var regions_filtered = [];
			for (var i = 0; i < regions.length; i++) {
				if (regions[i]["id"] == regionId) {
					regions_filtered.push(regions[i]);
					break;
				}
			}

			for (var i = 0; i < regions.length; i++) {
				if (regions[i]["id"] != regionId) {
					regions_filtered.push(regions[i]);
				}
			}
			
			var source   = document.getElementById("control-regions-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#regions").html(template(
				{
					regions: regions_filtered,
					language: language
				}
			));
		}, function () {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});


		geomap.getListOfRegions(function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var regions = result.data;
			var regions_filtered = [];
			for (var i = 0; i < regions.length; i++) {
				if (regions[i]["id"] == regionId) {
					regions_filtered.push(regions[i]);
					break;
				}
			}

			for (var i = 0; i < regions.length; i++) {
				if (regions[i]["id"] != regionId) {
					regions_filtered.push(regions[i]);
				}
			}
			
			var source   = document.getElementById("control-regions-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#investments_regions").html(template(
				{
					regions: regions_filtered,
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

		geomap.getListOfMinerals(function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var minerals = result.data;
			var source   = document.getElementById("control-minerals-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#investments_minerals").html(template(
				{
					minerals: minerals,
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

		geomap.getListOfAreas(regionId, function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			var areas = result.data;
			var source   = document.getElementById("control-areas-template").innerHTML;
			var template = Handlebars.compile(source);
			$("#investments_areas").html(template(
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
		console.log(regionId);
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
			numClusters,
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
						$("#distances").fadeIn("slow").show();
						$("#distances_label").fadeIn("slow").show();
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
						$("#distances").fadeIn("slow").show();
						$("#distances_label").fadeIn("slow").show();
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
			//showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
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

	$(document).on("click", "#info_graphics", function(event) {
		event.preventDefault();
		showSpinner();
		geomap.getInfographic(regionId, resourceKind, resourceGroup, resourceType, function(result) {
			hideForms();
			hideSpinner();
			if (!result.authenticated) {
				$(document).find("#login").attr("src","images/login.png");
			}
			image = result.data;
			$("#image-pane img").attr("src", "data:image/jpg;base64," + image);
			$("#image-pane").fadeIn("slow").show();
			$("#close_image_pane").fadeIn("slow").show();
			$("#close_image_pane").css("left", "calc(50% + 276px)");
			$("#close_image_pane").css("top", "calc(50% - 174px)");
			$("#magnify_image_pane").css("left", "calc(50% + 208px)");
			$("#magnify_image_pane").css("top", "calc(50% - 174px)");
			$("#magnify_image_pane").fadeIn("slow").show();
			(function(data) {
				$("#magnify_image_pane").off().on("click", function() {
					var img = new Image();
					img.src = "data:image/jpg;base64," + data;
					var w = window.open("");
					w.document.write(img.outerHTML);
				});
			})(image);
		}, function(error) {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});
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
				$("#login-info").fadeIn("slow").show();
				$("#login-window-close-button").fadeIn("slow").show();
				$("#login-window-close-button").css("left", "calc(50% + 276px)");
				$("#login-window-close-button").css("top", "calc(50% - 174px)");
				$(document).on("click","#login-window-close-button", function() {
					$("#login-info").fadeOut("slow");
					$("#login-window-close-button").fadeOut("slow");
				});
				$(document).on("click", "#login-button", function(event) {
					geomap.authenticate($("#username").val(), $("#password").val(), function(result) {
						if (result.status === "success") {
							//$("#login").attr("src","images/logout.png");
							$(document).find("#login").attr("src","images/logout.png");
							searchParamtersChanged = true;
							$(".login-message").fadeIn("slow").show();
							$(".login-message").html("<p>Вход выполнен успешно</p>");
							$(".login-message").fadeOut(1000);
							$(document).find("#extended_search_submit")[0].click();
							verificationFailed = false;
							setTimeout(function() {
								$(".login-message").fadeOut("slow");
								$("#login-info").fadeOut("slow");
								$("#login-window-close-button").fadeOut("slow");
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
			//showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		});
	});
	$(document).on("click", "#settings", function() {
		window.open("admin.html");
	});
	$(document).on("click", "#fold", function() {
		if (sidePanelFolded && !inInvestmentsSearchModule) {
			$("#resources").fadeIn("slow").show();
		} else {
			$("#resources").fadeOut("slow");
		}
		sidePanelFolded = !sidePanelFolded;
		google.maps.event.trigger(map, "resize");
	});

	$(document).on("click", "#search_by_location", function() {
		inInvestmentsSearchModule = false;
		if (enableSearchFromPoint) {
			$("#search_by_location").attr("src","images/disabled_location.png");
			searchParamtersChanged = true;
			$(document).find("#extended_search_submit")[0].click();
			$("#distances").fadeOut("slow");
			$("#distances_label").fadeOut("slow");
		} else {
			$("#search_by_location").attr("src","images/enabled_location.png");
			$("#distances").fadeIn("slow").show();
			$("#distances_label").fadeIn("slow").show();
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
		$("#extended-search-form").fadeIn("slow").show();
		$("#extended-search-form-close-button").fadeIn("slow").show();
		$("#extended-search-form-close-button").css("left", "calc(50% + 276px)");
		$("#extended-search-form-close-button").css("top", "calc(50% - 174px)");
		$(document).on("click","#extended-search-form-close-button", function() {
			$("#extended-search-form").fadeOut("slow");
			$("#extended-search-form-close-button").fadeOut("slow");
		});
	});

	$(document).on("click", "#investments_search", function() {

		$("#investments-search-form").css("left", "calc(50% - 300px)");
		$("#investments-search-form").css("top", "calc(50% - 150px)");
		$("#investments-search-form").fadeIn("slow").show();
		$("#investments-search-form-close-button").fadeIn("slow").show();
		$("#investments-search-form-close-button").css("left", "calc(50% + 276px)");
		$("#investments-search-form-close-button").css("top", "calc(50% - 174px)");
		$(document).on("click","#investments-search-form-close-button", function() {
			$("#investments-search-form").fadeOut("slow");
			$("#investments-search-form-close-button").fadeOut("slow");
		});
	});

	$(document).on("click", "#help", function() {
		var source   = document.getElementById("help-info-template").innerHTML;
		var template = Handlebars.compile(source);
		output       = template({language: language});
		$("#help-info").html(output);
		$("#help-info").css("left", "calc(50% - 300px)");
		$("#help-info").css("top", "calc(50% - 150px)");
		$("#help-info").fadeIn("slow").show();
		$("#help-close-button").fadeIn("slow").show();
		$("#help-close-button").css("left", "calc(50% + 276px)");
		$("#help-close-button").css("top", "calc(50% - 174px)");

		$(document).on("click","#help-close-button", function() {
			$("#help-info").fadeOut("slow");
			$("#help-close-button").fadeOut("slow");
		});
	});

	$("#close_image_pane").on("click", function() {
		$("#image-pane img").attr("src", "");
		$("#image-pane").fadeOut("slow");
		$("#close_image_pane").fadeOut("slow");
		$("#magnify_image_pane").fadeOut("slow");
	});

	$("#close_contours_pane").on("click", function() {
		$("#contours-pane").fadeOut("slow");
		$("#close_contours_pane").fadeOut("slow");
		$("#magnify_contours_pane").fadeOut("slow");
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
				strokeWeight: 4,
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
					$("#distances").fadeIn("slow").show();
					$("#distances_label").fadeIn("slow").show();
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
				$("#resource-info").fadeIn("slow").show();
				$(".resource-info-button").fadeIn("slow").show();
				$(".resource-info-button").css("left", "calc(50% + 276px)");
				$(".resource-info-button").css("top", "calc(50% - 174px)");
				$(".resource-print-button").fadeIn("slow").show();
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
			$(".resource-info-button").fadeOut("slow");
			$(".resource-print-button").fadeOut("slow");
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
						$("#distances").fadeIn("slow").show();
						$("#distances_label").fadeIn("slow").show();
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
							$("#distances").fadeIn("slow").show();
							$("#distances_label").fadeIn("slow").show();
						}
						searchParamtersChanged = true;
						$(document).find("#extended_search_submit")[0].click();
						return;
					}
					image = result.data;
					$("#image-pane img").attr("src", "data:image/jpg;base64," + image.data);
					$("#image-pane").fadeIn("slow").show();
					$("#close_image_pane").fadeIn("slow").show();
					$("#close_image_pane").css("left", "calc(50% + 276px)");
					$("#close_image_pane").css("top", "calc(50% - 174px)");
					$("#magnify_image_pane").css("left", "calc(50% + 208px)");
					$("#magnify_image_pane").css("top", "calc(50% - 174px)");
					$("#magnify_image_pane").fadeIn("slow").show();
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
						$("#distances").fadeIn("slow").show();
						$("#distances_label").fadeIn("slow").show();
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
							$("#distances").fadeIn("slow").show();
							$("#distances_label").fadeIn("slow").show();
						}
						searchParamtersChanged = true;
						$(document).find("#extended_search_submit")[0].click();
						return;
					}
					image = result.data;
					$("#image-pane img").attr("src", "data:image/jpg;base64," + image.data);
					$("#image-pane").fadeIn("slow").show();
					$("#close_image_pane").fadeIn("slow").show();
					$("#close_image_pane").css("left", "calc(50% + 276px)");
					$("#close_image_pane").css("top", "calc(50% - 174px)");
					$("#magnify_image_pane").css("left", "calc(50% + 208px)");
					$("#magnify_image_pane").css("top", "calc(50% - 174px)");
					$("#magnify_image_pane").fadeIn("slow").show();
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
			geomap.getSiteContours(resource.ID, function(result) {
				hideSpinner();
				if (!result.authenticated) {
					verificationFailed = true;
					$(document).find("#login").attr("src","images/login.png");
				}
				if (result.data.length != 0) {
					$("#contours-pane").fadeIn("slow").fadeIn("slow").show();
					$("#close_contours_pane").fadeIn("slow").show();
					$("#close_contours_pane").css("left", "calc(50% + 276px)");
					$("#close_contours_pane").css("top", "calc(50% - 174px)");
					$("#magnify_contours_pane").css("left", "calc(50% + 208px)");
					$("#magnify_contours_pane").css("top", "calc(50% - 174px)");
					$("#magnify_contours_pane").fadeIn("slow").show();
					initInlineMap();
					clearContourPolygons();
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
					var polygon = new google.maps.Polyline({
						path: points,
						strokeColor: "#FF0000",
						strokeWeight: 4
					});
					inlineMap.setZoom(14);
					inlineMap.setCenter(center);
					polygon.setMap(inlineMap);
					contourPolygons.push(polygon);
				} else {
					hideForms();
					if (enableSearchFromPoint) {				
						$("#distances").fadeIn("slow").show();
						$("#distances_label").fadeIn("slow").show();
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
			$("#resource-info").fadeOut("slow");
			$("#" + resource.ID).css("background-color", "#FFF");
			$("#" + resource.ID).css("background-color", "#FFF");
		}
	}
}

function doFillInvestments(investments) {
	clearOverlays();
	for (var i = 0; i < investments.length; i++) {
		var latLng = new google.maps.LatLng(investments[i].lat, investments[i].lng)
		var marker = new CustomMarker(latLng, map, 1);
		(function(investment_id, marker) {
			marker.addListener("click", function(event) {
				markerClicked = true;
				//selectedItemStateChanged(cluster.resources[0]);
				showSpinner();
				geomap.getInvestment(investment_id, function(result) {
					hideSpinner();
					var investment_info = result.data;
					investment_info.language = language;

					var source   = document.getElementById("investmnent-info-template").innerHTML;
					var template = Handlebars.compile(source);
					
					var output   = template(investment_info);
					$("#investment-info").html(output);
					$("#investment-info").css("left", "calc(50% - 300px)");
					$("#investment-info").css("top", "calc(50% - 150px)");
					$("#investment-info").fadeIn("slow").show();

					$(".investment-info-button").fadeIn("slow").show();
					$(".investment-info-button").css("left", "calc(50% + 276px)");
					$(".investment-info-button").css("top", "calc(50% - 174px)");

					$(document).off("click", ".investment-info-button");
					$(document).on("click", ".investment-info-button", function() {
						$("#investment-info").fadeOut("slow");
						$(".investment-info-button").fadeOut("slow").hide();
					});
				}, function() {
					hideSpinner();
					showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
				})
				if (event) {
					event.preventDefault();
				}
				
			});
			marker.addListener("mouseover", function() {
				
			});

			marker.addListener("mouseout", function() {
				
			});
		})(investments[i].id, marker);
		markers.push(marker);
	}
}

function doFillResources(resources) {
	clearOverlays();
	if (resources.length === 0) {
		$("#resources").fadeOut("slow");
		google.maps.event.trigger(map, "resize");
	} else {
		if (!sidePanelFolded) {
			$("#resources").fadeIn("slow").show();
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
					$("#clustered-resources-info").fadeIn("slow").show();
					$("#clustered-resources-close-button").fadeIn("slow").show();
					$("#clustered-resources-close-button").css("left", "calc(50% + 276px)");
					$("#clustered-resources-close-button").css("top", "calc(50% - 174px)");
					$(document).on("click", "#clustered-resources-close-button", function() {
						$("#clustered-resources-info").fadeOut("slow");
						$("#clustered-resources-close-button").fadeOut("slow");
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
	console.log(resources);
	$("#resources").html(template({
		resources: resources,
		language: language
	}));

	if (resources.length === 0) {
		$("#resource-info").fadeOut("slow");
	}

	for (i=0; i < resources.length; i++) {
		var resource = resources[i];
		(function(resource) {
			if (currentlySelectedResource != null) {
				map.setCenter(config.MAP_CENTER);
				resourceViewEnabled = false;
				$("#resource-info").fadeOut("slow");
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

$(document).on("change", "#investments_regions", function() {
	investmentsRegionId = this.value;
	showHideControls();
	showSpinner();
	geomap.getListOfAreas(investmentsRegionId, function(result) {
		if (!result.authenticated) {
			verificationFailed = true;
			$(document).find("#login").attr("src","images/login.png");
		}
		var areas = result.data;
		var source   = document.getElementById("control-areas-template").innerHTML;;
		var template = Handlebars.compile(source);
		$("#investments_areas").html(template(
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

$(document).on("change", "#investments_areas", function() {
	investmentsSearchParamtersChanged = true;
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
	inInvestmentsSearchModule = false;
	if (event) {
		event.preventDefault();
	}
	var itemsToLoad = 2;
	$("#extended-search-form").fadeOut("slow");
	$("#extended-search-form-close-button").fadeOut("slow");
	//if (searchParamtersChanged) {
		searchParamtersChanged = false;
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
			(regionId == -1 || regionId == "") ? numClusters : "All",
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
	//}
});


$(document).on("click", "#investment_search_submit", function(event) {
	inInvestmentsSearchModule = true;
	if (event) {
		event.preventDefault();
	}
	$("#investments-search-form").fadeOut("slow");
	$("#investments-search-form-close-button").fadeOut("slow");
	var itemsToLoad = 2;
	showSpinner();
	fillDdValues();

	geomap.getInvestments(
		$("#object_name").val(), 
		investmentsRegionId,
		investmentsAreaId,
		$("#investments_minerals").val(),
		function(result) {
			if (!result.authenticated) {
				verificationFailed = true;
				$(document).find("#login").attr("src","images/login.png");
			}
			if (--itemsToLoad == 0) {
				hideSpinner();
			}
			doFillInvestments(result.data);
		},
		function() {
			hideSpinner();
			showMessageWindow("Возникла ошибка. Попробуйте перезагрузить страницу");
		}
	);

	

	geomap.getRegionDecorations(investmentsRegionId, function(result) {
		if (!result.authenticated) {
			verificationFailed = true;
			$(document).find("#login").attr("src","images/login.png");
		}
		var decorations = result.data;
		geomap.getRegionBorders(investmentsRegionId, function(result) {
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
});
