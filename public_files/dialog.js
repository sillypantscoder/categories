document.head.appendChild(document.createElement("style")).innerHTML = `
dialog-menu .dialog-menu-expand-button {
	display: inline-block;
	width: 1em;
	height: 1em;
	background: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMiAxMiI+Cgk8cmVjdCB4PSIxIiB5PSIxIiB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHJ4PSIyIiBmaWxsPSIjMDUwMDFjIiAvPgoJPHBhdGggZD0iTSAyIDYgQSAxIDEgMCAwIDAgNCA2IEEgMSAxIDAgMCAwIDIgNiBaIE0gNSA2IEEgMSAxIDAgMCAwIDcgNiBBIDEgMSAwIDAgMCA1IDYgWiBNIDggNiBBIDEgMSAwIDAgMCAxMCA2IEEgMSAxIDAgMCAwIDggNiBaIiBmaWxsPSJ3aGl0ZSIgLz4KPC9zdmc+);
}
dialog-menu .dialog-menu-expanded-menu {
	position: absolute;
	top: 100%;
	left: 0;
	border: 1px solid black;
	z-index: 1000000;
	width: max-content;
}
dialog-menu .dialog-menu-option {
	padding: 0.5em 1em;
	background: white;
	color: black;
	font-weight: normal;
}
dialog-menu .dialog-menu-option:hover {
	background: #AAA;
}
`
class DialogMenu extends HTMLElement {
	constructor() {
		super();
		/** @type {{ text: string, onclick: string }[]} */
		this.buttons = []
		var _this = this;
		this.list = (e) => {
			if (this.children[1].contains(e.target)) return;
			_this.closeMenu()
		}
	}
	connectedCallback() {
		this.setAttribute("style", "position: relative;")
		this.appendChild(document.createElement("div"))
		this.children[0].classList.add("dialog-menu-expand-button")
		var _this = this;
		this.children[0].addEventListener("click", () => _this.openMenu())
	}
	openMenu() {
		this.appendChild(document.createElement("div"))
		this.children[1].classList.add("dialog-menu-expanded-menu")
		// Add menu options
		var _this = this;
		for (var i = 0; i < this.buttons.length; i++) {
			var button = document.createElement("div")
			button.classList.add("dialog-menu-option")
			button.innerText = this.buttons[i].text
			button.addEventListener("click", ((i) => (() => {
				_this.buttons[i].onclick()
				_this.closeMenu()
			}))(i))
			this.children[1].appendChild(button)
		}
		// Add listeners
		window.addEventListener("mousedown", this.list, true)
		window.addEventListener("touchstart", this.list, true)
	}
	closeMenu() {
		this.children[1].remove()
		// Remove listeners
		window.removeEventListener("mousedown", this.list, true)
		window.removeEventListener("touchstart", this.list, true)
	}
}
customElements.define("dialog-menu", DialogMenu);