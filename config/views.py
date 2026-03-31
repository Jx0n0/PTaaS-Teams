from django.shortcuts import render


def root_landing(request):
    return render(request, 'console.html')
