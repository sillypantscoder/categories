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

/**
 * Add buttons to the parent element.
 * @param {{ class: string, onclick: string }[]} buttons The buttons to add.
 * @param {HTMLElement} parent The parent element.
 */
function addButtons(buttons, parent) {
	for (var info of buttons) {
		var button = document.createElement("button")
		button.classList.add("button")
		button.classList.add("btn-" + info.class)
		button.setAttribute("onclick", info.onclick)
		parent.appendChild(button)
	}
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
			var category_elm = document.createElement("div")
			category_elm.classList.add("category")
			document.querySelector("#categories").appendChild(category_elm)
			// add header
			var header = document.createElement("h5")
			header.innerText = category.name
			category_elm.appendChild(header)
			// add header buttons
			addButtons([
				{ class: "delete", onclick: `` }
			], header)
			// add items
			for (var item = 0; item < category.items.length; item++) {
				// item
				var item_elm = document.createElement("div")
				item_elm.classList.add("item")
				category_elm.appendChild(item_elm)
				// buttons
				addButtons([
					{ class: "new", onclick: `createNewItem(${vi}, ${item})` },
					{ class: "delete", onclick: `createNewItem(${vi}, ${item})` },
					{ class: "move", onclick: `createNewItem(${vi}, ${item})` }
				], item_elm)
				// text
				var text_elm = document.createElement("span")
				text_elm.innerText = category.items[item]
				item_elm.appendChild(text_elm)
			}
			var big = document.createElement("div")
			big.innerHTML = `<button class="button new-big-btn" onclick="createNewItem(${vi}, ${item})">+ New item</button>`
			category_elm.appendChild(big)
		}
	})
}

refreshCategories()

function createNewItem(categoryno, itemno) {}