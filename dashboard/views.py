from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_dashboard_stats


@login_required
def index(request):
    stats = get_dashboard_stats(request.user)
    return render(request, "dashboard/index.html", {"stats": stats})