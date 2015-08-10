import random

COLORS = ["Brown", "Gray", "Blue", "Yellow", "Red", "Green", "Purple"]
COST_NAMES = ["Coin", "Wood", "Stone", "Clay", "Ore", "Loom", "Glass", "Papyrus"]
MATERIAL_NAMES = ["Wood", "Stone", "Clay", "Ore"]
GOOD_NAMES = ["Loom", "Glass", "Papyrus"]
	
class Player(object):
	def __init__(self, name, wonder):
		self.name = name
		self.wonder = wonder
		self.wonder_stages_built = 0
		self.buildings = []
		self.money = 3
		self.hand = []
		self.resources = [wonder.resource]
		self.vps = 0
		self.trade_east = [2,2,2,2,2,2,2]
		self.trade_west = [2,2,2,2,2,2,2]
		self.shields = 0
		self.conflict = []
		self.science = {Compass: 0, Cog: 0, Tablet: 0, Choice: 0}
		self.points_from_cards = []
		self.east_neighbor = None
		self.west_neighbor = None
		
	def can_afford(self, card):
		for res_set in self.resources:	
			for i in range(len(card.cost[1:])):
				if card.cost[i+1] >= res_set[i]:
					break
			return True
		return False
	
	def build_card(self, card):
		self.money -= card.cost[0]
		self.buildings.append(card)
		if card.color == "Brown":
			self.add_resources(card.resource + [0, 0, 0])
		elif card.color == "Gray":
			self.add_resources([0, 0, 0, 0] + card.resource)
		elif card.color == "Blue":
			self.vps += card.points
		elif card.color == "Yellow":
			if card.effect[0] == "coins":
				# card.effect == ("coins", number, color, who)
				if card.effect[2] == "none":
					# give "number" of coins unconditionally
					self.money += card.effect[1]
				else:
					coins = 0
					if card.effect[3] == "self" or card.effect[3] == "all":
						for building in self.buildings:
							if building.color == card.effect[2]:
								coins += card.effect[1]
					if card.effect[3] == "neighbors" or card.effect[3] == "all":
						for building in self.east_neighbor.buildings:
							if building.color == card.effect[2]:
								coins += card.effect[1]
						for building in self.west_neighbor.buildings:
							if building.color == card.effect[2]:
								coins += card.effect[1]
					self.money += coins
			elif card.effect[0] == "trade":
				if card.effect[1] == "east":
					self.trade_east[0:4] = [1, 1, 1, 1]
				elif card.effect[1] == "west":
					self.trade_west[0:4] = [1, 1, 1, 1]
				elif card.effect[1] == "goods":
					self.trade_east[4:7] = [1, 1, 1]
					self.trade_west[4:7] = [1, 1, 1]
			elif card.effect[0] == "resource":
				if card.effect[1] == "materials":
					self.add_resources([1,1,1,1,0,0,0])
				elif card.effect[1] == "goods":
					self.add_resources([0,0,0,0,1,1,1])
			elif card.effect[0] == "coins/vp":
				# card.effect = ("coins/vp", coins, vps, type, who)
				# Gives "coins" coins now, and "vps" VPs at the end of the game
				# based on how many of "type" "who" has
				coins = 0
				if card.effect[4] == "self" or card.effect[4] == "all":
					if card.effect[3] == "wonder":
						coins += card.effect[1] * self.wonder_stages_built
					else:
						for building in self.buildings:
							if building.color == card.effect[2]:
								coins += card.effect[1]
				if card.effect[4] == "neighbors" or card.effect[4] == "all":
					for building in self.east_neighbor.buildings:
						if building.color == card.effect[3]:
							coins += card.effect[1]
					for building in self.west_neighbor.buildings:
						if building.color == card.effect[3]:
							coins += card.effect[1]
				self.money += coins
				self.points_from_cards.append("Yellow", card.effect[2], [card.effect[3]], card.effect[4])
		elif card.color == "Red":
			self.shields += card.shields
		elif card.color == "Green":
			self.science[card.symbol] += 1
		elif card.color == "Purple":
			if card.effect == "science":
				self.science[Choice] += 1
			elif card.effect[0] == "vp":
				# card.effect = ("vp", number, [types], who)
				self.points_from_card.append("Purple", card.effect[1], card.effect[2], card.effect[3])

	def add_resources(self, res):
		if res.count(0) < 6:
			first = True
			for i in range(len(res)):
				if res[i] > 0:
					if first:
						for res_set in self.resources:
							res_set[i] += res[i]
						first = False
					else:
						for res_set in self.resources:
							new_res_set = list(res_set)
							new_res_set[i] += res[i]
							self.resources.append(new_res_set)
		else:
			for i in range(len(res)):
				for res_set in self.resources:
					res_set[i] += res[i]
		
class Wonder(object):
	def __init__(self, name, city, resource, stages):
		self.name = name
		self.city = city
		self.resource = resource
		self.stages = stages
		
	def __str__(self):
		if self.name == "Statue of Zeus" or self.name == "Temple of Artemis":
			return "The %s in %s" % (self.name, self.city)
		return "The %s of %s" % (self.name, self.city)
		
class Card(object):
	def __init__(self, name, age, players, cost):
		self.name = name
		self.age = age
		self.players = players
		self.cost = cost
		self.pred = None
		self.succ = None
		
class BrownCard(Card):
	def __init__(self, name, age, players, cost, resource):
		self.name = name
		self.age = age
		self.players = players
		self.cost = cost
		self.pred = None
		self.succ = None
		self.resource = resource
		self.color = "Brown"
	
	def __str__(self):
		cost_str = cost_string(self.cost)
		res_list = []
		for i in range(len(self.resource)):
			if self.resource[i] > 0:
				res_list.append("%d %s" % (self.resource[i], 
										   MATERIAL_NAMES[i]))
		res_string = " / ".join(res_list)
		return "%s (%d+)\nAge %d %s Card\nCost: %s\nResources: %s" % (self.name, self.players, self.age, self.color, cost_string, res_string)
		
class GrayCard(Card):
	def __init__(self, name, age, players, resource):
		self.name = name
		self.age = age
		self.players = players
		self.cost = [0, 0, 0, 0, 0, 0, 0, 0]
		self.pred = None
		self.succ = None
		self.resource = resource
		self.color = "Gray"
	
	def __str__(self):
		if self.resource == [1,0,0]:
			res_string = "1 Loom"
		elif self.resource == [0,1,0]:
			res_string = "1 Glass"
		else:
			res_string = "1 Papyrus"
		return "%s (%d+)\nAge %d %s Card\nCost: Free\nResource: %s" % (self.name, self.players, self.age, self.color, res_string)
		
class BlueCard(Card):
	def __init__(self, name, age, players, cost, pred, succ, points):
		self.name = name
		self.age = age
		self.players = players
		self.cost = cost
		self.pred = pred
		self.succ = succ
		self.points = points
		self.color = "Blue"
		
	def __str__(self):
		output_str = "%s (%d+)\nAge %d %s Card\n" % (self.name, self.players, self.age, self.color)
		output_str += "Cost: %s\n" % cost_string(self.cost)
		if self.pred != ['']:
			pred_str = ", ".join(self.pred)
			output_str += "Builds From: %s\n" % pred_str
		if self.succ != ['']:
			succ_str = ", ".join(self.succ)
			output_str += "Builds Into: %s\n" % succ_str
		output_str += "%d Victory Points" % self.points
		return output_str
				
class YellowCard(Card):
	def __init__(self, name, age, players, cost, pred, succ, effect):
		self.name = name
		self.age = age
		self.players = players
		self.cost = cost
		self.pred = pred
		self.succ = succ
		self.effect = effect
		self.color = "Yellow"
		
	def __str__(self):
		output_str = "%s (%d+)\nAge %d %s Card\n" % (self.name, self.players, self.age, self.color)
		output_str += "Cost: %s\n" % cost_string(self.cost)
		if self.pred != ['']:
			pred_str = ", ".join(self.pred)
			output_str += "Builds From: %s\n" % pred_str
		if self.succ != ['']:
			succ_str = ", ".join(self.succ)
			output_str += "Builds Into: %s\n" % succ_str
		output_str += "%s" % effect_string(self.effect)
		return output_str
		
class RedCard(Card):
	def __init__(self, name, age, players, cost, pred, succ, shields):
		self.name = name
		self.age = age
		self.players = players
		self.cost = cost
		self.pred = pred
		self.succ = succ
		self.shields = shields
		self.color = "Red"
		
	def __str__(self):
		output_str = "%s (%d+)\nAge %d %s Card\n" % (self.name, self.players, self.age, self.color)
		output_str += "Cost: %s\n" % cost_string(self.cost)
		if self.pred != ['']:
			pred_str = ", ".join(self.pred)
			output_str += "Builds From: %s\n" % pred_str
		if self.succ != ['']:
			succ_str = ", ".join(self.succ)
			output_str += "Builds Into: %s\n" % succ_str
		output_str += "%d Shields" % self.shields
		return output_str
		
class GreenCard(Card):
	def __init__(self, name, age, players, cost, pred, succ, symbol):
		self.name = name
		self.age = age
		self.players = players
		self.cost = cost
		self.pred = pred
		self.succ = succ
		self.symbol = symbol
		self.color = "Green"
		
	def __str__(self):
		output_str = "%s (%d+)\nAge %d %s Card\n" % (self.name, self.players, self.age, self.color)
		output_str += "Cost: %s\n" % cost_string(self.cost)
		if self.pred != ['']:
			pred_str = ", ".join(self.pred)
			output_str += "Builds From: %s\n" % pred_str
		if self.succ != ['']:
			succ_str = ", ".join(self.succ)
			output_str += "Builds Into: %s\n" % succ_str
		output_str += "%s" % self.symbol
		return output_str
		
class PurpleCard(Card):
	def __init__(self, name, cost, effect):
		self.name = name
		self.age = 3
		self.cost = cost
		self.pred = None
		self.succ = None
		self.effect = effect
		self.color = "Purple"
		
	def __str__(self):
		output_str = "%s\nCost: %s\n%s" % (self.name, cost_string(self.cost), effect_string(self.effect))
		return output_str
		
def cost_string(cost):
	cost_list = []
	for i in range(len(cost)):
		if cost[i] > 0:
			cost_list.append("%d %s" % (cost[i], COST_NAMES[i]))
	if not cost_list:
		cost_str = "Free"
	else:
		cost_str = ", ".join(cost_list)
	return cost_str
	
def effect_string(effect):
	if effect[0] == "coins":
		if effect[2] == "none":
			return "%d Coins" % effect[1]
		else:
			effect_str = "%d Coin" % effect[1]
			if effect[1] > 1:
				effect_str += "s"
			effect_str += " per %s Card " % effect[2]
			if effect[3] == "self":
				effect_str += "in Own City"
			elif effect[3] == "neighbors":
				effect_str += "in Neighboring Cities"
			elif effect[3] == "all":
				effect_str += "in Own and Neighboring Cities"
			return effect_str
	elif effect[0] == "trade":
		if effect[1] == "east":
			return "Discount on Wood, Stone, Clay, and Ore from Eastern Neighbor"
		elif effect[1] == "west":
			return "Discount on Wood, Stone, Clay, and Ore from Western Neighbor"
		else:
			return "Discount on Loom, Glass, and Papyrus from Neighbors"""
	elif effect[0] == "resource":
		if effect[1] == "goods":
			return "1 Loom / 1 Glass / 1 Papyrus"
		else:
			return "1 Wood / 1 Stone / 1 Clay / 1 Ore"
	elif effect[0] == "coins/vp":
		effect_str = "%d Coin" % effect[1]
		if effect[1] > 1:
			effect_str += "s"
		effect_str += " and %d VP" % effect[2]
		if effect[2] > 1:
			effect_str += "s"
		if effect[3] == "wonder":
			effect_str += " per Wonder Stage Built "
		else:
			effect_str += " per %s Card " % effect[3]
		if effect[4] == "self":
			effect_str += "in Own City"
		elif effect[4] == "neighbors":
			effect_str += "in Neighboring Cities"
		elif effect[4] == "all":
			effect_str += "in Own and Neighboring Cities"
		return effect_str
	elif effect[0] == "vp":
		effect_str = "%d VP" % effect[1]
		if effect[1] > 1:
			effect_str += "s"
		effect_str += " per "
		if len(effect[2]) > 1:
			effect_str += "Brown, Gray, and Purple Card "
		elif effect[2][0] == "defeat":
			effect_str += "Defeat Token "
		elif effect[2][0] == "wonder":
			effect_str += "Wonder Stage Built "
		else:
			effect_str += "%s Card " % effect[2][0]
		if effect[3] == "self":
			effect_str += "in Own City"
		elif effect[3] == "neighbors":
			effect_str += "in Neighboring Cities"
		elif effect[3] == "all":
			effect_str += "in Own and Neighboring Cities"
		return effect_str
	elif effect == "science":
		return "Science Symbol of Choice"
		
def gen_cards(file):
	cards = []
	f = open(file)
	for line in f:
		item = line.split(",")
		name = item[0]
		age = int(item[1])
		players = int(item[2])
		cost = map(int, item[3:11])
		color = item[11]
		if color == "Brown":
			resource = map(int, item[12:16])
			cards.append(BrownCard(name, age, players, cost, resource))
		elif color == "Gray":
			resource = map(int, item[12:15])
			cards.append(GrayCard(name, age, players, resource))
		elif color == "Blue":
			pred = item[12].split(";")
			succ = item[13].split(";")
			points = int(item[14])
			cards.append(BlueCard(name, age, players, cost, pred, succ, points))
		elif color == "Yellow":
			pred = item[12].split(";")
			succ = item[13].split(";")
			if item[14] == "coins":
				# ("coins", number, color, who)
				# Gives "number" of coins for every "color" card belonging to "who"
				# If "color" is "none", just give "number" of coins
				# "who" = {"self": own player, "neighbors": players to the left and right, "all": self and neighbors}
				effect = (item[14], int(item[15]), item[16], item[17].rstrip("\n"))
			elif item[14] == "trade" or item[14] == "resource":
				effect = (item[14], item[15].rstrip("\n"))
			elif item[14] == "coins/vp":
				# Same as "coins" except the second number is victory points
				effect = (item[14], int(item[15]), int(item[16]), item[17], item[18].rstrip("\n"))
			cards.append(YellowCard(name, age, players, cost, pred, succ, effect))
		elif color == "Red":
			pred = item[12].split(";")
			succ = item[13].split(";")
			shields = int(item[14])
			cards.append(RedCard(name, age, players, cost, pred, succ, shields))
		elif color == "Green":
			pred = item[12].split(";")
			succ = item[13].split(";")
			symbol = item[14].rstrip("\n")
			cards.append(GreenCard(name, age, players, cost, pred, succ, symbol))
		elif color == "Purple":
			if item[12] == "vp":
				effect = (item[12], int(item[13]), item[14].split(";"), item[15].rstrip("\n"))
			else:
				effect = (item[12].rstrip("\n"))
			cards.append(PurpleCard(name, cost, effect))
	f.close()
	return cards

def build_decks(num_players, file):
	all_cards = gen_cards(file)
	age_decks = ([], [], [])
	guilds = []
	for card in all_cards:
		if card.color == "Purple":
			guilds.append(card)
		elif card.players <= num_players:
			age_decks[card.age - 1].append(card)
	for i in range(num_players + 2):
		rand = random.randrange(len(guilds))
		age_decks[2].append(guilds.pop(rand))
	return age_decks
	
all_cards = gen_cards("card_list.txt")
for card in all_cards:
	if card.color == "Yellow" or card.color == "Purple":
		print card