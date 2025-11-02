from django.http import HttpResponse
from django.shortcuts import render

def mon_views(request):
    return render(request, 'templates/index.html')