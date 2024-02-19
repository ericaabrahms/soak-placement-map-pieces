import csv
from typing import List
from enum import Enum

def bool_fetcher(row):
    def bool_is_set(key):
        if row[key].strip() == '': # empty
            return False
        if row[key].lower() == 'no':
            return False
        return True
    return bool_is_set

class SoundZone(Enum):
    SZ_1 = 'SZ 1'
    SZ_2 = 'SZ 2'
    SZ_3 = 'SZ 3'
    NA   = '#N/A'

class CampType(Enum):
    WORK_SUPPORT = 'Work Support Camp'
    ART_SUPPORT = 'Art Support Camp'
    THEME_CAMP = 'Theme Camp'

    @classmethod
    def from_string(cls, s: str) -> 'CampType':
        if s == 'Work Support Camp':
            return CampType.WORK_SUPPORT
        if s == 'Art Support Camp':
            return CampType.ART_SUPPORT
        return CampType.THEME_CAMP

#  TODO: Deal with time sections getting smashed together
class InteractivityTime(Enum):
    ART_SUPPORT = 'Art Support Camp'
    WORK_SUPPORT = 'Work Support Camp'
    MORNING = 'Morning'
    AFTERNOON = 'Afternoon'
    LATE_AFTERNOON = 'Late Afternoon'
    EVENING = 'Evening'
    LATE_NIGHT = 'Late Night'
    EMPTY = ''
    # TODO: Blank string?

class SoundSize(Enum):
    SMALL = 1
    MEDIUM = 2
    EMPTY = 3

class Kids(Enum):
    KIDS = 'Kids'
    KIDS_PLUS = 'Kids+'
    NONE = 'N/A'

    @classmethod
    def from_string(cls, s: str) -> 'Kids':
        if s == 'Kids':
            return Kids.KIDS
        if s == 'Kids+':
            return Kids.KIDS_PLUS
        return Kids.NONE

class Food(Enum):
    FOOD = 'Food'
    FOOD_PLUS = 'Food+'
    NONE = 'N/A'

    @classmethod
    def from_string(cls, s: str) -> 'Food':
        if s == 'Food':
            return Food.FOOD
        if s == 'Food+':
            return Food.FOOD_PLUS
        return Food.NONE



class CampInfo(object):
    def __init__(
            self, width: int, height: int, name: str, camp_type: CampType,
            sound_zone: SoundZone, interactivity_time: InteractivityTime,
            sound_size: SoundSize, neighborhood_preference: List[str],
            coffee: bool, tea: bool, food: Food, fire: bool, fire_circle: bool, kids: Kids,
            bar: bool, ada: bool, xxx: bool, trees: bool, uneven_ground: bool,
            rv_count: int):
        self.width = width
        self.height = height
        self.name = name
        self.camp_type = camp_type
        self.sound_zone = sound_zone
        self.interactivity_time = interactivity_time
        self.sound_size = sound_size
        self.neighborhood_preference = neighborhood_preference
        self.coffee = coffee
        self.tea = tea
        self.food = food
        self.fire = fire
        self.fire_circle = fire_circle
        self.kids = kids
        self.bar = bar
        self.ada = ada
        self.xxx = xxx
        self.trees = trees
        self.uneven_ground = uneven_ground
        self.rv_count = rv_count

    def __repr__(self):
        return f'<CampInfo: {self.name}>'

def read_csv():
    with open('./placement-temp.csv') as f:
        reader = csv.DictReader(f)
        camps = []
        skids = set()
        sfood = set()
        sug = set()
        for row in reader:
            bool_get = bool_fetcher(row)

            try:
                rv_count = int(row['RVs'])
            except ValueError:
                rv_count = 0
            camp_type = row['Camp Type']  # e.g.  "Theme Camp"
            interactivity_time = row['Interactivity Time/Name Highlight Color']
            sound_size = row['Sound'] # how big their soundsystem is: small, medium, nothing
            sound_zone = row['Sound Zone'] # e.g. "SZ 2"
            kids = row['Kids'] # Kids, Kids+
            skids.add(kids)
            food = row['Food'] # Food, Food+
            sfood.add(food)
            ug = row['Uneven Ground Data']
            sug.add(ug)

            camps.append(CampInfo(
                width=int(row['Frontage']),
                height=int(row['Depth']),
                name=row[' '],
                camp_type=camp_type, sound_zone=sound_zone, interactivity_time=interactivity_time, sound_size=sound_size,
                neighborhood_preference=row['neighborhood'].strip().split(' '),
                coffee=bool_get('Coffee'),tea=bool_get('Tea'),fire=bool_get('Fire'), fire_circle=bool_get('Fire Circle'),
                food=Food.from_string(row['Food']),
                kids=Kids.from_string(row['Kids']),
                bar=bool_get('Bar'), ada=bool_get('ADA'), xxx=bool_get('XXX'),
                uneven_ground=bool_get('Uneven Ground Data'), trees=bool_get('Trees'),
                rv_count=rv_count
            ))
    print("Kids: ", skids)
    print("Food: ", sfood)
    print("UG: ", sug)

    return camps
