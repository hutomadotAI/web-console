from django.shortcuts import render


def handler400(request, exception):
    return render(request, '400.html', locals(), status=400)


def handler403(request, exception):
    return render(request, '403.html', locals(), status=403)


def handler403_csrf(request, reason):
    return render(request, '403_csrf.html', locals(), status=403)


def handler404(request, exception):
    return render(request, '404.html', locals(), status=404)


def handler500(request):
    return render(request, '500.html', locals(), status=500)
