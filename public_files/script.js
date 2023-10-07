/**
 * Send an HTTP request and return the response.
 * @param {string} url The URL to get data from.
 * @returns {Promise<string>} A promise that resolves with the request respose.
 */
function request(url) {
	return new Promise((resolve) => {
		var x = new XMLHttpRequest()
		x.open("GET", url)
		x.addEventListener("loadend", (e) => {
			resolve(e.target.responseText)
		})
		x.send()
	})
}

function refreshCategories() {
	var data = request("/data/categories")
	data.then((v) => {
	})
}