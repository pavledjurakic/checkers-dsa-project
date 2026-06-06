from enum import Enum
import random

class RelicType(Enum):
    TOKA_OD_CELIKA = "toka od celika"
    MESINA_RUJNOG_VINA = "mesina rujnog vina"
    TOPUZ = "topuz"
    SARAC = "sarac"
    TRI_TOVARA_BLAGA = "tri tovara blaga"

def relic_cycle():
    relics = [RelicType.TOKA_OD_CELIKA, RelicType.MESINA_RUJNOG_VINA, RelicType.TOPUZ, RelicType.SARAC, RelicType.TRI_TOVARA_BLAGA]
    random.shuffle(relics)
    while True:
        for relic in relics:
            yield relic

