var geomap = (function() {
	"use strict";

	var ApiBaseURL = "https://map.uzgeolcom.uz/api",
		//ApiBaseURL = "http://localhost/api",
		//ApiBaseURL = "http://217.29.112.158/api",
		api,
		log = function(msg) {
			try {
				if (window) {
					window.console.log(msg);
				} else {
					console.log(msg);
				}
			} catch (err) {
				throw err;
			}
		},

		jsonGet = function(url, data, success, error, always, method) {
			var params = '';
			for (var key in data) {
				var val = encodeURIComponent(data[key]);
				params += ((params ||
				url.indexOf("?") != -1) ? '&' : '?') + key + '=' + val;
			}
			if (((typeof navigator) != "undefined") 
				&& navigator.userAgent 
				&& navigator.userAgent.indexOf("MSIE") != -1 
				&& window.XDomainRequest) {
				var xdr = new XDomainRequest();
				xdr.open("GET", url + params);
				xdr.timeout = 20000;
				xdr.onprogress = function() {}
				xdr.onload = function() {
					if (success) {
						var data = {};
						var status = 200;
						try {
							var jsonObj = JSON.parse(xdr.responseText);
							data = jsonObj || {};
						} catch (err) {
							log(err);
						} finally {
							if (success) success(data, status);
							if (always) always();
						}
					}
				}
				xdr.onerror = function() {
					try {
					} catch (err) {
						log(err);
					} finally {
						if (error) error(0);
						if (always) always();
					}
				}
				xdr.ontimeout = function() {
					if (error) error(500);
					if (always) always();
				}
				xdr.send();
			} else {
				try {
					var xhr = new XMLHttpRequest();
					xhr.open("GET", url + params, true);
					xhr.setRequestHeader("Content-type", "application/json");
					xhr.onreadystatechange = function() {
						if (xhr.readyState == 4) {
							if (xhr.status == 200 || xhr.status == 201) {
								if (success) {
									var jsonObj = JSON.parse(xhr.responseText);
									success(jsonObj, xhr.status);
								}
							} else {
								log(xhr.responseText);
								if (error) error(xhr.status);
							}
							if (always) always();
						}
					}
					xhr.send();
				} catch (e) {
					throw e;
				}
			}
		},

		jsonPost = function(url, data, success, error, always, method) {
			if (((typeof navigator) != "undefined") && navigator.userAgent 
				&& navigator.userAgent.indexOf("MSIE") != -1 
				&& window.XDomainRequest) {
				var xdr = new XDomainRequest();
				xdr.open(method, url);
				
				xdr.onload = function() {
					if (success) {
						var data = {};
						var status = 200;
						try {
							var jsonObj = JSON.parse(xdr.responseText);
							data = jsonObj || {};
						} catch (e) {
							throw e;
						} finally {
							if (success) success(data, status);
							if (always) always();
						}
					}
				}
				xdr.timeout = 20000;
				xdr.onprogress = function() {}
				xdr.onerror = function() {
					var status = 0;
					try {
						
					} catch (err) {
						throw err;
					} finally {
						if (error) error(status);
						if (always) always();
					}
				}

				xdr.ontimeout = function() {
					if (error) error(500);
					if (always) always();
				}

				xdr.send(data);
			} else {
				try {
					var xhr = new XMLHttpRequest();
					xhr.open(method, url, true);
					xhr.setRequestHeader("Content-type", "application/json");
					xhr.onreadystatechange = function() {
						if (xhr.readyState == 4) {
							if (xhr.status == 200 || xhr.status == 201) {
								if (success) {
									var jsonObj = JSON.parse(xhr.responseText);
									success(jsonObj, xhr.status);
								}
							} else {
								if (error) {
									error(xhr.status);
								}
							}
							if (always) always();
						}
					}
					xhr.send(data);
				} catch (e) {
					throw e;
				}
			}
		},

		httprequest = function(options) {
			options.type = options.type || "GET";
			var settings = options;
			if (!settings.url) {
				throw "API URL is not set";
			}

			if (settings.type === "DELETE" || settings.type === "POST") {
				if (!settings.data || typeof settings.data !== 'object') {
					return;
				} else {
					settings.data = JSON.stringify(settings.data);
				}
				jsonPost(settings.url, settings.data,
					settings.success, settings.error,
					settings.final, settings.type);
			} else if (settings.type === "GET") {
				jsonGet(settings.url, settings.data,
					settings.success, settings.error,
					settings.final, settings.type);
			}
		};
		
	api = {

		/*
		Simple HTTP request method with custom options.
		Options can contain the following fields:
		data, url, type, success, error, always
		*/
		httprequest: function (options) {
			httprequest(options);
		},

		/*
		Gets the list of regions
		*/
		getListOfRegions: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/regions/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Gets the list of areas
		*/
		getListOfAreas: function(region_id, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/areas/",
				data : {
					region_id: region_id
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Gets the list of minerals
		*/
		getListOfMinerals: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/minerals/",
				data : {
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Gets list of resource groups
		*/
		getListOfResourceGroups: function(kind_id, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/resource_groups/",
				data : {
					kind_id: kind_id
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Gets list of resource kinds
		*/
		getListOfResourceKinds: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/resource_kinds/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Gets list of resource types
		*/
		getListOfResourceTypes: function(kind_id, group_id, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/resource_types/",
				data : {
					kind_id  : kind_id,
					group_id : group_id,
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getInvestments: function(
			object_name,
			region_id, 
			area_id, 
			mineral_id,
			success, 
			error, 
			always) {
				httprequest({
				url: ApiBaseURL + "/investments/",
				data: {
					region_id      : region_id,
					area_id        : area_id,
					object_name    : object_name,
					mineral_id     : mineral_id,
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getInvestment: function(
			investment_id,
			success, 
			error, 
			always) {
				httprequest({
				url: ApiBaseURL + "/investment/",
				data: {
					investment_id      : investment_id
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Gets resources which match specified region and type of the resource
		If these parameters are empty all resources will be returned.
		*/
		getResources: function(
			region_id, 
			area_id, 
			language, 
			resource_kind, 
			resource_group, 
			resource_type, 
			resource_name, 
			num_clusters,
			status_id,
			remainder_id,
			success, 
			error, 
			always) {
				httprequest({
				url: ApiBaseURL + "/resources/",
				data: {
					region_id      : region_id,
					area_id        : area_id,
					resource_kind  : resource_kind,
					resource_group : resource_group,
					resource_type  : resource_type,
					resource_name  : resource_name,
					language       : language,
					num_clusters   : num_clusters,
					status_id      : status_id,
					remainder_id   : remainder_id
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getResourcesFromPoint: function(
			region_id, 
			area_id, 
			resource_kind, 
			resource_group, 
			resource_type, 
			num_clusters, 
			latitude, longitude, distance, status_id,
			remainder_id, 
			success, error, always) {
				httprequest({
				url: ApiBaseURL + "/resources_from_point/",
				data: {
					region_id      : region_id,
					area_id        : area_id,
					resource_kind  : resource_kind,
					resource_group : resource_group,
					resource_type  : resource_type,
					resource_name  : resource_name,
					language       : language,
					num_clusters   : num_clusters,
					latitude       : latitude,
					longitude      : longitude,
					distance       : distance,
					status_id      : status_id,
					remainder_id   : remainder_id
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Gets resource by ID
		*/
		getResource: function(resource_id, success, error, always) {
				httprequest({
				url: ApiBaseURL + "/resource/",
				data: {
					resource_id : resource_id
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Gets resource by ID
		*/
		getLicenses: function(resource_id, success, error, always) {
				httprequest({
				url: ApiBaseURL + "/licenses/",
				data: {
					resource_id : resource_id
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/* Retrieves image based on specified UUID */
		getImage: function(uuid, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/get_image/",
				data: {
					uuid      : uuid
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*Get infographic*/
		getInfographic: function(region_id, resource_kind, resource_group, resource_type, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/info_graphics/",
				data: {
					region_id      : region_id,
					resource_kind  : resource_kind,
					resource_group : resource_group,
					resource_type  : resource_type
				},
				final: always,
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});			
		},

		/*
		Gets the borders for the given region(s)
		*/
		getRegionBorders: function(region_id, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/region_borders/",
				final: always,
				data: {
					region_id: region_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},
		
		/*
		Gets decorations (styles) for the regions
		*/
		getRegionDecorations: function(region_id, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/region_decorations/",
				final: always,
				data: {
					region_id: region_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*
		Authenticates the user using username and password
		*/
		authenticate: function(username, password, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/authenticate/",
				final: always,
				type: "POST",
				data: {
					username: username,
					password: password
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/*Checks the token for validity */
		checkToken: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/check_token/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/* Returns scatter data for resource access time */
		getHistogram: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/histogram/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/* Returns aggregated statistics for resource access time */
		getStats: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/stats/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/* Gets list of available roles in the system */
		getRoles: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/get_roles/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});	
		},

		/* Gets list of available users in the system */
		getUsers: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/get_users/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});	
		},

		getUser: function(user_id, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/get_user/",
				final: always,
				data: {
					user_id: user_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});	
		},

		/* Deletes the user from the system */
		deleteUser: function(user_id, success, error, always) {
			httprequest({
				url: ApiBaseURL + "/delete_user/",
				final: always,
				type: "DELETE",
				data: {
					user_id: user_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});	
		},

		/* Adds new user into the system */
		addUser: function(
			username, password, 
			first_name, last_name, 
			phone_number, email_address, 
			role_id,  
			success, error, always) {
			httprequest({
				url: ApiBaseURL + "/add_user/",
				final: always,
				type: "POST",
				data: {
					username: username,
					password: password,
					first_name: first_name,
					last_name: last_name,
					phone_number: phone_number,
					email_address: email_address,
					role_id: role_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/* Updates the user information */
		updateUser: function(
			user_id, first_name, last_name, 
			phone_number, email_address, 
			role_id, enabled, 
			success, error, always) {
			httprequest({
				url: ApiBaseURL + "/update_user/",
				final: always,
				type: "POST",
				data: {
					user_id: user_id,
					first_name: first_name,
					last_name: last_name,
					phone_number: phone_number,
					email_address: email_address,
					role_id: role_id,
					enabled: enabled
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/* Changes the password for existing user */
		changePassword: function(
			user_id, new_password, 
			success, error, always) {
			httprequest({
				url: ApiBaseURL + "/change_password/",
				final: always,
				type: "POST",
				data: {
					user_id: user_id,
					new_password: new_password
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		/* Gets all deposit statuses from the database */
		getDepositStatuses: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/get_deposit_statuses/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getRegions: function(
			success,
			error,	
			always) {
			httprequest({
				url: ApiBaseURL + "/get_regions/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getAreas: function(
			region_id,
			success,
			error,
			always) {
			httprequest({
				url: ApiBaseURL + "/get_areas/",
				final: always,
				data: {
					region_id: region_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getDepositKinds: function(
			success,
			error,
			always) {
			httprequest({
				url: ApiBaseURL + "/get_deposit_kinds/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		logout: function(success, error, always) {
			httprequest({
				url: ApiBaseURL + "/logout/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		requestRegistration: function(
			first_name, last_name, 
			phone_number, email_address, 
			description,  
			success, error, always) {
			httprequest({
				url: ApiBaseURL + "/request_registration/",
				final: always,
				type: "POST",
				data: {
					first_name: first_name,
					last_name: last_name,
					phone_number: phone_number,
					email_address: email_address,
					description: description
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getPendingRegistrations: function(
			success, 
			error, 
			always) {
			httprequest({
				url: ApiBaseURL + "/get_pending_registrations/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		deletePendingRegistration: function(
			pending_registration_id, 
			success, 
			error, 
			always) {
			httprequest({
				url: ApiBaseURL + "/delete_pending_registration/",
				final: always,
				data: {
					pending_registration_id: pending_registration_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getDepositContours: function(
			deposit_site_id, 
			success,
			error,  
			always) {
			httprequest({
				url: ApiBaseURL + "/get_deposit_contours/",
				final: always,
				data: {
					deposit_site_id: deposit_site_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getSiteContours: function(
			deposit_site_id, 
			success, 
			error,
			always) {
			httprequest({
				url: ApiBaseURL + "/get_deposit_site_contour/",
				final: always,
				data: {
					deposit_site_id: deposit_site_id
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		},

		getRole: function(
			success, 
			error,
			always) {
			httprequest({
				url: ApiBaseURL + "/get_role/",
				final: always,
				data: {
				},
				success: function (jsonObj, status) {
					if (success) success(jsonObj);
				},
				error: function(status) {
					if (error) error(status);
				}
			});
		}
	}
	return api;
})();
