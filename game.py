import random

def generate_id():
	id = random.randint(0, 1000000)
	return id

class Category:
	def __init__(self, name: str):
		self.name: str = name
		self.items: list[Item] = []
		self.id = generate_id()
	def __repr__(self):
		return f"Category:" + "".join(["\n\t- " + x.name for x in self.items])
	def save(self):
		return {
			"name": self.name,
			"items": [x.save() for x in self.items],
			"id": self.id
		}

class Item:
	def __init__(self, name: str):
		self.name: str = name
		self.id = generate_id()
	def __repr__(self):
		return f"Item {{ {repr(self.name)} }}"
	def save(self):
		return {
			"name": self.name,
			"id": self.id
		}

class Action:
	def __init__(self):
		pass
	def execute(self):
		pass
	def getName(self):
		return "Invalid Action"
	def save(self):
		return {
			"type": "invalid"
		}

class AddItemAction(Action):
	def __init__(self, category: Category, index: int, item: Item):
		self.category: Category = category
		self.index: int = index
		self.item: Item = item
	def execute(self):
		self.category.items.insert(self.index, self.item)
	def getName(self):
		return f"Add item \"{self.item.name}\" to category \"{self.category.name}\""
	def save(self):
		return {
			"type": "add_item",
			"category": self.category.save(),
			"index": self.index,
			"item": self.item.save()
		}

class DeleteItemAction(Action):
	def __init__(self, category: Category, item: Item):
		self.category: Category = category
		self.item: Item = item
	def execute(self):
		self.category.items.remove(self.item)
	def getName(self):
		return f"Delete item \"{self.item.name}\" from category \"{self.category.name}\""
	def save(self):
		return {
			"type": "delete_item",
			"category": self.category.save(),
			"item": self.item.save()
		}

class AddCategoryAction(Action):
	def __init__(self, game: "Game", category: Category, index: int):
		self.game: "Game" = game
		self.category: Category = category
		self.index: int = index
	def execute(self):
		self.game.categories.insert(self.index, self.category)
	def getName(self):
		return f"Add category \"{self.category.name}\" to game"
	def save(self):
		return {
			"type": "add_category",
			"category": self.category.save(),
			"index": self.index
		}

class DeleteCategoryAction(Action):
	def __init__(self, game: "Game", category: Category):
		self.game: "Game" = game
		self.category: Category = category
	def execute(self):
		self.game.categories.remove(self.category)
	def getName(self):
		return f"Delete category \"{self.category.name}\" from game"
	def save(self):
		return {
			"type": "delete_category",
			"category": self.category.save()
		}

class RenameItemAction(Action):
	def __init__(self, category: Category, item: Item, newName: str):
		self.category: Category = category
		self.item: Item = item
		self.newName: str = newName
	def execute(self):
		self.item.name = self.newName
	def getName(self):
		return f"Rename item \"{self.item.name}\" in category \"{self.category.name}\" to \"{self.newName}\""
	def save(self):
		return {
			"type": "rename_item",
			"category": self.category.save(),
			"item": self.item.save(),
			"newName": self.newName
		}

class RenameCategoryAction(Action):
	def __init__(self, category: Category, newName: str):
		self.category: Category = category
		self.newName: str = newName
	def execute(self):
		self.category.name = self.newName
	def getName(self):
		return f"Rename category \"{self.category.name}\" to \"{self.newName}\""
	def save(self):
		return {
			"type": "rename_category",
			"category": self.category.save(),
			"newName": self.newName
		}

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
	def save(self):
		return {
			"type": "move_item",
			"category": self.category.save(),
			"item": self.item.save(),
			"amount": self.amount
		}

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
	def save(self):
		return {
			"type": "move_category",
			"category": self.category.save(),
			"amount": self.amount
		}

class ActiveVote:
	def __init__(self, game: "Game", action: Action):
		self.target = game
		self.action: Action = action
		self.target.votes.append(self)
		self.votes: list[bool] = [False for a in game.players]
		self.ready: list[bool] = [False for a in game.players]
		self.finished = False
	def vote(self, playername: str, vote: bool):
		index = self.target.players.index(playername)
		if not self.finished: self.votes[index] = vote
		self.ready[index] = True
		# Tally votes
		votes_for = 0
		votes_against = 0
		votes_null = 0
		for i in range(len(self.votes)):
			if self.ready[i] == False:
				votes_null += 1
			elif vote:
				votes_for += 1
			else:
				votes_against += 1
		# Can we switch to next stage early?
		pre_yes = votes_for > votes_against + votes_null
		pre_no = votes_against > votes_for + votes_null
		can_pre = (pre_yes or pre_no) and not self.finished
		all_voted = False not in self.ready
		can_next_stage = False or all_voted
		# Check for next stage
		if can_next_stage:
			# Next stage!
			if not self.finished:
				self.finished = True
				self.ready = [False for a in self.ready]
				# Finish!
				if votes_for > votes_against:
					self.action.execute()
			else:
				self.target.votes.remove(self)
	def toJSON(self):
		return {
			"action": self.action.getName(),
			"votes": self.votes,
			"ready": self.ready,
			"finished": self.finished
		}
	def save(self):
		return {
			"action": self.action.save(),
			"votes": self.votes,
			"ready": self.ready,
			"finished": self.finished
		}

class Game:
	def __init__(self):
		self.players: list[str] = []
		self.categories: list[Category] = []
		self.votes: list[ActiveVote] = []
	def get_categories(self) -> list[dict[str, str | list[str]]]:
		return [
			{"name": c.name, "items": [x.name for x in c.items]}
			for c in self.categories
		]
	def get_vote(self):
		return {
			"players": self.players,
			"votes": [v.toJSON() for v in self.votes]
		}
	def new_vote(self, action: Action):
		ActiveVote(self, action)
	def create_vote(self, data: dict):
		if data["type"] == "create_item":
			self.new_vote(AddItemAction(self.categories[data["categoryno"]], data["itemno"], Item(data["text"])))
		elif data["type"] == "delete_item":
			category = self.categories[data["categoryno"]]
			self.new_vote(DeleteItemAction(category, category.items[data["itemno"]]))
		elif data["type"] == "create_category":
			self.new_vote(AddCategoryAction(self, Category(data["text"]), data["categoryno"]))
		elif data["type"] == "delete_category":
			self.new_vote(DeleteCategoryAction(self, self.categories[data["categoryno"]]))
		elif data["type"] == "edit_item":
			category = self.categories[data["categoryno"]]
			self.new_vote(RenameItemAction(category, category.items[data["itemno"]], data["text"]))
		elif data["type"] == "edit_category":
			category = self.categories[data["categoryno"]]
			self.new_vote(RenameCategoryAction(category, data["text"]))
		elif data["type"] == "move_item":
			category = self.categories[data["categoryno"]]
			self.new_vote(MoveItemAction(category, category.items[data["itemno"]], data["amount"]))
		elif data["type"] == "move_category":
			self.new_vote(MoveCategoryAction(self, self.categories[data["categoryno"]], data["amount"]))
		else:
			print("Unknown type!!!")
			print(repr(data))
	def vote(self, data: dict):
		self.votes[data["vote_idx"]].vote(data["name"], data["value"])
	def save(self):
		return {
			"players": self.players,
			"categories": [c.save() for c in self.categories],
			"votes": [v.save() for v in self.votes]
		}

def save_game(game: Game):
	import json
	data = game.save()
	return json.dumps(data, indent='\t')

def load_game(data: str):
	import json
	decoded = json.loads(data)
	game = Game()
	game.players = decoded["players"]
	items = []
	def loadItem(data):
		# Search for existing item
		for t in items:
			if t.id == data["id"]:
				return t
		# Construct the data
		i = Item(data["name"])
		i.id = data["id"]
		items.append(i)
		return i
	categories = []
	def loadCategory(data):
		# Search for existing item
		for c in categories:
			if c.id == data["id"]:
				return c
		# Construct the data
		category = Category(data["name"])
		category.id = data["id"]
		for item in data["items"]:
			category.items.append(loadItem(item))
		categories.append(category)
		return category
	def loadAction(data):
		if data["type"] == "add_item":
			return AddItemAction(loadCategory(data["category"]), data["index"], loadItem(data["item"]))
		elif data["type"] == "delete_item":
			return DeleteItemAction(loadCategory(data["category"]), loadItem(data["item"]))
		elif data["type"] == "add_category":
			return AddCategoryAction(game, loadCategory(data["category"]), data["index"])
		elif data["type"] == "delete_category":
			return DeleteCategoryAction(game, loadCategory(data["category"]))
		elif data["type"] == "rename_item":
			return RenameItemAction(loadCategory(data["category"]), loadItem(data["item"]), data["newName"])
		elif data["type"] == "rename_category":
			return RenameCategoryAction(loadCategory(data["category"]), data["newName"])
		elif data["type"] == "move_item":
			return MoveItemAction(loadCategory(data["category"]), loadItem(data["item"]), data["amount"])
		elif data["type"] == "move_category":
			return MoveCategoryAction(game, loadCategory(data["category"]), data["amount"])
		else:
			return Action()
	for category in decoded["categories"]:
		game.categories.append(loadCategory(category))
	game.votes = [ActiveVote(game, loadAction(v["action"])) for v in decoded["votes"]]
	for vote_data in decoded["votes"]:
		activeVote = ActiveVote(game, loadAction(vote_data["action"]))
		activeVote.votes = vote_data["votes"]
		activeVote.ready = vote_data["ready"]
		activeVote.finished = vote_data["finished"]
	return game
