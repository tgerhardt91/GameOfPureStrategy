#!/usr/bin/python

from utils.log import log
import json

#make python 2 and 3 behave the same for raw input
if hasattr(__builtins__, 'raw_input'):
    input = raw_input



data_file = "data.json"



num_games = 100000
num_cards = 13

#any bot class names to leave off the scoreboard for various reasons.
bots_to_skip = ["HumanBot", "WatchingBot"]

def generate_json():
	#import all the bots
	from bots.simpleBots import BasicBot, ObviousBot, RandomBot, HumanBot, ObviousPlusOneBot
	from bots.alexBots import LearningBot, WatchingBot, InterestingBot
	from bots.philBots import PhillipBotUpBot, PhillipAdaptoBot
	from bots.brianBots import GreedBot, SafeBetBot, OddBot

	import inspect, sys, itertools, time
	
	
	clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
	print(clsmembers)
	
	
	#########rest of imports go here ###########
	from gameArena import GameArena
	############################################
	
	start = time.time()
	
	bot_names = [bot[0] for bot in clsmembers]
	bot_results = { name:{} for name in bot_names}
	
	
	for combination in itertools.combinations(clsmembers,2):
		bot1_name, bot1_class = combination[0]
		bot2_name, bot2_class = combination[1]
	
		if bot1_name in bots_to_skip or bot2_name in bots_to_skip:
			continue
	
		print(str(bot1_name)+" vs "+str(bot2_name))
		game = GameArena(num_cards=num_cards, num_games=num_games, player_arr=[bot1_class, bot2_class])
		bot1_score, bot2_score = game.play(play_method = "quiet")
		
		#update player results
		bot_results[bot1_name][bot2_name] = bot1_score
		bot_results[bot2_name][bot1_name] = bot2_score
	
	
	with open(data_file, 'w') as outfile:
	    json.dump(bot_results, outfile, indent=4, sort_keys=True)
	print(bot_results)
	
	print("Completed scoreboard in "+str(time.time()-start)+" seconds")




def generate_scoreboard():
	import operator
	with open(data_file) as f:
		data = json.load(f)

		#get wins per bot
		wins_per_bot = { name:{} for name in data.keys() if name not in bots_to_skip}
		for bot_name, result in data.items():
			if bot_name in bots_to_skip:
				continue
			wins = 0
			for result_name, result_number in result.items():
				if result_name in bots_to_skip:
					continue
				if result_number > num_games/2:
					wins+=1
			wins_per_bot[bot_name] = wins

		sorted_bots = sorted(wins_per_bot.items(), key=operator.itemgetter(1))
		sorted_bots.reverse()
		#print(sorted_bots)
		

		#print ranked bots
		with open("bot_scores.md", "w") as o:
			o.write("# Bot Scores\n")
			o.write("Results of "+str(num_games)+" 1v1 games, with "+str(num_cards)+" cards each\n\n")
			o.write("|rank|bot|score|results|\n")
			o.write("|-----|-----|-----|-----|\n")
			i=0
			last_wins = num_games
			for bot_name, wins in sorted_bots:
				if wins < last_wins:
					i+=1 #handle ties
				last_wins = wins
				#be obnoxious about scores


				o.write("|**#"+str(i)+"**|"+str(bot_name)+"|"+str(wins)+"|")

				sorted_opponents = sorted(data[bot_name].items(), key=operator.itemgetter(1))
				sorted_opponents.reverse()
				for opponent,won_games in sorted_opponents:
					if opponent in bots_to_skip:
						continue
					win_percent = round(won_games/num_games*100,2)
					if win_percent > 50:
						o.write("WIN ")
					else:
						o.write("LOSS ")
					o.write(str(win_percent)+"% vs "+str(opponent)+"<br>")
				o.write("|\n")



if __name__== "__main__":
	#generate_json()
	generate_scoreboard()
