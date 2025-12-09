import requests
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pylab as pylab
import os

params = {'legend.fontsize': 'x-large',
         'axes.labelsize': 'x-large',
         'axes.labelweight': 'bold',
         'axes.titlesize':'xx-large',
         'axes.titleweight': 'bold',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)


URL_TEAMS = "https://www.nationalleague.ch/api/teams?lang=fr-CH"
URL_GAMES = "https://www.nationalleague.ch/api/games?lang=fr-CH"

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


fig, ax = plt.subplots(figsize=(10, 6))


teams = requests.get(URL_TEAMS).json()
games = requests.get(URL_GAMES).json()

teams_short = [team["shortName"] for team in teams]
finished = [game for game in games if game["status"] == "finished" and game["isExhibition"] == False]

for team in teams_short:
    completed_games = [game for game in finished if game["homeTeamShortName"] == team or game["awayTeamShortName"] == team]

    streak = [0]
    cum_streak = 0

    for game in completed_games:
        is_away = game["awayTeamShortName"] == team

        team_score = game["awayTeamResult"] if is_away else game["homeTeamResult"]
        opp_score = game["homeTeamResult"] if is_away else game["awayTeamResult"]

        if team_score > opp_score:
            if game["isOvertime"] == False:
                cum_streak += 1    
            else:
                cum_streak += 0.5
        else:
            if game["isOvertime"] == False:
                cum_streak -= 1    
            else:
                cum_streak -= 0.5
        streak.append(cum_streak)
    
    logo_path = os.path.join("assets", f"{team}.png")
    logo_img = plt.imread(logo_path)

    imagebox = OffsetImage(logo_img, zoom=0.3)
    imagebox.image.axes = ax
    img_x, img_y = len(streak)-1, streak[-1]

    ab = AnnotationBbox(
        imagebox,
        (img_x, img_y),
        xybox=(10, 0),
        xycoords='data',
        boxcoords="offset points",
        frameon=False
    )

    ax.plot(streak, lw=3, label=team)
    ax.add_artist(ab)

ax.set_ylabel("Wins")
ax.set_xlabel("Games")
ax.set_xlim(left=0)
ax.legend(loc='upper left')
ax.set_facecolor("#EEEEEE")
plt.title("National League")
plt.grid()
plt.show()