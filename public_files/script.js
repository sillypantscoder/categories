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
		/** @type {{items: string[], name: string}[]} */
		var r = JSON.parse(v)
		return r;
	}).then((v) => {
		for (var vi = 0; vi < v.length; vi++) {
			var category = v[vi]
			var e = document.createElement("div")
			e.classList.add("category")
			document.querySelector("#categories").appendChild(e)
			// add header
			var h = document.createElement("h5")
			h.innerText = category.name
			e.appendChild(h)
			// add header buttons
			for (var info of [
				{ class: "remove" }
			]) {
				var b = document.createElement("button")
				b.classList.add("button")
				b.classList.add("btn-" + info.class)
				h.appendChild(b)
			}
			// add spacer
			var s = document.createElement("div")
				s.classList.add("spacer")
				e.appendChild(s)
			// add items
			for (var i = 0; i < category.items.length; i++) {
				var s = document.createElement("button")
				s.classList.add("new-btn")
				s.setAttribute("onclick", `createNewItem(${vi}, ${i})`)
				e.appendChild(s)
				var s = document.createElement("button")
				s.classList.add("delete-btn")
				e.appendChild(s)
				var s = document.createElement("button")
				s.classList.add("move-btn")
				e.appendChild(s)
				// item
				var i = document.createElement("div")
				i.classList.add("item")
				i.innerText = category.items[i]
				e.appendChild(i)
			}
			var s = document.createElement("button")
			s.classList.add("new-btn")
			e.appendChild(s)
		}
	})
}

refreshCategories()

function createNewItem(categoryno, itemno) {}