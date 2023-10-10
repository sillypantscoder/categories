class Action:
	def __init__(self):
		pass

class Category:
	def __init__(self, name: str):
		self.name: str = name
		self.items: list[Item] = []

class Item:
	def __init__(self, name: str):
		self.name: str = name

class Game:
	def __init__(self):
		self.players: list[str] = []
		self.categories: list[Category] = []
		self.currentVote: None | Action = None
		self.voteQueue: list[Action] = []
		self.categories.append(Category("hi"))
		for i in range(10): self.categories[0].items.append(Item(f"ASDFASDF{i}"))
	def get_categories(self) -> list[dict[str, str | list[str]]]:
		return [
			{"name": c.name, "items": [x.name for x in c.items]}
			for c in self.categories
		]