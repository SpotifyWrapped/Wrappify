from django.shortcuts import render

def loginPage(request):
    return render(request, "spotify/login.html")