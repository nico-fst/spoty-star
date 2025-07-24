import os
from flask import Flask, redirect, request, session, url_for, jsonify, make_response
from functools import wraps
from datetime import datetime
import calendar
from typing import List

from .app_types import FavEntry, Track, List
from .exceptions import LoggedOutError

IS_DEV = os.getenv("IS_DEV", "false").lower() == "true"


def ensure_domain(url: str) -> str:
    print(IS_DEV, url)
    if IS_DEV and url:
        return f"http://localhost:5173{url}"
    return url


def token_required(f):
    @wraps(f)
    def decorated_f(*args, **kwargs):
        if not "access_token" in session:
            if request.path.startswith("/api/"):
                raise LoggedOutError()
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_f


def date_to_decade(date: str) -> str:
    """macht aus YYYY-MM-DD die auf Decade abgerundetes YYYY (e.g. 1974 -> 1970)"""
    year = date.split("-")[0]
    return str(int(year) // 10 * 10)


def str_to_datetime(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def iso8601_to_datetime(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")


def get_end_of_month(year: str, month: str) -> str:
    month_str = month.zfill(2)
    last_day = calendar.monthrange(int(year), int(month_str))[1]
    return str(last_day).zfill(2)
