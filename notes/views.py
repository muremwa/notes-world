from django.shortcuts import render, redirect, reverse


def index(request):
    if request.user.is_authenticated:
        print(request.user.is_authenticated)
        return render(request, 'notes/index.html')
    else:
        print(request.user.is_authenticated)
        return redirect(reverse('base_account:account-index'))
