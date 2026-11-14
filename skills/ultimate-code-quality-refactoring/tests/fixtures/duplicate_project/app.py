#!/usr/bin/env python3
"""Fixture: duplicated validation logic in two modules (clone detection target)."""


def validate_user_a(payload):
    errors = []
    if not payload.get("email"):
        errors.append("email required")
    if not payload.get("name"):
        errors.append("name required")
    if len(payload.get("tags", [])) > 10:
        errors.append("too many tags")
    return errors


def validate_user_b(payload):
    errors = []
    if not payload.get("email"):
        errors.append("email required")
    if not payload.get("name"):
        errors.append("name required")
    if len(payload.get("tags", [])) > 10:
        errors.append("too many tags")
    return errors
