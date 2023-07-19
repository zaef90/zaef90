import openai
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold
from main import get_today_matches
import orjson
import os
import json
import requests
import csv

bot = Bot(token="6334349451:AAGm91LG9T0WqV8GberB1tZiwQPUDQSKnXU", parse_mode=types.ParseMode.HTML)


storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

match_id = ""

@dp.message_handler(text="Analyze Home Stats")
async def handle_home_stats_button(message: types.Message):
    await message.answer(f"Please wait, I'm thinking about how to present the home team's stats\n\n"
                             "The operation may take up to 30 seconds.\n\n"
                             "Babz")
    await handle_home_stats(message)


@dp.message_handler(text="Analyze Away Stats")
async def handle_away_stats_button(message: types.Message):
    await message.answer(f"Please wait, I'm thinking about how to present you the away team's stats... \n\n"
                " The operation may take up to 30 seconds.\n\n"
                "Babz")

    await handle_away_stats(message)


@dp.message_handler(text="Analyze both teams")
async def handle_analyze_button(message: types.Message):
    await message.answer("Please be patient; I am thinking to provide you with a very precise analysis.\n\n"
                        "babz")
    await handle_analyze(message)

@dp.message_handler(commands="babz")
async def start(message: types.Message):
    start_buttons = ["Load today Matches", "Load Stats", "Analyze Home Stats", "Analyze Away Stats", "Analyze both teams", "Corners Prediction", "Cards Prediction"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)


    await message.answer(f'''{hbold("Hello! I'm DayoBabz, your companion for insightful football match analyses. As an expert with over 8 years of experience, my mission is to share the wealth of my knowledge and provide you with a pleasant and hassle-free experience while analyzing your favorite matches. Alongside offering wise advice for your sports betting, I aim to utilize my expertise to ensure you gain the most from our journey together. Together, we'll dissect the games and enable you to make informed decisions. May luck be on your side, and may the excitement of football keep growing!")}
                         
                         
    {hbold('Notice:')} {hbold("I'm still under development, so please be patient.")}


    {hbold('Some options like cards and corners predictions are under development')}''', reply_markup=keyboard)


@dp.message_handler(Text(equals="Load today Matches"))
async def get_matches(message: types.Message):
    await message.answer("Give me a few seconds please, I’ll look up today’s matches for you… 😊")
    get_today_matches()
    
    

    with open("matches.json", encoding='utf-8') as file:
        data = orjson.loads(file.read())
        match_info = ""
        for item in data:
            match_info += f"{hbold('ID: ')} {hbold(item.get('id'))}\n" \
                        f"{hbold('time: ')} {item.get('heure')}\n" \
                        f"{hbold('league: ')}{item.get('league')}\n" \
                        f"{hbold('home: ')}{item.get('team_a')}\n" \
                        f"{hbold('away: ')}{item.get('team_b')}\n" \
                        f"---------------------------------------------------------------------------------------------------------------\n\n"
            if len(match_info) >= 4000:
                await message.answer(match_info)
                match_info = ""
                            
        if match_info:
            await message.answer(match_info)


            

@dp.message_handler(Text(equals="Load Stats"))
async def get_home_stats(message: types.Message):
    
    await message.answer("please enter the match_id value :")
    await dp.register_message_handler(process_match_id)
    await get_home_stats(message)

@dp.message_handler(text="Corners Prediction")
async def handle_corners_button(message: types.Message):
    await handle_corners(message)

@dp.message_handler(text="Cards Prediction")
async def handle_cartons_button(message: types.Message):
    await handle_cartons(message)


async def handle_cartons(message: types.Message):
    try:
        file_path = "div.csv"
        file_path = file_path.strip()
        with open("stats.json", encoding='utf-8') as file:
            data = orjson.loads(file.read())
            team_a = data['team_a_stats'] 
            team_b = data['team_b_stats']     
            home_a = team_a["name_tr"]
            away_b = team_b["name_tr"]
         #Please estimate the number of corners that can occur between {home_a} and {away_b}. I want numbers, do not give me reasons.   
        prompt = f"Please estimate the number of cards that can occur between {home_a} and {away_b}. I want numbers, do not give me reasons. "
        # prompt = f"Estime le nombre de cartons qu'il peut y avoir entre {home_a} et {away_b} je veux un chiffres. ne me donne pas de raisons"
        response = read_file_content(file_path, prompt)
        #saving user response into a variable=> c'est important
        # user_data = await storage.get_data(user=message.from_user.id)
        # user_data["home_step_1"] = response
        # await storage.set_data(user=message.from_user.id, data=user_data)

        await message.answer(response)
    except Exception as e:
        print(f"Error: {e}")


async def handle_corners(message: types.Message):
    try:
        file_path = "div.csv"
        file_path = file_path.strip()
        with open("stats.json", encoding='utf-8') as file:
            data = orjson.loads(file.read())
            team_a = data['team_a_stats'] 
            team_b = data['team_b_stats']     
            home_a = team_a["name_tr"]
            away_b = team_b["name_tr"]
            
        prompt = f"Please estimate the number of corners that can occur between {home_a} and {away_b}. I want numbers, do not give me reasons."
        # prompt = f"Estime le nombre de corners qu'il peut y avoir entre {home_a} et {away_b} je veux des chiffres. ne me donne pas de raisons"
        response = read_file_content(file_path, prompt)

        await message.answer(response)
    except Exception as e:
        print(f"Error: {e}")


def write_to_csv(data, filename):
    keys = data[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


async def process_match_id(message: types.Message):
    match_id = message.text.strip()

    try:
        match_id = int(match_id)  # Vérifiez si match_id est un entier valide
    except ValueError:
        await message.answer("match_id should be an integer number. avoid spaces and providing the match. pleasetry again...")
        return
    url = f"https://app.footystats.org/app-h2h?key=pattystats&match_id={match_id}&dimension=season&include=stats"
    headers = {"User-Agent": "dart"}

    response = requests.get(url, headers=headers)
    data = response.json()['data']
    team_a = data['team_a_stats']
    team_a_s = team_a['stats']
    team_a_ad = team_a_s['additional_info']
    team_b = data['team_b_stats']
    team_b_s = team_b['stats']
    team_b_ad = team_b_s['additional_info']
    home_a = team_a["name_tr"]
    away_b = team_b["name_tr"]
    
    with open("stats.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    
    
    tm_a_div = ({
        "Team": home_a,
        "homeDefenceAdvantage": team_a_s.get('homeDefenceAdvantage'),
        "homeAdvantage": team_a_s.get('homeOverallAdvantage'),
        "foulsAVG": team_a_s.get("foulsAVG_home"),
        "dangerous_attacks_avg": team_a_s.get('dangerous_attacks_avg_home'),
        "attacks_avg": team_a_s.get('attacks_avg_home'),
        "SoT": team_a_s.get('shotsOnTargetAVG_home'),
        "shotsOffTargetAVG": team_a_s.get('shotsOffTargetAVG_home'),
        "form": team_a_ad.get('formRun_home'),
        "performance_rank": team_a.get('performance_rank'),
        "PossAVG_at_H": team_a_s.get("possessionAVG_home"),
        "shot_conversion_rate": team_a_ad.get('shot_conversion_rate_home'),
        "fh_cards_for_avg": team_a_ad.get('fh_cards_for_avg_home'),
        "2h_cards_for_avg": team_a_ad.get('2h_cards_for_avg_home'),
        "fh_cards_against_avg": team_a_ad.get('fh_cards_against_avg_home'),
        "2h_cards_against_avg": team_a_ad.get('2h_cards_against_avg_home'),
        "cards_against": team_a_ad.get('cards_against_home'),
        "cards_for_avg": team_a_ad.get('cards_for_avg_home'),
        "cards_against_avg": team_a_ad.get('cards_against_avg_home'),
        "fouls_against_avg": team_a_ad.get('fouls_against_avg_home'),
        "corners_earned_2h_avg": team_a_ad.get('corners_earned_2h_avg_home'),
        "cornersAVG": team_a_s.get('cornersAVG_home'),
        "cornersAgainstAVG": team_a_s.get('cornersAgainstAVG_home'),
        "cornersHighest": team_a_s.get('cornersHighest_overall'),
        "cornersLowest": team_a_s.get('cornersLowest_overall'),
        "cardsHighest": team_a_s.get('cardsHighest_overall'),
        "cardsLowest": team_a_s.get('cardsLowest_overall')
    },
    {
        "Team": away_b,
        "homeDefenceAdvantage": team_b_s.get('homeDefenceAdvantage'),
        "homeAdvantage": team_b_s.get('homeOverallAdvantage'),
        "foulsAVG": team_b_s.get("foulsAVG_away"),
        "dangerous_attacks_avg": team_b_s.get('dangerous_attacks_avg_away'),
        "attacks_avg": team_b_s.get('attacks_avg_away'),
        "SoT": team_b_s.get('shotsOnTargetAVG_away'),
        "shotsOffTargetAVG": team_b_s.get('shotsOffTargetAVG_away'),
        "form": team_b_ad.get('formRun_away'),
        "performance_rank": team_b.get('performance_rank'),
        "PossAVG_at_H": team_b_s.get("possessionAVG_away"),
        "shot_conversion_rate": team_b_ad.get('shot_conversion_rate_away'),
        "fh_cards_for_avg": team_b_ad.get('fh_cards_for_avg_away'),
        "2h_cards_for_avg": team_b_ad.get('2h_cards_for_avg_away'),
        "fh_cards_against_avg": team_b_ad.get('fh_cards_against_avg_away'),
        "2h_cards_against_avg": team_b_ad.get('2h_cards_against_avg_away'),
        "cards_against": team_b_ad.get('cards_against_away'),
        "cards_for_avg": team_b_ad.get('cards_for_avg_away'),
        "cards_against_avg": team_b_ad.get('cards_against_avg_away'),
        "fouls_against_avg": team_b_ad.get('fouls_against_avg_away'),
        "corners_earned_2h_avg": team_b_ad.get('corners_earned_2h_avg_away'),
        "cornersAVG": team_b_s.get('cornersAVG_away'),
        "cornersAgainstAVG": team_b_s.get('cornersAgainstAVG_away'),
        "cornersHighest": team_b_s.get('cornersHighest_overall'),
        "cornersLowest": team_b_s.get('cornersLowest_overall'),
        "cardsHighest": team_b_s.get('cardsHighest_overall'),
        "cardsLowest": team_b_s.get('cardsLowest_overall')  
    })
    with open("div.json", "w", encoding='utf-8') as file:
        json.dump(tm_a_div, file, indent=4, ensure_ascii=False)
    
    # Load the data from the div.json file
    with open('div.json', 'r') as file:
        data = json.load(file)

    # Extract the fieldnames from the first object in the data
    fieldnames = data[0].keys()

    # Write the data to a CSV file
    with open('div.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    


    team_a_stats_list = [{
                "Home_Team": team_a.get("name_tr"),
                "position": team_a.get("table_position"),
                "MP_at_H": team_a_s.get("seasonMatchesPlayed_home"),
                "GF_at_H": team_a_s.get("seasonScoredNum_home"),
                "GA_at_H": team_a_s.get("seasonConcededNum_home"),
                "goals_mins_at_H": team_a_s.get("seasonGoalsMin_home"),
                "GC_mins_at_H": team_a_s.get("seasonConcededMin_home"),
                "goal_diff_at_H": team_a_s.get("seasonGoalDifference_home"),
                "wins_at_H": team_a_s.get("seasonWinsNum_home"),
                "draws_at_H": team_a_s.get("seasonDrawsNum_home"),
                "losses_at_H": team_a_s.get("seasonLossesNum_home"),
                "form_at_H": team_a_ad.get("formRun_home"),
                "CS_at_H": team_a_s.get("seasonCS_home"),
                "ScoredAVG_H": team_a_s.get("seasonScoredAVG_home"),
                "Conceded_AVG_H": team_a_s.get("seasonConcededAVG_home"),
                "firstGoalScored_at_H": team_a_s.get("firstGoalScored_home"),
                "FTS_at_H": team_a_s.get("seasonFTSHT_home"),
                "FTS_HT_at_H": team_a_s.get("seasonFTS_home"),
                "PPG_at_H": team_a_s.get("seasonPPG_home"),
                "leadingAtHT_at_H": team_a_s.get("leadingAtHT_home"),
                "drawingAtHT_at_H": team_a_s.get("drawingAtHT_home"),
                "trailingAtHT_at_H": team_a_s.get("trailingAtHT_home"),
                "GS_HT_at_H": team_a_s.get("scoredGoalsHT_home"),
                "GC_HT_at_H": team_a_s.get("concededGoalsHT_home"),
                "CS_HT_at_H": team_a_s.get("seasonCSHT_home"),
                "GoalDiffHT_at_H": team_a_s.get("GoalDifferenceHT_home"),
                "shotsTotal_at_H": team_a_s.get("shotsTotal_home"),
                "shotsAVG_at_H": team_a_s.get("shotsAVG_home"),
                "SoT_Total_at_H": team_a_s.get("shotsOnTargetTotal_home"),
                "shotsOffTargetTotal_at_H": team_a_s.get("shotsOffTargetTotal_home"),
                "SoT_AVG_at_H": team_a_s.get("shotsOnTargetAVG_home"),
                "PossAVG_at_H": team_a_s.get("possessionAVG_home"),
                "attacks_avg_at_H": team_a_s.get("attacks_avg_home"),
                "dangerous_attacks_avg_at_H": team_a_s.get("dangerous_attacks_avg_home"),
                "xg_for_avg_at_H": team_a_s.get("xg_for_avg_home"),
                "xg_against_avg_at_H": team_a_s.get("xg_against_avg_home"),
                "foulsAVG_at_H": team_a_s.get("foulsAVG_home"),
                "offsidesAVG_at_H": team_a_s.get("offsidesAVG_home"),
                "goal_kicks_team_avg_at_H": team_a_ad.get("goal_kicks_team_avg_home"),
                "throwins_team_avg_at_H": team_a_ad.get("throwins_team_avg_home"),
                "GF_at_A": team_a_s.get("seasonScoredNum_away"),
                "GA_at_A": team_a_s.get("seasonConcededNum_away"),
                "goals_minutes_at_A": team_a_s.get("seasonGoalsMin_away"),
                "away_conceded_minutes_at_A": team_a_s.get("seasonConcededMin_away"),
                "goal_difference_at_A": team_a_s.get("seasonGoalDifference_away"),
                "wins_at_A": team_a_s.get("seasonWinsNum_away"),
                "draws_at_A": team_a_s.get("seasonDrawsNum_away"),
                "losses_at_A": team_a_s.get("seasonLossesNum_away"),
                "form_at_A": team_a_ad.get("formRun_away"),
                "CS_A": team_a_s.get("seasonCS_away"),
                "ScoredAVG_A": team_a_s.get("seasonScoredAVG_away"),
                "GA_AVG_A": team_a_s.get("seasonConcededAVG_away"),
                "firstGoalScored_at_A": team_a_s.get("firstGoalScored_away"),
                "FTS_at_A": team_a_s.get("seasonFTSHT_away"),
                "FTS_HT_at_A": team_a_s.get("seasonFTS_away"),
                "PPG_at_A": team_a_s.get("seasonPPG_away"),
                "leadingAtHT_at_A": team_a_s.get("leadingAtHT_away"),
                "drawingAtHT_at_A": team_a_s.get("drawingAtHT_away"),
                "trailingAtHT_at_A": team_a_s.get("trailingAtHT_away"),
                "GF_HT_at_A": team_a_s.get("scoredGoalsHT_away"),
                "GA_HT_at_A": team_a_s.get("concededGoalsHT_away"),
                "CS_HT_at_A": team_a_s.get("seasonCSHT_home"),
                "GD_HT_at_A": team_a_s.get("GoalDifferenceHT_away"),
                "shotsTotal_at_A": team_a_s.get("shotsTotal_away"),
                "shotsAVG_at_A": team_a_s.get("shotsAVG_away"),
                "SoT_Total_at_A": team_a_s.get("shotsOnTargetTotal_away"),
                "shotsOffTargetTotal_at_A": team_a_s.get("shotsOffTargetTotal_away"),
                "SoT_AVG_at_A": team_a_s.get("shotsOnTargetAVG_away"),
                "PossAVG_at_A": team_a_s.get("possessionAVG_away"),
                "attacks_avg_at_A": team_a_s.get("attacks_avg_away"),
                "dangerous_attacks_avg_at_A": team_a_s.get("dangerous_attacks_avg_away"),
                "xg_for_avg_at_A": team_a_s.get("xg_for_avg_away"),
                "xg_against_avg_at_A": team_a_s.get("xg_against_avg_away"),
                "foulsAVG_at_A": team_a_s.get("foulsAVG_away"),
                "offsidesAVG_at_A": team_a_s.get("offsidesAVG_away"),
                "goal_kicks_team_avg_at_A": team_a_ad.get("goal_kicks_team_avg_away"),
                "throwins_team_avg_at_A": team_a_ad.get("throwins_team_avg_away")
                }]
    team_b_stats_list = [{
                "Away_Team": team_b.get("name_tr"),
                "position": team_b.get("table_position"),
                "MP_at_H": team_b_s.get("seasonMatchesPlayed_home"),
                "GF_at_H": team_b_s.get("seasonScoredNum_home"),
                "GA_at_H": team_b_s.get("seasonConcededNum_home"),
                "goals_mins_at_H": team_b_s.get("seasonGoalsMin_home"),
                "GC_mins_at_H": team_b_s.get("seasonConcededMin_home"),
                "goal_diff_at_H": team_b_s.get("seasonGoalDifference_home"),
                "wins_at_H": team_b_s.get("seasonWinsNum_home"),
                "draws_at_H": team_b_s.get("seasonDrawsNum_home"),
                "losses_at_H": team_b_s.get("seasonLossesNum_home"),
                "form_at_H": team_b_ad.get("formRun_home"),
                "CS_at_H": team_b_s.get("seasonCS_home"),
                "ScoredAVG_H": team_b_s.get("seasonScoredAVG_home"),
                "Conceded_AVG_H": team_b_s.get("seasonConcededAVG_home"),
                "firstGoalScored_at_H": team_b_s.get("firstGoalScored_home"),
                "FTS_at_H": team_b_s.get("seasonFTSHT_home"),
                "FTS_HT_at_H": team_b_s.get("seasonFTS_home"),
                "PPG_at_H": team_b_s.get("seasonPPG_home"),
                "leadingAtHT_at_H": team_b_s.get("leadingAtHT_home"),
                "drawingAtHT_at_H": team_b_s.get("drawingAtHT_home"),
                "trailingAtHT_at_H": team_b_s.get("trailingAtHT_home"),
                "GS_HT_at_H": team_b_s.get("scoredGoalsHT_home"),
                "GC_HT_at_H": team_b_s.get("concededGoalsHT_home"),
                "CS_HT_at_H": team_b_s.get("seasonCSHT_home"),
                "GoalDiffHT_at_H": team_b_s.get("GoalDifferenceHT_home"),
                "shotsTotal_at_H": team_b_s.get("shotsTotal_home"),
                "shotsAVG_at_H": team_b_s.get("shotsAVG_home"),
                "SoT_Total_at_H": team_b_s.get("shotsOnTargetTotal_home"),
                "shotsOffTargetTotal_at_H": team_b_s.get("shotsOffTargetTotal_home"),
                "SoT_AVG_at_H": team_b_s.get("shotsOnTargetAVG_home"),
                "PossAVG_at_H": team_b_s.get("possessionAVG_home"),
                "attacks_avg_at_H": team_b_s.get("attacks_avg_home"),
                "dangerous_attacks_avg_at_H": team_b_s.get("dangerous_attacks_avg_home"),
                "xg_for_avg_at_H": team_b_s.get("xg_for_avg_home"),
                "xg_against_avg_at_H": team_b_s.get("xg_against_avg_home"),
                "foulsAVG_at_H": team_b_s.get("foulsAVG_home"),
                "offsidesAVG_at_H": team_b_s.get("offsidesAVG_home"),
                "goal_kicks_team_avg_at_H": team_b_ad.get("goal_kicks_team_avg_home"),
                "throwins_team_avg_at_H": team_b_ad.get("throwins_team_avg_home"),
                "GF_at_A": team_b_s.get("seasonScoredNum_away"),
                "GA_at_A": team_b_s.get("seasonConcededNum_away"),
                "goals_minutes_at_A": team_b_s.get("seasonGoalsMin_away"),
                "away_conceded_minutes_at_A": team_b_s.get("seasonConcededMin_away"),
                "goal_difference_at_A": team_b_s.get("seasonGoalDifference_away"),
                "wins_at_A": team_b_s.get("seasonWinsNum_away"),
                "draws_at_A": team_b_s.get("seasonDrawsNum_away"),
                "losses_at_A": team_b_s.get("seasonLossesNum_away"),
                "form_at_A": team_b_ad.get("formRun_away"),
                "CS_A": team_b_s.get("seasonCS_away"),
                "ScoredAVG_A": team_b_s.get("seasonScoredAVG_away"),
                "GA_AVG_A": team_b_s.get("seasonConcededAVG_away"),
                "firstGoalScored_at_A": team_b_s.get("firstGoalScored_away"),
                "FTS_at_A": team_b_s.get("seasonFTSHT_away"),
                "FTS_HT_at_A": team_b_s.get("seasonFTS_away"),
                "PPG_at_A": team_b_s.get("seasonPPG_away"),
                "leadingAtHT_at_A": team_b_s.get("leadingAtHT_away"),
                "drawingAtHT_at_A": team_b_s.get("drawingAtHT_away"),
                "trailingAtHT_at_A": team_b_s.get("trailingAtHT_away"),
                "GF_HT_at_A": team_b_s.get("scoredGoalsHT_away"),
                "GA_HT_at_A": team_b_s.get("concededGoalsHT_away"),
                "CS_HT_at_A": team_b_s.get("seasonCSHT_home"),
                "GD_HT_at_A": team_b_s.get("GoalDifferenceHT_away"),
                "shotsTotal_at_A": team_b_s.get("shotsTotal_away"),
                "shotsAVG_at_A": team_b_s.get("shotsAVG_away"),
                "SoT_Total_at_A": team_b_s.get("shotsOnTargetTotal_away"),
                "shotsOffTargetTotal_at_A": team_b_s.get("shotsOffTargetTotal_away"),
                "SoT_AVG_at_A": team_b_s.get("shotsOnTargetAVG_away"),
                "PossAVG_at_A": team_b_s.get("possessionAVG_away"),
                "attacks_avg_at_A": team_b_s.get("attacks_avg_away"),
                "dangerous_attacks_avg_at_A": team_b_s.get("dangerous_attacks_avg_away"),
                "xg_for_avg_at_A": team_b_s.get("xg_for_avg_away"),
                "xg_against_avg_at_A": team_b_s.get("xg_against_avg_away"),
                "foulsAVG_at_A": team_b_s.get("foulsAVG_away"),
                "offsidesAVG_at_A": team_b_s.get("offsidesAVG_away"),
                "goal_kicks_team_avg_at_A": team_b_ad.get("goal_kicks_team_avg_away"),
                "throwins_team_avg_at_A": team_b_ad.get("throwins_team_avg_away")
                }]

    home_f = json.dumps(team_a_stats_list, indent=4, ensure_ascii=False)
    away_f = json.dumps(team_b_stats_list, indent=4, ensure_ascii=False)


    # Check if the "file_store" folder exists, create it if not


    # Define the file path and name
    file_path = os.path.join("home_stats.json")

    # Save the JSON data to the file
    with open(file_path, "w", encoding='utf-8') as file:
        file.write(home_f)

    csv_file_path = os.path.join("home_stats.csv")

    # Convert the JSON data to a Python dictionary
    home_stats_data = json.loads(home_f)

    # Write the data to the CSV file
    write_to_csv(home_stats_data, csv_file_path)
    
    file_path_2 = os.path.join("away_stats.json")

    # Save the JSON data to the file
    with open(file_path_2, "w", encoding='utf-8') as file:
        file.write(away_f)
    csv_file_path2 = os.path.join("away_stats.csv")

    away_stats_data = json.loads(away_f)
    
    write_to_csv(away_stats_data, csv_file_path2)

    await message.answer(f"recherche des stats de l'equipe {home_a} en cours.... !")

    file_home_stats = os.path.join("home_stats.json")
    with open(file_home_stats, encoding='utf-8') as file:
        data = orjson.loads(file.read())
        # home_a = team_a["name_tr"]
        # away_b = team_b["name_tr"]
        
        
        for item in data:
            match_stats = (
                f"{hbold('Home_Team: ')} {item.get('Home_Team')}\n"
                f"{hbold('League Position: ')} {item.get('position')}\n"
                f"{hbold('stats:')} | {hbold('playing at Home')} | {hbold('playing at Away')}\n"
                f"{hbold('GF')} | {item.get('GF_at_H')} | {item.get('GF_at_A')}\n"
                f"{hbold('GA')} | {item.get('GA_at_H')} | {item.get('GA_at_A')}\n"
                f"{hbold('goals_mins')} | {item.get('goals_mins_at_H')} | {item.get('goals_minutes_at_A')}\n"
                f"{hbold('GC_mins')} | {item.get('GC_mins_at_H')} | {item.get('away_conceded_minutes_at_A')}\n"
                f"{hbold('goal_diff')} | {item.get('goal_diff_at_H')} | {item.get('goal_difference_at_A')}\n"
                f"{hbold('wins')} | {item.get('wins_at_H')} | {item.get('wins_at_A')}\n"
                f"{hbold('draws')} | {item.get('draws_at_H')} | {item.get('draws_at_A')}\n"
                f"{hbold('losses')} | {item.get('losses_at_H')} | {item.get('losses_at_A')}\n"
                f"{hbold('form')} | {item.get('form_at_H')} | {item.get('form_at_A')}\n"
                f"{hbold('CS')} | {item.get('CS_at_H')} | {item.get('CS_A')}\n"
                f"{hbold('ScoredAVG')} | {item.get('ScoredAVG_H')} | {item.get('ScoredAVG_A')}\n"
                f"{hbold('Conceded_AVG')} | {item.get('Conceded_AVG_H')} | {item.get('GA_AVG_A')}\n"
                f"{hbold('firstGoalScored')} | {item.get('firstGoalScored_at_H')} | {item.get('firstGoalScored_at_A')}\n"
                f"{hbold('FTS')} | {item.get('FTS_at_H')} | {item.get('FTS_at_A')}\n"
                f"{hbold('FTS_HT')} | {item.get('FTS_HT_at_H')} | {item.get('FTS_HT_at_A')}\n"
                f"{hbold('PPG')} | {item.get('PPG_at_H')} | {item.get('PPG_at_A')}\n"
                f"{hbold('leadingAtHT')} | {item.get('leadingAtHT_at_H')} | {item.get('leadingAtHT_at_A')}\n"
                f"{hbold('drawingAtHT')} | {item.get('drawingAtHT_at_H')} | {item.get('drawingAtHT_at_A')}\n"
                f"{hbold('trailingAtHT')} | {item.get('trailingAtHT_at_H')} | {item.get('trailingAtHT_at_A')}\n"
                f"{hbold('GS_HT')} | {item.get('GS_HT_at_H')} | {item.get('GF_HT_at_A')}\n"
                f"{hbold('GA_HT')} | {item.get('GC_HT_at_H')} | {item.get('GA_HT_at_A')}\n"
                f"{hbold('CS_HT')} | {item.get('CS_HT_at_H')} | {item.get('CS_HT_at_A')}\n"
                f"{hbold('GoalDiffHT')} | {item.get('GoalDiffHT_at_H')} | {item.get('GD_HT_at_A')}\n"
                f"{hbold('shotsTotal')} | {item.get('shotsTotal_at_H')} | {item.get('shotsTotal_at_A')}\n"
                f"{hbold('shotsAVG')} | {item.get('shotsAVG_at_H')} | {item.get('shotsAVG_at_A')}\n"
                f"{hbold('SoT_Total')} | {item.get('SoT_Total_at_H')} | {item.get('SoT_Total_at_A')}\n"
                f"{hbold('shotsOffTargetTotal')} | {item.get('shotsOffTargetTotal_at_H')} | {item.get('shotsOffTargetTotal_at_A')}\n"
                f"{hbold('SoT_AVG')} | {item.get('SoT_AVG_at_H')} | {item.get('SoT_AVG_at_A')}\n"
                f"{hbold('PossAVG')} | {item.get('PossAVG_at_H')} | {item.get('PossAVG_at_A')}\n"
                f"{hbold('attacks_avg')} | {item.get('attacks_avg_at_H')} | {item.get('attacks_avg_at_A')}\n"
                f"{hbold('dangerous_attacks_avg')} | {item.get('dangerous_attacks_avg_at_H')} | {item.get('dangerous_attacks_avg_at_A')}\n"
                f"{hbold('xg_for_avg')} | {item.get('xg_for_avg_at_H')} | {item.get('xg_for_avg_at_A')}\n"
                f"{hbold('xg_against_avg')} | {item.get('xg_against_avg_at_H')} | {item.get('xg_against_avg_at_A')}\n"
                f"{hbold('foulsAVG')} | {item.get('foulsAVG_at_H')} | {item.get('foulsAVG_at_A')}\n"
                f"{hbold('offsidesAVG')} | {item.get('offsidesAVG_at_H')} | {item.get('offsidesAVG_at_A')}\n"
                f"{hbold('goal_kicks_team_avg')} | {item.get('goal_kicks_team_avg_at_H')} | {item.get('goal_kicks_team_avg_at_A')}\n"
                f"{hbold('throwins_team_avg')} | {item.get('throwins_team_avg_at_H')} | {item.get('throwins_team_avg_at_A')}\n"
            )
        await message.answer(match_stats)
        
    await message.answer(f"Recherche des stats de l'equipe {away_b} en cours.... !")   
    file_away_stats = os.path.join("away_stats.json")
    with open(file_away_stats, encoding='utf-8') as file:
        data = orjson.loads(file.read())
        for item in data:
            match_stats_away = (
                f"{hbold('away_Team: ')} {item.get('Away_Team')}\n"
                f"{hbold('League Position: ')} {item.get('position')}\n"
                f"{hbold('stats:')} | {hbold('playing at Home')} | {hbold('playing at Away')}\n"
                f"{hbold('GF')} | {item.get('GF_at_H')} | {item.get('GF_at_A')}\n"
                f"{hbold('GA')} | {item.get('GA_at_H')} | {item.get('GA_at_A')}\n"
                f"{hbold('goals_mins')} | {item.get('goals_mins_at_H')} | {item.get('goals_minutes_at_A')}\n"
                f"{hbold('GC_mins')} | {item.get('GC_mins_at_H')} | {item.get('away_conceded_minutes_at_A')}\n"
                f"{hbold('goal_diff')} | {item.get('goal_diff_at_H')} | {item.get('goal_difference_at_A')}\n"
                f"{hbold('wins')} | {item.get('wins_at_H')} | {item.get('wins_at_A')}\n"
                f"{hbold('draws')} | {item.get('draws_at_H')} | {item.get('draws_at_A')}\n"
                f"{hbold('losses')} | {item.get('losses_at_H')} | {item.get('losses_at_A')}\n"
                f"{hbold('form')} | {item.get('form_at_H')} | {item.get('form_at_A')}\n"
                f"{hbold('CS')} | {item.get('CS_at_H')} | {item.get('CS_A')}\n"
                f"{hbold('ScoredAVG')} | {item.get('ScoredAVG_H')} | {item.get('ScoredAVG_A')}\n"
                f"{hbold('Conceded_AVG')} | {item.get('Conceded_AVG_H')} | {item.get('GA_AVG_A')}\n"
                f"{hbold('firstGoalScored')} | {item.get('firstGoalScored_at_H')} | {item.get('firstGoalScored_at_A')}\n"
                f"{hbold('FTS')} | {item.get('FTS_at_H')} | {item.get('FTS_at_A')}\n"
                f"{hbold('FTS_HT')} | {item.get('FTS_HT_at_H')} | {item.get('FTS_HT_at_A')}\n"
                f"{hbold('PPG')} | {item.get('PPG_at_H')} | {item.get('PPG_at_A')}\n"
                f"{hbold('leadingAtHT')} | {item.get('leadingAtHT_at_H')} | {item.get('leadingAtHT_at_A')}\n"
                f"{hbold('drawingAtHT')} | {item.get('drawingAtHT_at_H')} | {item.get('drawingAtHT_at_A')}\n"
                f"{hbold('trailingAtHT')} | {item.get('trailingAtHT_at_H')} | {item.get('trailingAtHT_at_A')}\n"
                f"{hbold('GS_HT')} | {item.get('GS_HT_at_H')} | {item.get('GF_HT_at_A')}\n"
                f"{hbold('GA_HT')} | {item.get('GC_HT_at_H')} | {item.get('GA_HT_at_A')}\n"
                f"{hbold('CS_HT')} | {item.get('CS_HT_at_H')} | {item.get('CS_HT_at_A')}\n"
                f"{hbold('GoalDiffHT')} | {item.get('GoalDiffHT_at_H')} | {item.get('GD_HT_at_A')}\n"
                f"{hbold('shotsTotal')} | {item.get('shotsTotal_at_H')} | {item.get('shotsTotal_at_A')}\n"
                f"{hbold('shotsAVG')} | {item.get('shotsAVG_at_H')} | {item.get('shotsAVG_at_A')}\n"
                f"{hbold('SoT_Total')} | {item.get('SoT_Total_at_H')} | {item.get('SoT_Total_at_A')}\n"
                f"{hbold('shotsOffTargetTotal')} | {item.get('shotsOffTargetTotal_at_H')} | {item.get('shotsOffTargetTotal_at_A')}\n"
                f"{hbold('SoT_AVG')} | {item.get('SoT_AVG_at_H')} | {item.get('SoT_AVG_at_A')}\n"
                f"{hbold('PossAVG')} | {item.get('PossAVG_at_H')} | {item.get('PossAVG_at_A')}\n"
                f"{hbold('attacks_avg')} | {item.get('attacks_avg_at_H')} | {item.get('attacks_avg_at_A')}\n"
                f"{hbold('dangerous_attacks_avg')} | {item.get('dangerous_attacks_avg_at_H')} | {item.get('dangerous_attacks_avg_at_A')}\n"
                f"{hbold('xg_for_avg')} | {item.get('xg_for_avg_at_H')} | {item.get('xg_for_avg_at_A')}\n"
                f"{hbold('xg_against_avg')} | {item.get('xg_against_avg_at_H')} | {item.get('xg_against_avg_at_A')}\n"
                f"{hbold('foulsAVG')} | {item.get('foulsAVG_at_H')} | {item.get('foulsAVG_at_A')}\n"
                f"{hbold('offsidesAVG')} | {item.get('offsidesAVG_at_H')} | {item.get('offsidesAVG_at_A')}\n"
                f"{hbold('goal_kicks_team_avg')} | {item.get('goal_kicks_team_avg_at_H')} | {item.get('goal_kicks_team_avg_at_A')}\n"
                f"{hbold('throwins_team_avg')} | {item.get('throwins_team_avg_at_H')} | {item.get('throwins_team_avg_at_A')}\n"
            )
        await message.answer(match_stats_away)
            


def read_file_content(file_path, prompt):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        response = call_gpt_api(prompt + content)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return ""


async def start(message: types.Message):
    message.answer("Salut je m'appel lucien et je suis ici pour t'aider a mieux analyser tes match avant de miser 😊😊😊.")


async def handle_home_stats(message: types.Message):
    try:
        file_path = "home_stats.csv"
        prompt = f"Act like a proffessionnal betting expert, analyze the home team’s general performance, goal performance, goal timing performance in the first and second half, defensive performance, halftime performance, shots and possession, and advanced stats when they play at home. Compare it to their away games. Based on your analysis, provide a detailed analysis of their likelihood trends when playing at home. Be brief and serious."
        response = read_file_content(file_path, prompt)
        user_data = await storage.get_data(user=message.from_user.id)
        user_data["home_step_1"] = response
        await storage.set_data(user=message.from_user.id, data=user_data)
        
        await message.answer(response)
    except Exception as e:
        print(f"Error: {e}")


async def handle_away_stats(message: types.Message):
    try:
        file_path = "away_stats.csv"

        prompt = f"Act like a proffessionnal betting expert, analyze the away team’s general performance, goal performance, goal timing performance in the first and second half, defensive performance, halftime performance, shots and possession, and advanced stats when they play at away. Compare it to their home games. Based on your analysis, provide a detailed analysis of their likelihood trends when playing at away. Be brief and serious."
        response = read_file_content(file_path, prompt)

        user_data = await storage.get_data(user=message.from_user.id)
        user_data["home_step_3"] = response
        await storage.set_data(user=message.from_user.id, data=user_data)
        

        await message.answer(response)
    except Exception as e:
        print(f"Error: {e}")


async def handle_analyze(message: types.Message):
    try:
        user_data = await storage.get_data(user=message.from_user.id)
        home_step_1 = user_data.get("home_step_1")
        home_step_2 = call_gpt_api(
            home_step_1
        ).strip()
        user_data["home_step_2"] = home_step_2

        home_step_3 = user_data.get("home_step_3")
        home_step_4 = call_gpt_api(
            home_step_3
        ).strip()
        user_data["home_step_4"] = home_step_4

        await storage.set_data(user=message.from_user.id, data=user_data)
        folder_path = "file_store"
        file_away_stats = os.path.join(folder_path, "away_stats.json")
        with open(file_away_stats, encoding='utf-8') as file:
            data = orjson.loads(file.read())
            Away = data[0]['Away_Team']
        file_home_stats = os.path.join(folder_path, "home_stats.json")
        with open(file_home_stats, encoding='utf-8') as file:
            data = orjson.loads(file.read())
            Home = data[0]['Home_Team']

        
        result_message = call_gpt_api(
        f"Now listen to me: Ignore additional missing stats. Just do what i need with provided summaries : Here is {Home} stats summary: {home_step_2}. Here is {Away} stats summary: {home_step_4}.Act like a professional betting analyst and Predict the likehood HT scores, SH scores and FT scores.",
        ).strip()
        
        # result_message = call_gpt_api(
        # f"Avoid any kind of reasons like it's difficult, because of missing stats or anything that you cannot give accurate results.now listen to me, Predict the outcome of {Home} against {Away}. Ignore additional missing stats. Just do what i need with provided summaries : Here is {Home} stats summary: {home_step_2}. Here is {Away} stats summary: {home_step_4}.Act like a professional betting analyst and Predict the likehood HT scores, SH scores and FT scores. Your answer should be in French",
        # ).strip()
        
        
        
        
        
        await message.answer(result_message)
    except Exception as e:
        print(f"Error: {e}")


async def help(message: types.Message):
    help_message = "Welcome to the betting analysis bot!\n\n"
    help_message += "Here's how you can use this bot:\n"
    help_message += "- Click the button 'Home Stats' to analyze the home team's statistics when they play at home.\n"
    help_message += "- Click the button 'Away Stats' to analyze the away team's statistics when they play away.\n"
    help_message += "- Click the button 'Analyze' to generate an analysis and summary of the home and away team trends.\n"
    help_message += "Note: Make sure to click the buttons in the correct order for accurate results.\n"
    help_message += "Enjoy your analysis!\n"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Home Stats"))
    keyboard.add(types.KeyboardButton("Away Stats"))
    keyboard.add(types.KeyboardButton("Analyze"))
    await message.answer(help_message, reply_markup=keyboard)


def call_gpt_api(prompt):
    try:
        openai.api_key='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'
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            temperature=0.0,
            messages=[
                {"role": "system", "content": "Act like a pro betting tipster expert in analyzing team statistics and providing accurate summarized analysys. Use clear and concise language. Be specific and provide details. Avoid asking questions. Avoid Reasons, Warnings and Notes"},
                {"role": "user", "content": prompt}
            ],#Avoid asking who their opponent is or the home team. Avoid saying: it is difficult to make a precise forecast
            #{"role": "system", "content": "start chat by: Hey c'est lucien, et je suis la pour t'aider. alors commençons."},
        )
        message = response.choices[0].message.content.strip()
        return message
    except Exception as e:
        print(f"Error: {e}")
        return ""



def main():
    executor.start_polling(dp)


if __name__ == "__main__":
    main()
