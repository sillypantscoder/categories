class Category:
	def __init__(self, name: str):
		self.name: str = name
		self.items: list[Item] = []
	def __repr__(self):
		return f"Category:" + "".join(["\n\t- " + x.name for x in self.items])

class Item:
	def __init__(self, name: str):
		self.name: str = name
	def __repr__(self):
		return f"Item {{ {repr(self.name)} }}"

class Action:
	def __init__(self):
		pass
	def execute(self):
		pass
	def getName(self):
		return "Invalid Action"

class AddItemAction(Action):
	def __init__(self, category: Category, index: int, item: Item):
		self.category: Category = category
		self.index: int = index
		self.item: Item = item
	def execute(self):
		self.category.items.insert(self.index, self.item)
	def getName(self):
		return f"Add item \"{self.item.name}\" to category \"{self.category.name}\""

class DeleteItemAction(Action):
	def __init__(self, category: Category, item: Item):
		self.category: Category = category
		self.item: Item = item
	def execute(self):
		self.category.items.remove(self.item)
	def getName(self):
		return f"Delete item \"{self.item.name}\" from category \"{self.category.name}\""

class AddCategoryAction(Action):
	def __init__(self, game: "Game", category: Category, index: int):
		self.game: "Game" = game
		self.category: Category = category
		self.index: int = index
	def execute(self):
		self.game.categories.insert(self.index, self.category)
	def getName(self):
		return f"Add category \"{self.category.name}\" to game"

class ActiveVote:
	def __init__(self, game: "Game"):
		self.target = game
		self.action: Action = game.voteQueue.pop(0)
		game.currentVote = self
		self.votes: list[bool] = [False for a in game.players]
		self.ready: list[bool] = [False for a in game.players]
		self.finished = False
	def vote(self, playername: str, vote: bool):
		index = self.target.players.index(playername)
		if not self.finished: self.votes[index] = vote
		self.ready[index] = True
		if False not in self.ready:
			# Next stage!
			if not self.finished:
				self.finished = True
				self.ready = [False for a in self.ready]
				votes_for = 0
				votes_against = 0
				for vote in self.votes:
					print(vote)
					if vote:
						votes_for += 1
					else:
						votes_against += 1
				if votes_for > votes_against:
					self.action.execute()
			else:
				self.target.currentVote = None
				self.target.update_active_vote()
	def toJSON(self):
		return {
			"action": self.action.getName(),
			"votes": self.votes,
			"ready": self.ready,
			"finished": self.finished
		}

class Game:
	def __init__(self):
		self.players: list[str] = []
		self.categories: list[Category] = []
		self.currentVote: None | ActiveVote = None
		self.voteQueue: list[Action] = []
		self.voteQueue: list[Action] = []
		self.categories.append(Category("hi"))
		for i in range(10): self.categories[0].items.append(Item(f"ASDFASDF{i}"))
	def get_categories(self) -> list[dict[str, str | list[str]]]:
		return [
			{"name": c.name, "items": [x.name for x in c.items]}
			for c in self.categories
		]
	def get_vote(self):
		return {
			"players": self.players,
			"vote": self.currentVote.toJSON() if self.currentVote else False
		}
	def create_vote(self, data: dict):
		if data["type"] == "create_item":
			self.voteQueue.append(AddItemAction(self.categories[data["categoryno"]], data["itemno"], Item(data["text"])))
		elif data["type"] == "delete_item":
			category = self.categories[data["categoryno"]]
			self.voteQueue.append(DeleteItemAction(category, category.items[data["itemno"]]))
		elif data["type"] == "create_category":
			self.voteQueue.append(AddCategoryAction(self, Category(data["text"]), data["categoryno"]))
		else:
			print("Unknown type!!!")
			print(repr(data))
		self.update_active_vote()
	def vote(self, data: dict):
		if self.currentVote != None:
			self.currentVote.vote(data["name"], data["value"])
	def update_active_vote(self):
		if self.currentVote == None:
			if len(self.voteQueue) > 0:
				ActiveVote(self)