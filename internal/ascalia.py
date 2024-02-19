import logging
import json
import os
import requests

PROD_URL = ""
PROD_TOKEN = ""
DEV_URL = "https://app-dev.ascalia.io/api/v1/"
DEV_TOKEN = "6a115b704d349c0075e41b4fb0d12b5368f79a44"


def handle_return(r, ok_status, prod, api_url, data=None):
    """
    Processes the return stuff. Returns TRUE if all good.
    :param r:
    :param ok_status:
    :param prod:
    :param api_url:
    :return: True if all ok, False otherwise
    """
    if r.status_code != ok_status:
        body = str(r.content)
        logging.error(
            f"Sent request with ERROR, prod:{prod} request URL: {api_url}, result:{r.status_code}, output/error.html. Response: {body[:300]} "
        )
        if not os.path.exists("output"):
            os.makedirs("output")
        with open("output/error.html", "w") as outfile:
            outfile.write(body)
            outfile.write(json.dumps(data if data else {}))
        return False
    else:
        logging.debug(f"Success {api_url}")
        return True


def create_order_items(group, items, prod=False, update=False):
    api_url = (PROD_URL if prod else DEV_URL) + "orders/order_items/"
    headers = {
        "Authorization": f"Token {PROD_TOKEN if prod else DEV_TOKEN}",
        "Content-Type": "application/json",
    }

    for item in items:
        item["order_group"] = group["id"]
        item["order"] = group["order"]
        r = requests.post(api_url, headers=headers, data=json.dumps(item))
        if r.status_code != 201:
            logging.error(
                f"Sent order with ERROR, prod:{prod} request URL: {api_url}, result:{r.status_code} , saving data to output/.json {item} and error to output/error.html"
            )
            with open("output/error.html", "w") as outfile:
                outfile.write(str(r.content))
            with open("output/last_item_error_request.json", "w") as outfile:
                outfile.write(json.dumps(group))
            break
        # else:
        #     logging.info(
        #         f"Sent ITEM with SUCCESS, prod:{prod} ORDER:  result:{r.status_code} {r.content}")


def create_order_group(real_order, group, prod=False):
    api_url = (PROD_URL if prod else DEV_URL) + "orders/order_groups/"
    headers = {
        "Authorization": f"Token {PROD_TOKEN if prod else DEV_TOKEN}",
        "Content-Type": "application/json",
    }

    group["order"] = real_order["id"]

    r = requests.post(api_url, headers=headers, data=json.dumps(group))

    if r.status_code == 201:
        group_response = json.loads(r.content)
        logging.debug(
            f"Sent order GROUP with SUCCESS, prod:{prod} ORDER: {group_response['id']} result:{r.status_code} {r.content}"
        )
        create_order_items(group_response, group["items"], prod)
    else:
        logging.warning(
            f"Sent order with ERROR, prod:{prod} request URL: {api_url}, result:{r.status_code} {r.content}, saving data to output/.json"
        )
        with open("output/last_order_error.json", "w") as outfile:
            outfile.write(json.dumps(group))


def create_order(order, prod=False):
    """
    Creates a new order in the system, then it creates the order_groups.

    :param order:
    :param prod:
    :return:
    """
    api_url = (PROD_URL if prod else DEV_URL) + "orders/orders/?expand=groups,items"
    headers = {
        "Authorization": f"Token {PROD_TOKEN if prod else DEV_TOKEN}",
        "Content-Type": "application/json",
    }

    data = order
    ret = requests.post(api_url, headers=headers, data=json.dumps(data))

    if handle_return(ret, 201, prod, api_url):
        order_response = json.loads(ret.content)
        for group in data["groups"]:
            create_order_group(order_response, group, prod)
        return order_response
    elif (
        ret.status_code == 400
        and "external_id" in ret.json()
        and "already exists" in ret.json()["external_id"]
    ):
        logging.warning(f'Order {order["external_id"]} already exists')
        return None
