import html
import logging

# Set up logging
logger = logging.getLogger(__name__)


def parse_json_to_order(data):
    order = {"order_id": "", "groups": []}

    for item in data:
        try:
            if "Zaglavlje" in item:
                header = item["Zaglavlje"][0]
                sastavnica = html.unescape(header["sastavnica"])
                order_id_suffix = sastavnica[-5:]
                order["order_id"] = f'{header["oznaka"]}-{order_id_suffix}'
                order["company"] = header["kupacID"]
                logger.info(
                    f"Order header parsed: {order['order_id']}, Company: {order['company']}"
                )
            else:
                group = {
                    "name": item.get("artiklNaziv", "Unknown"),
                    "material_code": item.get("code", "Unknown"),
                    "items": [],
                }
                for plate in item.get("ploce", []):
                    item_detail = {
                        "item_num": plate["id"],
                        "name": f"{plate['sirinaMM']}x{plate['visinaMM']} - {group['material_code']}"
                        + (f" - {plate['napomena']}" if plate.get("napomena") else ""),
                        "quantity": plate["komada"],
                        "unit_code": "kom",
                    }
                    group["items"].append(item_detail)
                order["groups"].append(group)
                logger.info(
                    f"Group added: {group['name']} with {len(group['items'])} items"
                )
        except KeyError as e:
            logger.error(f"Missing expected key in JSON data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while parsing JSON: {e}")

    return order
