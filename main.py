from http.server import BaseHTTPRequestHandler, HTTPServer
import typing
import os
import game as g
import json

hostName = "0.0.0.0"
serverPort = 8093

def read_file(filename):
	f = open(filename, "r")
	t = f.read()
	f.close()
	return t

def bin_read_file(filename):
	f = open(filename, "rb")
	t = f.read()
	f.close()
	return t

def write_file(filename, content):
	f = open(filename, "w")
	f.write(content)
	f.close()

# setup
game: g.Game = g.Game()
if os.path.isfile("save.json"):
	game = g.load_game(read_file("save.json"))
else:
	game.categories.append(g.Category("Example Category"))
	for i in range(9):
		game.categories[0].items.append(g.Item(f"Example Item {i + 1}"))

class HttpResponse(typing.TypedDict):
	status: int
	headers: dict[str, str]
	content: str | bytes

class URLQuery:
	def __init__(self, q: str):
		self.fields: dict[str, str] = {}
		for f in q.split("&"):
			s = f.split("=")
			if len(s) >= 2:
				self.fields[s[0]] = s[1]
	def get(self, key: str) -> str:
		if key in self.fields:
			return self.fields[key]
		else:
			return ''

def get(path: str, query: URLQuery) -> HttpResponse:
	write_file("save.json", g.save_game(game))
	if os.path.isfile("public_files" + path):
		return {
			"status": 200,
			"headers": {
				"Content-Type": {
					"html": "text/html",
					"js": "text/javascript",
					"css": "text/css"
				}[path.split(".")[-1]]
			},
			"content": bin_read_file("public_files" + path)
		}
	elif os.path.isdir("public_files" + path):
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": read_file("public_files" + path + "index.html")
		}
	elif path == "/playerlist":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": "\n".join(game.players)
		}
	elif path == "/data/categories":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/json"
			},
			"content": json.dumps(game.get_categories())
		}
	elif path == "/data/vote":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/json"
			},
			"content": json.dumps(game.get_vote())
		}
	else: # 404 page
		print("404 encountered! Path: " + path + " Query: " + repr(query.fields))
		return {
			"status": 404,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": f""
		}

def post(path: str, body: bytes) -> HttpResponse:
	if path == "/createuser":
		game.players.append(body.decode("UTF-8"))
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": ""
		}
		# bodydata = body.decode("UTF-8").split("\n")
	elif path == "/data/create_vote":
		game.create_vote(json.loads(body.decode("UTF-8")))
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": ""
		}
	elif path == "/data/vote":
		game.vote(json.loads(body.decode("UTF-8")))
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": ""
		}
	else:
		print("404 POST encountered! Path: " + path + " Body: " + repr(body))
		return {
			"status": 404,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": f""
		}

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		global running
		splitpath = self.path.split("?")
		res = get(splitpath[0], URLQuery('?'.join(splitpath[1:])))
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		c = res["content"]
		if isinstance(c, str): c = c.encode("utf-8")
		self.wfile.write(c)
	def do_POST(self):
		res = post(self.path, self.rfile.read(int(self.headers["Content-Length"])))
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		c = res["content"]
		if isinstance(c, str): c = c.encode("utf-8")
		self.wfile.write(c)
	def log_message(self, format: str, *args) -> None:
		return;
		if 400 <= int(args[1]) < 500:
			# Errored request!
			print(u"\u001b[31m", end="")
		print(args[0].split(" ")[0], "request to", args[0].split(" ")[1], "(status code:", args[1] + ")")
		print(u"\u001b[0m", end="")
		# don't output requests

if __name__ == "__main__":
	running = True
	webServer = HTTPServer((hostName, serverPort), MyServer)
	webServer.timeout = 1
	print("Server started http://%s:%s" % (hostName, serverPort))
	while running:
		try:
			webServer.handle_request()
		except KeyboardInterrupt:
			running = False
	webServer.server_close()
	print("Server stopped")
