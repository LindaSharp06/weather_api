import logging

from django.http import JsonResponse
from django.shortcuts import render

from .exchange_rate import get_exchange_rate, save_to_db, get_stored_history

logger = logging.getLogger(__name__)


def get_exchange_rate_view(request):
    if request.method not in ("GET", "POST"):
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = get_exchange_rate()
        if data is None:
            return JsonResponse({"error": "Failed to fetch exchange rate"}, status=502)
        saved, save_error = True, None
        try:
            save_to_db(data)
        except Exception as e:
            logger.exception("Failed to store exchange rate in database")
            saved, save_error = False, str(e)
        out = {**data, "saved": saved}
        if save_error:
            out["save_error"] = save_error
        return JsonResponse(out)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def dashboard_view(request):
    try:
        history = get_stored_history(limit=50)
        count = len(history)
    except Exception:
        history, count = [], 0
    resp = render(request, "api_integration/dashboard.html", {"history": history, "count": count})
    resp["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return resp


def exchange_history_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        limit = min(max(int(request.GET.get("limit", 50)), 1), 200)
    except (TypeError, ValueError):
        limit = 50
    try:
        data = get_stored_history(limit=limit)
        return JsonResponse({"count": len(data), "data": data})
    except Exception as e:
        logger.exception("Failed to load stored history")
        return JsonResponse({"error": str(e)}, status=500)