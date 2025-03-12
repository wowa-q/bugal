from django.shortcuts import render
from django.http import Http404
from .models import EUR
# Temporary data
META_TRANSACTION = {
    'tdate': '',
    'text': '',
    'status': '',
    'debitor': '',
    'verwendung': '',
    'konto': '',
    'value': '',
    'debitor_id': '',
    'mandats_ref': '',
    'customer_ref': '',
    'src_konto': '',
}

def create_transactions(text=''):
    context = META_TRANSACTION.copy()
    for key in context:
        context[key]='Test'
    context['text'] = text
    return context

def starting_page(request):

    try:
        eur_q = EUR.objects.all() # das ist nur ein query
        if not eur_q.exists():  # Wenn das Ergebnis leer ist
            raise Http404()
    except:
        raise Http404()
    
    return render(request, 'finapp/index.html', {"eur":eur_q})

def all_transactions(request):
    context = create_transactions()
    return render(request, 'finapp/transactions.html', context)

def transaction_detail(request, slug):    
    transaction = create_transactions(text=slug)
    print(transaction)
    return render(request, 'finapp/transaction-detail.html', transaction)