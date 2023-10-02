from django.shortcuts import render, redirect

from .forms import CustomerForm


def index(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('order')
    else:
        form = CustomerForm()

    return render(request, 'index.html', {'form': form})
