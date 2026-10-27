import time
import ccxt
import json
import os
from datetime import datetime

POSITIONS_FILE = "open_positions.json"


def save_position_open_time(symbol):
    data = {}

    if os.path.exists(POSITIONS_FILE):
        try:
            with open(POSITIONS_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            print("Could not read positions file; refusing to overwrite it.")
            return False

    data[symbol] = datetime.now().isoformat()

    temp_file = POSITIONS_FILE + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(data, f, indent=2)

    os.replace(temp_file, POSITIONS_FILE)
    return True


def check_flip_after_24h():
    if not os.path.exists(POSITIONS_FILE):
        return

    try:
        with open(POSITIONS_FILE, "r") as f:
            data = json.load(f)

        positions = exchange.fetch_positions()

        for pos in positions:
            symbol = pos.get("symbol")
            contracts = pos.get("contracts") or 0

            if not symbol or symbol not in data:
                continue

            if contracts <= 0 or pos.get("side") != "short":
                continue

            open_time = datetime.fromisoformat(data[symbol])
            hours_open = (
                datetime.now() - open_time
            ).total_seconds() / 3600

            if hours_open < 24:
                continue

            amount = abs(contracts)

            print(f"{symbol}: short open {hours_open:.1f} hours")

            # Close the short in one-way mode.
            close_order = exchange.create_order(
                symbol,
                "market",
                "buy",
                amount,
                None,
                {"reduceOnly": True}
            )

            print("Close order submitted:", close_order.get("id"))

            # Do not assume the order has closed the position.
            time.sleep(2)
            updated_positions = exchange.fetch_positions([symbol])

            remaining_short = any(
                p.get("symbol") == symbol
                and p.get("side") == "short"
                and abs(p.get("contracts") or 0) > 0
                for p in updated_positions
            )

            if remaining_short:
                print(f"{symbol}: short still open; NOT opening long.")
                continue

            # Open a long only after confirming the short is closed.
            exchange.create_market_buy_order(symbol, amount)

            print(f"{symbol}: long order submitted.")

            del data[symbol]
            with open(POSITIONS_FILE, "w") as f:
                json.dump(data, f, indent=2)

    except Exception as e:
        print(f"Flip check error: {e}")
