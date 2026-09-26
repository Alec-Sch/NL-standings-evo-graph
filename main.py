import os
from datetime import datetime
from typing import List

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import requests
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from models.models import Game, Team

params = {'legend.fontsize': 'x-large',
         'axes.labelsize': 'x-large',
         'axes.labelweight': 'bold',
         'axes.titlesize':'xx-large',
         'axes.titleweight': 'bold',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)


if not os.path.exists("Goldman-Regular.ttf"):
    font_github_url = "https://github.com/google/fonts/blob/main/ofl/goldman/Goldman-Regular.ttf?raw=true"

    a = requests.get(font_github_url, verify=True)
    with open("Goldman-Regular.ttf", "wb") as f:
        f.write(a.content)

font_file_path = "Goldman-Regular.ttf"

if not os.path.exists("OUT"):
    os.mkdir("OUT")

URL_TEAMS = "https://www.nationalleague.ch/api/teams?lang=fr-CH"
URL_GAMES = "https://www.nationalleague.ch/api/games?lang=fr-CH"

fig, ax = plt.subplots(figsize=(2560/96, 1335/96)) # 2K resolution with a dpi of 96

teams_json = requests.get(URL_TEAMS).json()
games_json = requests.get(URL_GAMES).json()
games : List[Game] = [Game(**x) for x in games_json]
teams : List[Team] = [Team(**x) for x in teams_json]

teams_short = [team.shortName for team in teams]
finished = [game for game in games if (game.status == "finished" or game.status == "end") and game.isExhibition == False] # only keep finished games from the regular season

colors = mpl.colormaps['tab20b'].colors

if len(finished) == 0:
    print("Season did not start yet")
    exit()

first_game_date = finished[0].date # take the first game to determine the year of the season
year = datetime.fromisoformat(first_game_date).year
year_str =f"{year}-{year%100+1}" # This code 

pts_final = []
max_height = 0

for i, team in enumerate(teams_short):
    completed_games = [game for game in finished if game.homeTeamShortName == team or game.awayTeamShortName == team] # filter the games for a given team

    streak = [0.0]
    cum_streak = 0.0 # cumulative of streak, it is what is inputed into the streak at each new game

    for game_number, game in enumerate(completed_games):
        if game_number >= 52:
            # ignore post season
            break

        # For each game, we can easily find who between the home team and away team won
        # But we also need to determine if the team we're focusing on was at home or away
        is_away = game.awayTeamShortName == team

        team_score = game.awayTeamResult if is_away else game.homeTeamResult
        opp_score = game.homeTeamResult if is_away else game.awayTeamResult

        if team_score > opp_score:
            if game.isOvertime == False:
                cum_streak += 1
            else:
                cum_streak += 1/3
        else:
            if game.isOvertime == True:
                cum_streak -= 1/3
            else:
                cum_streak -= 1
        streak.append(cum_streak)

    logo_path = os.path.join("assets", f"{team}.png")
    logo_img = plt.imread(logo_path)

    imagebox = OffsetImage(logo_img, zoom=0.3)
    imagebox.image.axes = ax

    img_x, img_y = len(streak)-1, round(streak[-1], 2) # coordinates where to place the image

    # store the height of the team with most points -- value used to plot the title
    if img_y > max_height:
        max_height = img_y 

    # In case of two teams being superposed, need to move to the right the next logos
    # We save the coordinates of each logo and compare how many are currently already drawn to
    # determine how many time to shift to the right
    
    app = pts_final.count((img_x, img_y))
    pts_final.append((img_x, img_y))

    ab = AnnotationBbox(
        imagebox,
        (img_x, img_y),
        xybox=(10+50*app, 0), # shift by 10px to the right and 50px to the right in case of multiple logos superposed
        xycoords='data',
        boxcoords="offset points",
        frameon=False
    )

    ax.plot(streak, lw=5, label=team, color=colors[i], zorder=2)
    ax.add_artist(ab)

prop = fm.FontProperties(fname=font_file_path)
ax.text(0.5, max_height-1, f"NATIONAL LEAGUE {year_str}", fontsize=36, fontweight='bold', fontproperties=prop)

ax.set_ylabel("Win ratio", fontsize=25, fontproperties=prop)
ax.set_xlabel("Games", fontsize=25, fontproperties=prop)
ax.set_xlim(left=0)
ax.legend(
    ncol=2,
    loc='lower left',
    fontsize=20,
)
ax.set_facecolor("#EEEEEE")
ax.yaxis.set_major_locator(plt.MultipleLocator(2))
ax.xaxis.set_major_locator(plt.MultipleLocator(2))
plt.grid(zorder=2)
plt.savefig(os.path.join("OUT", f"standings-{datetime.today().strftime('%Y-%m-%d')}.png"))