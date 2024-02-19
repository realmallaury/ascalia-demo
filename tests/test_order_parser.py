from statistics import quantiles
from internal.order import parse_json_to_order
import yaml


def test_parse_json_to_order():
    json = """[
    {
        "Zaglavlje": [
            {
                "broj": 12,
                "oznaka": "0442-178",
                "sastavnica": "0001324232",
                "datum": "02.01.2024",
                "kupacID": 178,
                "kupac": "quot;JUG",
                "datumStampanja": "02.01.2024",
                "planDatIsp": "05.01.2024",
                "nacinIsporuke": "",
                "kaljenje": false, referentID: 37, poslano: "04.01.24 08:09:36"
            }
        ]
    },
    {
        "rowId": 1,
        "artikId": 9823,
        "code": "SA3T8ESG",
        "artiklNaziv": "staklo 8mm satinato, brušeno, kaljeno",
        "jedMjera": "m2",
        "kolicina": 1.18,
        "cijena": 653.07,
        "izoStaklo": true,
        "kaljenje": true,
        "ploce": [
            {
                "id": 1,
                "sirinaMM": 672,
                "visinaMM": 1690,
                "komada": 1,
                "povrsinaM2": 1.18,
                "opsegM": 44.72,
                "napomena": "",
            }
        ]
    }
]"""

    expected_order = {
        "order_id": "0442-178-24232",
        "company": 178,
        "groups": [
            {
                "name": "staklo 8mm satinato, brušeno, kaljeno",
                "material_code": "SA3T8ESG",
                "items": [
                    {
                        "item_num": 1,
                        "name": "672x1690 - SA3T8ESG",
                        "quantity": 1,
                        "unit_code": "kom",
                    },
                ],
            },
        ],
    }

    data = yaml.load(json, yaml.SafeLoader)
    assert parse_json_to_order(data) == expected_order
