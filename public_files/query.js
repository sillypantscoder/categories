(() => {
	var php_var_ret = {}
	var url = decodeURIComponent(location.href.replaceAll("+", " "))
	var things = url.split("?").slice(1).join("?").split("#")[0].split("&")
	if (Boolean(things[0])) {
		for (var a = 0; a < things.length; a++) {
			var name =  things[a].split("=")[0]
			var value = things[a].split("=")[1]
			php_var_ret[name] = value
		}
	} else {
		php_var_ret = {}
	}
	window.query = php_var_ret
})();