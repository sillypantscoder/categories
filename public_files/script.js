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
			if (e.target.status != 200) location.replace("/")
			else resolve(e.target.responseText)
		})
		x.addEventListener("error", () => {
			location.replace("/")
		})
		x.send()
	})
}

/**
 * Send an HTTP POST request with some data.
 * @param {string} url The URL to send data to.
 * @param {string} body The data to send.
 * @returns {Promise<void>} A promise that resolves when the data has been sent.
 */
function post(url, body) {
	return new Promise((resolve) => {
		var x = new XMLHttpRequest()
		x.open("POST", url)
		x.addEventListener("loadend", (e) => {
			resolve()
		})
		x.send(body)
	})
}

/**
 * Add buttons to the parent element.
 * @param {{ text: string, onclick: string }[]} buttons The buttons to add.
 * @param {HTMLElement} parent The parent element.
 */
function addButtons(buttons, parent) {
	var menu = document.createElement("dialog-menu")
	menu.buttons = buttons
	parent.appendChild(menu)
}

var previousCategories = false
function refreshCategories() {
	var data = request("/data/categories")
	data.then((v) => {
		/** @type {{items: string[], name: string}[]} */
		var r = JSON.parse(v)
		return r;
	}).then((v) => {
		if ((function sameAs(o1, o2) {
			if (typeof o1 !== typeof o2) return false
			if (["number", "string", "boolean", "undefined"].includes(typeof o1)) return o1 === o2
			// They are both objects!
			var keys1 = Object.keys(o1)
			var keys2 = Object.keys(o2)
			if (keys1.length !== keys2.length) return false
			for (var i = 0; i < keys1.length; i++) {
				if (keys1[i] !== keys2[i]) return false
				if (!sameAs(o1[keys1[i]], o2[keys2[i]])) return false
			}
			return true
		})(previousCategories, v)) {
			return;
		}
		previousCategories = v;
		[...document.querySelectorAll("#categories > * + *")].forEach((e) => e.remove())
		for (var vi = 0; vi < v.length; vi++) {
			// insert category
			var big = document.createElement("div")
			big.innerHTML = `<button class="button new-big-btn" onclick="createNewCategory(${vi})">+ Insert category</button>`
			document.querySelector("#categories").appendChild(big)
			// init
			var category = v[vi]
			var category_elm = document.createElement("div")
			category_elm.classList.add("category")
			document.querySelector("#categories").appendChild(category_elm)
			// add header
			var header = document.createElement("h5")
			category_elm.appendChild(header)
			addButtons([
				{ text: "Insert category above", onclick: ((vi, item) => (() => createNewCategory(vi)))(vi) },
				{ text: "Insert category below", onclick: ((vi, item) => (() => createNewCategory(vi + 1)))(vi) },
				{ text: "Delete category", onclick: ((vi, item) => (() => deleteCategory(vi)))(vi) },
				{ text: "Move category", onclick: ((vi, item) => (() => moveCategory(vi)))(vi) },
				{ text: "Rename category", onclick: ((vi, item) => (() => editCategory(vi)))(vi) }
			], header)
			header.appendChild(document.createElement("span"))
			header.children[header.children.length - 1].innerText = category.name
			// add items
			for (var item = 0; item < category.items.length; item++) {
				// item
				var item_elm = document.createElement("div")
				item_elm.classList.add("item")
				category_elm.appendChild(item_elm)
				// buttons
				addButtons([
					{ text: "New item above", onclick: ((vi, item) => (() => createNewItem(vi, item)))(vi, item) },
					{ text: "New item below", onclick: ((vi, item) => (() => createNewItem(vi, item + 1)))(vi, item) },
					{ text: "Delete item", onclick: ((vi, item) => (() => deleteItem(vi, item)))(vi, item) },
					{ text: "Move item", onclick: ((vi, item) => (() => moveItem(vi, item)))(vi, item) },
					{ text: "Edit item", onclick: ((vi, item) => (() => editItem(vi, item)))(vi, item) }
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
		// insert category
		var big = document.createElement("div")
		big.innerHTML = `<button class="button new-big-btn" onclick="createNewCategory(${vi})">+ Insert category</button>`
		document.querySelector("#categories").appendChild(big)
	}).then((zzz) => {
		setTimeout(() => {
			refreshCategories()
		}, 1000)
	})
}

function refreshVote() {
	var data = request("/data/vote")
	data.then((v) => {
		/** @type {{players: string[], vote: { action: string, votes: boolean[], ready: boolean[], finished: boolean }}} */
		var r = JSON.parse(v)
		return r;
	}).then((v) => {
		[...document.querySelectorAll("#currentvote > * + *")].forEach((e) => e.remove())
		var e = document.createElement("div")
		document.querySelector("#currentvote").appendChild(e)
		// 1. Add vote
		if (v.vote) {
			// a. Add the header.
			e.appendChild(document.createElement("h4"))
			e.children[0].innerText = v.vote.action
			// b. Find out if we have already voted.
			var playername = query.name
			var index = v.players.indexOf(playername)
			var hasFinished = v.vote.ready[index]
			// c. Add buttons, if needed.
			function votebtn(value) {
				return (e) => {
					post("/data/vote", JSON.stringify({
						name: query.name,
						value
					}))
				}
			}
			if (v.vote.finished) {
				if (hasFinished) {
					e.appendChild(document.createElement("h4"))
					e.children[1].innerText = "Please wait for everyone else to finish!"
				} else {
					var votes = [0, 0]
					for (var vote of v.vote.votes) votes[vote * 1] += 1
					// Add vote buttons
					e.appendChild(document.createElement("div"))
					e.children[1].classList.add("vote-button-container")
					e.children[1].innerHTML = `<div class="vote-button vote-button-no">${votes[0]}</div><div class="vote-button vote-button-yes">${votes[1]}</div>`
					// Add finish button
					e.appendChild(document.createElement("div"))
					e.children[2].classList.add("vote-button-container")
					e.children[2].innerHTML = `<div class="vote-button vote-button-finish">Finish</div>`
					e.children[2].children[0].addEventListener("click", votebtn(true))
				}
			} else {
				if (hasFinished) {
					e.appendChild(document.createElement("h4"))
					e.children[1].innerText = "Please wait for everyone else to vote!"
				} else {
					// Add vote buttons
					e.appendChild(document.createElement("div"))
					e.children[1].classList.add("vote-button-container")
					e.children[1].innerHTML = `<div class="vote-button vote-button-no">No</div><div class="vote-button vote-button-yes">Yes</div>`
					e.children[1].children[0].addEventListener("click", votebtn(false))
					e.children[1].children[1].addEventListener("click", votebtn(true))
				}
			}
		} else {
			e.appendChild(document.createElement("h4"))
			e.children[0].innerText = "There is no voting currently in progress."
		}
		// 2. Add player indicators
		var playerlist = document.createElement("div")
		e.appendChild(playerlist)
		for (var i = 0; i < v.players.length; i++) {
			var p = document.createElement("div")
			p.classList.add("player")
			if (v.vote) {
				if (v.vote.ready[i]) p.classList.add("player-ready")
				if (v.vote.finished) p.classList.add("player-vote-" + v.vote.votes[i])
			}
			p.innerText = v.players[i]
			playerlist.appendChild(p)
		}
	}).then(() => {
		setTimeout(() => {
			refreshVote()
		}, 1000)
	})
}

refreshCategories()
refreshVote()

function createNewItem(categoryno, itemno) {
	[...document.querySelectorAll("#createvote > * + *")].forEach((e) => e.remove())
	var info = document.createElement("div")
	document.querySelector("#createvote").appendChild(info)
	// info
	info.innerHTML = `<div>Create new item:</div><div><input type="text" placeholder="Enter item text here"></div><div><button>Submit</button><button onclick="this.parentNode.parentNode.remove()">Cancel</button></div>`
	info.children[2].children[0].addEventListener("click", (event) => {
		post("/data/create_vote", JSON.stringify({
			type: "create_item",
			categoryno,
			itemno,
			text: info.querySelector("input").value
		})).then(() => {
			event.target.parentNode.parentNode.remove()
		})
	})
}
function deleteItem(categoryno, itemno) {
	[...document.querySelectorAll("#createvote > * + *")].forEach((e) => e.remove())
	var info = document.createElement("div")
	document.querySelector("#createvote").appendChild(info)
	// info
	info.innerHTML = `<div>Delete item:</div><div>Category: <b>${previousCategories[categoryno].name}</b><br>Item: <b>${previousCategories[categoryno].items[itemno]}</b></div><div><button>Submit</button><button onclick="this.parentNode.parentNode.remove()">Cancel</button></div>`
	info.children[2].children[0].addEventListener("click", (event) => {
		post("/data/create_vote", JSON.stringify({
			type: "delete_item",
			categoryno,
			itemno
		})).then(() => {
			event.target.parentNode.parentNode.remove()
		})
	})
}
function createNewCategory(categoryno) {
	[...document.querySelectorAll("#createvote > * + *")].forEach((e) => e.remove())
	var info = document.createElement("div")
	document.querySelector("#createvote").appendChild(info)
	// info
	info.innerHTML = `<div>Create new category:</div><div>Name: <input type="text" placeholder="Category title here..."></div><div><button>Submit</button><button onclick="this.parentNode.parentNode.remove()">Cancel</button></div>`
	info.children[2].children[0].addEventListener("click", (event) => {
		post("/data/create_vote", JSON.stringify({
			type: "create_category",
			categoryno,
			text: info.querySelector("input").value
		})).then(() => {
			event.target.parentNode.parentNode.remove()
		})
	})
}
function deleteCategory(categoryno) {
	[...document.querySelectorAll("#createvote > * + *")].forEach((e) => e.remove())
	var info = document.createElement("div")
	document.querySelector("#createvote").appendChild(info)
	// info
	info.innerHTML = `<div>Delete category:</div><div>Category: <b>${previousCategories[categoryno].name}</b></div><div><button>Submit</button><button onclick="this.parentNode.parentNode.remove()">Cancel</button></div>`
	info.children[2].children[0].addEventListener("click", (event) => {
		post("/data/create_vote", JSON.stringify({
			type: "delete_category",
			categoryno
		})).then(() => {
			event.target.parentNode.parentNode.remove()
		})
	})
}
function editItem(categoryno, itemno) {
	[...document.querySelectorAll("#createvote > * + *")].forEach((e) => e.remove())
	var info = document.createElement("div")
	document.querySelector("#createvote").appendChild(info)
	// info
	info.innerHTML = `<div>Edit item:</div><div><input type="text" placeholder="Enter item text here" value="${previousCategories[categoryno].items[itemno]}"></div><div><button>Submit</button><button onclick="this.parentNode.parentNode.remove()">Cancel</button></div>`
	info.children[2].children[0].addEventListener("click", (event) => {
		post("/data/create_vote", JSON.stringify({
			type: "edit_item",
			categoryno,
			itemno,
			text: info.querySelector("input").value
		})).then(() => {
			event.target.parentNode.parentNode.remove()
		})
	})
}
function editCategory(categoryno) {
	[...document.querySelectorAll("#createvote > * + *")].forEach((e) => e.remove())
	var info = document.createElement("div")
	document.querySelector("#createvote").appendChild(info)
	// info
	info.innerHTML = `<div>Rename category:</div><div>Name: <input type="text" placeholder="Category title here..." value="${previousCategories[categoryno].name}"></div><div><button>Submit</button><button onclick="this.parentNode.parentNode.remove()">Cancel</button></div>`
	info.children[2].children[0].addEventListener("click", (event) => {
		post("/data/create_vote", JSON.stringify({
			type: "edit_category",
			categoryno,
			text: info.querySelector("input").value
		})).then(() => {
			event.target.parentNode.parentNode.remove()
		})
	})
}
function moveItem(categoryno, itemno) {
	[...document.querySelectorAll("#createvote > * + *")].forEach((e) => e.remove())
	var info = document.createElement("div")
	document.querySelector("#createvote").appendChild(info)
	// info
	info.innerHTML = `<div>Move item:</div><div>Shift by: <input type="number" value="0"></div><div><button>Submit</button><button onclick="this.parentNode.parentNode.remove()">Cancel</button></div>`
	info.children[2].children[0].addEventListener("click", (event) => {
		post("/data/create_vote", JSON.stringify({
			type: "move_item",
			categoryno,
			itemno,
			amount: info.querySelector("input").valueAsNumber
		})).then(() => {
			event.target.parentNode.parentNode.remove()
		})
	})
}
function moveCategory(categoryno) {
	[...document.querySelectorAll("#createvote > * + *")].forEach((e) => e.remove())
	var info = document.createElement("div")
	document.querySelector("#createvote").appendChild(info)
	// info
	info.innerHTML = `<div>Move category:</div><div>Shift by: <input type="number" value="0"></div><div><button>Submit</button><button onclick="this.parentNode.parentNode.remove()">Cancel</button></div>`
	info.children[2].children[0].addEventListener("click", (event) => {
		post("/data/create_vote", JSON.stringify({
			type: "move_category",
			categoryno,
			amount: info.querySelector("input").valueAsNumber
		})).then(() => {
			event.target.parentNode.parentNode.remove()
		})
	})
}