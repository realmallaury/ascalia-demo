import html


def parse_json_to_order(data):
    order = {
        "groups": [],
    }

    for item in data:
        if "Zaglavlje" in item:
            zaglavlje = item["Zaglavlje"][0]
            sastavnica = html.unescape(zaglavlje["sastavnica"])
            id = sastavnica[-5:]

            order["order_id"] = zaglavlje["oznaka"] + "-" + id
            order["company"] = zaglavlje["kupacID"]

        else:
            group = {
                "name": item["artiklNaziv"],
                "material_code": item["code"],
                "items": [],
            }

            for i in item["ploce"]:
                item = {
                    "item_num": i["id"],
                    "name": f"{i['sirinaMM']}x{i['visinaMM']} - {group['material_code']}"
                    + (f" - {i['napomena']}" if i["napomena"] else ""),
                    "quantity": i["komada"],
                    "unit_code": "kom",
                }

                group["items"].append(item)

            order["groups"].append(group)

    return order
