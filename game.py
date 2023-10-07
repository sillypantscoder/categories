class Action:
	def __init__(self):
		pass

class Category:
	def __init__(self, name):
		self.name: str = name
		self.items: list[str] = []

class Game:
	def __init__(self):
		self.players: list[str] = []
		self.categories: list[Category] = []
		self.currentVote: None | Action = None
		self.voteQueue: list[Action] = []
	def get_categories(self) -> list[dict[str, str | list[str]]]:
		return [
			{"name": c.name, "items": c.items}
			for c in self.categories
		]