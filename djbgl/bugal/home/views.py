# from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, DeleteView, UpdateView, CreateView
from django.urls import reverse_lazy

from . import models


class BugalHomeView(ListView):
    template_name = 'home/home.html'
    model = models.Transaction
    context_object_name = 'transactions'

    def get_queryset(self):
        # Hier kannst du optional den Queryset anpassen
        return models.Transaction.objects.all()  # Gibt alle Transaktionen zurück

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['injectme'] = 'BASIC INJECTIONS'
        transactions = models.Transaction.objects.all()  # Holt alle Transaktionen
        return context

class TransactionListView(ListView):
    model = models.Transaction  # Das Modell, von dem du die Daten abrufen möchtest
    template_name = 'home.html'  # Dein Template
    context_object_name = 'transactions'  # Der Kontextname, der im Template verwendet wird

    def get_queryset(self):
        # Hier kannst du optional den Queryset anpassen
        return models.Transaction.objects.all()  # Gibt alle Transaktionen zurück
