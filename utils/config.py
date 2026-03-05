from scrapper.mmt import scrap_extract as mmt
from scrapper.ixigo import scrap_extract as ixigo
from scrapper.cleartrip import scrap_extract as cleartrip
SCRAPPER_REGISTRY = {
            "mmt": {
            "func": mmt.execute,
                "dateFormat": "%d/%m/%Y"
            },
            "ixigo": {
            "func": ixigo.execute,
                "dateFormat": "%d%m%Y"
            },
            # "expedia": {
            #     "func": scrap_extract.execute,
            #     "dateFormat": "%d/%m/%Y"
            # }
        }

INSTANT_SCRAPPER_REGISTRY = {
    "cleartrip": {
        "func": cleartrip.execute,
        "dateFormat": "%d/%m/%Y"
    }
}