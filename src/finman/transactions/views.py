import logging
import os

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from django.views.generic.edit import FormMixin

from .forms import (
    CategoryForm,
    FilterRuleForm,
    ImportForm,
    ManualCategoryForm,
    TransactionFilterForm,
    TransactionInfoForm,
    TransactionMetaForm,
)
from .models import (
    Category,
    FilterRule,
    ImportHistory,
    PredictionResult,
    Transaction,
    TransactionCategory,
    TransactionInfo,
    TransactionMeta,
)
from .services.categorization import apply_rules_to_all
from .services.filter_service import TransactionFilter
from .services.importer import cleanup_temp, import_csv, save_upload_to_temp
from .services.prediction import update_predictions

SORT_FIELDS = {'date', '-date', 'value', '-value', 'debitor', '-debitor', 'status', '-status'}

logger = logging.getLogger(__name__)


def dashboard(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    txs_this_month = Transaction.objects.filter(date__gte=month_start)
    income = txs_this_month.filter(value__gt=0).aggregate(total=Sum('value'))['total'] or 0
    expenses = txs_this_month.filter(value__lt=0).aggregate(total=Sum('value'))['total'] or 0
    balance = income + expenses

    top_expenses = (
        TransactionCategory.objects
        .filter(transaction__date__gte=month_start, transaction__value__lt=0)
        .values('category__name')
        .annotate(total=Sum('transaction__value'))
        .order_by('total')[:5]
    )

    upcoming = PredictionResult.objects.order_by('next_expected_date')[:10]
    last_imports = ImportHistory.objects.all()[:5]

    return render(request, 'transactions/dashboard.html', {
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'top_expenses': top_expenses,
        'upcoming': upcoming,
        'last_imports': last_imports,
    })


@method_decorator(never_cache, name='dispatch')
class ImportView(FormView):
    template_name = 'transactions/import.html'
    form_class = ImportForm

    def form_valid(self, form):
        filepath = None
        original_filename = None
        try:
            if self.request.FILES.get('file'):
                uploaded = self.request.FILES['file']
                original_filename = uploaded.name
                filepath = save_upload_to_temp(uploaded)
            else:
                filepath = form.cleaned_data['file_path']
                logger.info(f'ImportView: Using file path from form: {filepath}')
                if not os.path.exists(filepath):
                    messages.error(self.request, 'Datei nicht gefunden.')
                    return self.form_invalid(form)

            from .parsers.registry import get_parser
            logger.info(f'ImportView: Calling get_parser for {filepath}')
            parser = get_parser(filepath)
            logger.info(f'ImportView: Parser selected: {parser.__class__.__name__}')
            preview = parser.get_meta_info(filepath) if parser else None

            result = import_csv(filepath, original_filename=original_filename)
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        finally:
            cleanup_temp(filepath)

        context = self.get_context_data(form=form, result=result, preview=preview)
        return self.render_to_response(context)

    def form_invalid(self, form):
        messages.error(self.request, 'Import fehlgeschlagen. Bitte Eingaben prüfen.')
        return super().form_invalid(form)


def import_history(request):
    imports = ImportHistory.objects.all()
    return render(request, 'transactions/import_history.html', {'imports': imports})


@method_decorator(never_cache, name='dispatch')
class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        if self.request.GET:
            form = TransactionFilterForm(self.request.GET)
            if form.is_valid():
                self._filter_form = form
                self._cleaned = form.cleaned_data
            else:
                messages.error(self.request, 'Ungültige Filterangaben wurden ignoriert.')
                self._filter_form = TransactionFilterForm()
                self._cleaned = {}
        else:
            self._filter_form = TransactionFilterForm()
            self._cleaned = {}

        f = TransactionFilter()
        cd = self._cleaned
        start, end = cd.get('start'), cd.get('end')
        if start and end:
            f.by_date_range(start, end)
        f.by_debitor(cd.get('debitor') or '')
        category = cd.get('category')
        if category:
            f.by_category(category.pk)
        f.by_art(cd.get('art') or '')
        f.by_prioritaet(cd.get('prioritaet') or '')
        f.by_intervall(cd.get('intervall') or '')

        sort = self.request.GET.get('sort', '-date')
        if sort not in SORT_FIELDS:
            sort = '-date'
        self._sort = sort
        self._filtered_qs = f.apply().order_by(sort)
        return self._filtered_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cd = self._cleaned
        context['filter_form'] = self._filter_form
        context['sort'] = self._sort
        context['meta_form'] = TransactionMetaForm()
        context['total_sum'] = self.object_list.aggregate(
            total=Sum('value'),
        )['total'] or 0
        context['filters'] = {
            'start': str(cd['start']) if cd.get('start') else '',
            'end': str(cd['end']) if cd.get('end') else '',
            'debitor': cd.get('debitor') or '',
            'category': str(cd['category'].pk) if cd.get('category') else '',
            'art': cd.get('art') or '',
            'prioritaet': cd.get('prioritaet') or '',
            'intervall': cd.get('intervall') or '',
        }
        return context


@method_decorator(never_cache, name='dispatch')
class TransactionDetailView(DetailView, FormMixin):
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'tx'
    form_class = ManualCategoryForm
    info_form_class = TransactionInfoForm

    def get_success_url(self):
        return reverse('transaction_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.object.categories.select_related('category').all()
        context['meta'] = getattr(self.object, 'meta', None)
        context['info'] = getattr(self.object, 'info', None)
        if 'form' not in context:
            context['form'] = self.get_form()
        if 'info_form' not in context:
            context['info_form'] = self.info_form_class(instance=context.get('info'))
        if 'meta_form' not in context:
            meta = context.get('meta')
            context['meta_form'] = TransactionMetaForm(initial={
                'art': meta.art,
                'prioritaet': meta.prioritaet,
                'intervall': meta.intervall,
            } if meta else {})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST.get('form_type') == 'info':
            info = getattr(self.object, 'info', None)
            info_form = self.info_form_class(request.POST, instance=info)
            if info_form.is_valid():
                obj = info_form.save(commit=False)
                obj.transaction = self.object
                obj.save()
                messages.success(self.request, 'Info wurde gespeichert.')
                return redirect(self.get_success_url())
            return self.render_to_response(self.get_context_data(
                form=ManualCategoryForm(),
                info_form=info_form,
            ))
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        tc, created = TransactionCategory.objects.get_or_create(
            transaction=self.object,
            category=form.cleaned_data['category'],
            defaults={'assigned_by': 'manual'},
        )
        if created:
            messages.success(self.request, f"Kategorie '{tc.category}' wurde manuell zugewiesen.")
        else:
            messages.info(self.request, f"Kategorie '{tc.category}' war bereits zugewiesen.")
        return super().form_valid(form)


META_CLEAR_LABELS = {'art': 'Art', 'prioritaet': 'Priorität'}


def _redirect_back_to_list(request):
    next_url = request.POST.get('next') or ''
    if next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)
    return redirect('transaction_list')


@require_POST
def transaction_meta_save(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    form = TransactionMetaForm(request.POST)
    if not form.is_valid():
        messages.error(request, f'Ungültige Angaben für Transaktion #{pk}.')
        return _redirect_back_to_list(request)
    cd = form.cleaned_data
    meta, _ = TransactionMeta.objects.get_or_create(transaction=tx)
    meta.art = cd.get('art') or ''
    meta.prioritaet = cd.get('prioritaet') or ''
    meta.intervall = cd.get('intervall') or ''
    meta.save()
    if cd.get('category'):
        _, created = TransactionCategory.objects.get_or_create(
            transaction=tx,
            category=cd['category'],
            defaults={'assigned_by': 'manual'},
        )
        if created:
            messages.success(request, f"Kategorie '{cd['category']}' wurde zugewiesen.")
    messages.success(request, f'Transaktion #{tx.pk} wurde aktualisiert.')
    return _redirect_back_to_list(request)


@require_POST
def transaction_meta_clear(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    field = request.POST.get('field', '')
    if field not in META_CLEAR_LABELS:
        messages.error(request, 'Unbekanntes Feld.')
        return _redirect_back_to_list(request)
    meta = getattr(tx, 'meta', None)
    if meta is None:
        messages.info(request, 'Nichts zu entfernen.')
        return _redirect_back_to_list(request)
    setattr(meta, field, '')
    meta.save()
    messages.success(request, f'{META_CLEAR_LABELS[field]} wurde entfernt.')
    return _redirect_back_to_list(request)


@require_POST
def transaction_category_remove(request, pk, cat_pk):
    tx = get_object_or_404(Transaction, pk=pk)
    tc = (
        TransactionCategory.objects
        .filter(transaction=tx, category_id=cat_pk)
        .select_related('category')
        .first()
    )
    if tc:
        name = str(tc.category)
        tc.delete()
        messages.success(request, f"Kategorie '{name}' wurde entfernt.")
    return _redirect_back_to_list(request)


@method_decorator(never_cache, name='dispatch')
class CategoryListView(FormMixin, ListView):
    model = Category
    template_name = 'transactions/category_list.html'
    context_object_name = 'roots'
    form_class = CategoryForm

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_roots'] = self.get_queryset().count()
        context['total_categories'] = Category.objects.count()
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        cat = form.save()
        messages.success(self.request, f"Kategorie '{cat.name}' wurde erstellt.")
        return redirect(f"{reverse('category_list')}#cat-{cat.pk}")


@method_decorator(never_cache, name='dispatch')
class CategoryNewSubView(DetailView, FormMixin):
    model = Category
    template_name = 'transactions/category_form.html'
    context_object_name = 'root'
    form_class = CategoryForm

    def get_initial(self):
        return {'parent': self.get_object().pk}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fixed_parent'] = True
        if 'form' not in kwargs:
            context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        self.root_category = self.get_object()
        data = request.POST.copy()
        data['parent'] = str(self.root_category.pk)
        form = CategoryForm(data)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        cat = form.save(commit=False)
        cat.parent = self.root_category
        cat.save()
        messages.success(self.request, f"Kategorie '{cat.name}' wurde erstellt.")
        return redirect(f"{reverse('category_list')}#cat-{cat.pk}")

    def form_invalid(self, form):
        messages.error(self.request, 'Bitte Eingaben korrigieren.')
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(never_cache, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'transactions/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, f"Kategorie '{form.instance.name}' wurde aktualisiert.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Bitte Eingaben korrigieren.')
        return super().form_invalid(form)


@method_decorator(never_cache, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'transactions/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = self.object
        context['tx_count'] = TransactionCategory.objects.filter(category=cat).count()
        context['rule_count'] = FilterRule.objects.filter(category=cat).count()
        context['children_count'] = cat.subcategories.count()
        return context

    def form_valid(self, form):
        cat = self.object
        used_by_tx = TransactionCategory.objects.filter(category=cat).exists()
        used_by_rule = FilterRule.objects.filter(category=cat).exists()
        has_children = cat.subcategories.exists()

        if used_by_tx or used_by_rule or has_children:
            reasons = []
            if used_by_tx:
                reasons.append('wird von Transaktionen verwendet')
            if used_by_rule:
                reasons.append('wird von Filter-Regeln verwendet')
            if has_children:
                reasons.append('besitzt Sub-Kategorien')
            messages.error(
                self.request,
                f"Kategorie '{cat.name}' kann nicht gelöscht werden: {', '.join(reasons)}.",
            )
            return redirect(self.success_url)

        messages.success(self.request, f"Kategorie '{cat.name}' wurde gelöscht.")
        return super().form_valid(form)


@method_decorator(never_cache, name='dispatch')
class RuleListView(FormMixin, ListView):
    model = FilterRule
    template_name = 'transactions/rule_list.html'
    context_object_name = 'rules'
    form_class = FilterRuleForm

    def get_queryset(self):
        return FilterRule.objects.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_rules'] = FilterRule.objects.count()
        context['active_rules'] = FilterRule.objects.filter(is_active=True).count()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'create':
            self.object_list = self.get_queryset()
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            return self.form_invalid(form)

        if action == 'toggle':
            rule = get_object_or_404(FilterRule, pk=request.POST.get('rule_id'))
            rule.is_active = not rule.is_active
            rule.save()
            state = 'aktiviert' if rule.is_active else 'deaktiviert'
            messages.success(request, f"Regel '{rule.name}' wurde {state}.")
            return redirect('rule_list')

        if action == 'apply_rules':
            result = apply_rules_to_all()
            messages.success(
                request,
                f"Regeln angewendet: {result['processed']} Transaktionen geprüft, "
                f"{result['matched']} kategorisiert, "
                f"{result['unmatched']} ohne passende Regel.",
            )
            return redirect('rule_list')

        messages.error(request, 'Unbekannte Aktion.')
        return redirect('rule_list')

    def form_valid(self, form):
        rule = form.save()
        messages.success(self.request, f"Regel '{rule.name}' wurde erstellt.")
        return redirect('rule_list')

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        messages.error(self.request, 'Regel konnte nicht gespeichert werden. Bitte Eingaben prüfen.')
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(never_cache, name='dispatch')
class RuleUpdateView(UpdateView):
    model = FilterRule
    form_class = FilterRuleForm
    template_name = 'transactions/rule_form.html'
    success_url = reverse_lazy('rule_list')

    def form_valid(self, form):
        messages.success(self.request, f"Regel '{form.instance.name}' wurde aktualisiert.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Bitte Eingaben korrigieren.')
        return super().form_invalid(form)


@method_decorator(never_cache, name='dispatch')
class RuleDeleteView(DeleteView):
    model = FilterRule
    template_name = 'transactions/rule_confirm_delete.html'
    success_url = reverse_lazy('rule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_count'] = TransactionMeta.objects.filter(rule=self.object).count()
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Regel '{self.object.name}' wurde gelöscht.")
        return super().form_valid(form)


def prediction_list(request):
    if request.GET.get('refresh') == '1':
        update_predictions()
        return redirect('prediction_list')

    predictions = PredictionResult.objects.select_related('category').all()
    return render(request, 'transactions/prediction_list.html', {
        'predictions': predictions,
    })


def report_euer(request):
    year = int(request.GET.get('year', timezone.now().year))

    monthly = []
    for month in range(1, 13):
        income = Transaction.objects.filter(
            date__year=year, date__month=month, value__gt=0,
        ).aggregate(total=Sum('value'))['total'] or 0
        expenses = Transaction.objects.filter(
            date__year=year, date__month=month, value__lt=0,
        ).aggregate(total=Sum('value'))['total'] or 0
        monthly.append({
            'month': month,
            'income': income,
            'expenses': expenses,
            'balance': income + expenses,
        })

    total_income = sum(m['income'] for m in monthly)
    total_expenses = sum(m['expenses'] for m in monthly)
    total_balance = total_income + total_expenses

    return render(request, 'transactions/report_euer.html', {
        'year': year,
        'monthly': monthly,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_balance': total_balance,
        'years': range(year - 5, year + 2),
    })
