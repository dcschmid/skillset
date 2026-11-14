#!/usr/bin/env python3
"""Fixture: deeply nested branching (complexity hotspot target)."""


def classify(order, user, stock, cfg):
    total = 0
    for item in order["items"]:
        if item["kind"] == "book":
            if user["tier"] == "gold":
                if stock[item["sku"]] > 0:
                    if cfg["tax"] == "eu":
                        if item["price"] > 10:
                            total += item["price"] * 0.9
                        else:
                            total += item["price"]
                    else:
                        total += item["price"]
                else:
                    total += 0
            else:
                total += item["price"]
    return total
