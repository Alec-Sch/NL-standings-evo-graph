from dataclasses import dataclass, fields

@dataclass
class Game(object):
    awayTeamResult: str
    homeTeamResult: str
    awayTeamShortName: str
    homeTeamShortName: str
    status: str
    isOvertime: bool
    isExhibition: bool

    # This is to accept keyword args that aren't a defined field in the dataclass
    # a.k.a fields that aren't useful in the code
    def __init__(self, **kwargs):
        for f in fields(Game):
            setattr(self, f.name, kwargs.get(f.name))


@dataclass
class Team(object):
    shortName: str

    def __init__(self, **kwargs):
        for f in fields(Team):
            setattr(self, f.name, kwargs.get(f.name))