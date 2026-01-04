from scrapper.mmt import scrap_extract as mmt
from scrapper.ixigo import scrap_extract as ixigo
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