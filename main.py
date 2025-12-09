import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import List

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import numpy as np
import requests
import urllib3
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

URL_TEAMS = "https://www.nationalleague.ch/api/teams?lang=fr-CH"
URL_GAMES = "https://www.nationalleague.ch/api/games?lang=fr-CH"

# Tested those colors for the lines in the plot, but the reds and blue are too close to each other
# Edit those colors at will, find where the streak is plotted (ax.plot(...)) and add the argument : c=COLOR[team] where team is the team's shortName
COLOR = {
    "GSHC": "#6E0B14",
    "HCD": "#FFDD00",
    "HCA": "#FFCC00",
    "HCAP": "#202c59",
    "SCB": "#e30613",
    "EHCB": "#d11216",
    "FRI": "#121516",
    "EHCK": "#324b9b",
    "SCL": "#e30613",
    "LHC": "#e40f29",
    "HCL": "#000000",
    "SCRJ": "#03326d",
    "EVZ": "#0f6ca9",
    "ZSC": "#0092cc"
}


fig, ax = plt.subplots(figsize=(2560/96, 1335/96)) # 2K resolution with a dpi of 96

teams_json = requests.get(URL_TEAMS).json()
games_json = requests.get(URL_GAMES).json()
games : List[Game] = [Game(**x) for x in games_json]
teams : List[Team] = [Team(**x) for x in teams_json]

teams_short = [team.shortName for team in teams]
finished = [game for game in games if game.status == "finished" and game.isExhibition == False] # only keep finished games from the regular season

colors = mpl.colormaps['tab20b'].colors

for i, team in enumerate(teams_short):
    completed_games = [game for game in finished if game.homeTeamShortName == team or game.awayTeamShortName == team] # filter the games for a given team

    streak = [0]
    cum_streak = 0 # cumulative of streak, it is what is inputed into the streak at each new game

    for game in completed_games:
        # For each game, we can easily find who between the home team and away team won
        # But we also need to determine if the team we're focusing on was at home or away

        is_away = game.awayTeamShortName == team

        team_score = game.awayTeamResult if is_away else game.homeTeamResult
        opp_score = game.homeTeamResult if is_away else game.awayTeamResult

        if team_score > opp_score:
            if game.isOvertime == False:
                cum_streak += 1    
            else:
                cum_streak += 0.5
        else:
            if game.isOvertime == False:
                cum_streak -= 1    
            else:
                cum_streak -= 0.5
        streak.append(cum_streak)
    
    logo_path = os.path.join("assets", f"{team}.png")
    logo_img = plt.imread(logo_path)

    imagebox = OffsetImage(logo_img, zoom=0.3)
    imagebox.image.axes = ax
    img_x, img_y = len(streak)-1, streak[-1] # coordinates where to place the image

    ab = AnnotationBbox(
        imagebox,
        (img_x, img_y),
        xybox=(10, 0), # shift by 10px to the right
        xycoords='data',
        boxcoords="offset points",
        frameon=False
    )

    ax.plot(streak, lw=5, label=team, color=colors[i], zorder=3)
    ax.add_artist(ab)

prop = fm.FontProperties(fname=font_file_path)
ax.text(1, 16.5, "NATIONAL LEAGUE 2025-26", fontsize=36, fontweight='bold', fontproperties=prop)

ax.set_ylabel("Wins", fontsize=20, fontproperties=prop)
ax.set_xlabel("Games", fontsize=20, fontproperties=prop)
ax.set_xlim(left=0)
ax.legend(loc='lower left')
ax.set_facecolor("#EEEEEE")
ax.yaxis.set_major_locator(plt.MultipleLocator(2))
ax.xaxis.set_major_locator(plt.MultipleLocator(2))
plt.grid(zorder=2)
plt.savefig(os.path.join("OUT", f"standings-{datetime.today().strftime('%Y-%m-%d')}.png"))
plt.show()