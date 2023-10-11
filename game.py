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

class DeleteCategoryAction(Action):
	def __init__(self, game: "Game", category: Category):
		self.game: "Game" = game
		self.category: Category = category
	def execute(self):
		self.game.categories.remove(self.category)
	def getName(self):
		return f"Delete category \"{self.category.name}\" from game"

class RenameItemAction(Action):
	def __init__(self, category: Category, item: Item, newName: str):
		self.category: Category = category
		self.item: Item = item
		self.newName: str = newName
	def execute(self):
		self.item.name = self.newName
	def getName(self):
		return f"Rename item \"{self.item.name}\" in category \"{self.category.name}\" to \"{self.newName}\""

class RenameCategoryAction(Action):
	def __init__(self, category: Category, newName: str):
		self.category: Category = category
		self.newName: str = newName
	def execute(self):
		self.category.name = self.newName
	def getName(self):
		return f"Rename category \"{self.category.name}\" to \"{self.newName}\""

class MoveItemAction(Action):
	def __init__(self, category: Category, item: Item, amount: int):
		self.category: Category = category
		self.item: Item = item
		self.amount: int = amount
	def execute(self):
		new_index = self.category.items.index(self.item) + self.amount
		self.category.items.remove(self.item)
		self.category.items.insert(new_index, self.item)
	def getName(self):
		return f"Move item \"{self.item.name}\" in category \"{self.category.name}\" {abs(self.amount)} spaces {'up' if self.amount < 0 else 'down'}"

class MoveCategoryAction(Action):
	def __init__(self, game: "Game", category: Category, amount: int):
		self.game: "Game" = game
		self.category: Category = category
		self.amount: int = amount
	def execute(self):
		new_index = self.game.categories.index(self.category) + self.amount
		self.game.categories.remove(self.category)
		self.game.categories.insert(new_index, self.category)
	def getName(self):
		return f"Move category \"{self.category.name}\" {abs(self.amount)} spaces {'up' if self.amount < 0 else 'down'}"

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
		elif data["type"] == "delete_category":
			self.voteQueue.append(DeleteCategoryAction(self, self.categories[data["categoryno"]]))
		elif data["type"] == "edit_item":
			category = self.categories[data["categoryno"]]
			self.voteQueue.append(RenameItemAction(category, category.items[data["itemno"]], data["text"]))
		elif data["type"] == "edit_category":
			category = self.categories[data["categoryno"]]
			self.voteQueue.append(RenameCategoryAction(category, data["text"]))
		elif data["type"] == "move_item":
			category = self.categories[data["categoryno"]]
			self.voteQueue.append(MoveItemAction(category, category.items[data["itemno"]], data["amount"]))
		elif data["type"] == "move_category":
			self.voteQueue.append(MoveCategoryAction(self, self.categories[data["categoryno"]], data["amount"]))
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

# def load_game(data: str):
# 	import json
# 	decoded = json.loads(data)
# 	game = Game()
# 	for category in decoded["categories"]:
# 		game.categories.append(Category(category["name"]))
# 		for item in category["items"]:
# 			game.categories[-1].items.append(Item(item["name"], item["text"]))
# 	return game