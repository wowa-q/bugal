import logging
import os

from django import forms as django_forms
from django.conf import settings
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
    EuerPositionForm,
    FilterRuleForm,
    ImportForm,
    ManualCategoryForm,
    PositionTransactionsForm,
    TransactionFilterForm,
    TransactionInfoForm,
    TransactionMetaForm,
)
from .models import (
    Category,
    EuerPosition,
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
class ImportDeleteView(DeleteView):
    model = ImportHistory
    template_name = 'transactions/import_confirm_delete.html'
    success_url = reverse_lazy('import_history')
    context_object_name = 'import_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        context['tx_count'] = obj.transactions.count()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        pin = request.POST.get('pin', '').strip()
        if pin != settings.IMPORT_DELETE_PIN:
            messages.error(request, 'Falscher PIN – Import wurde nicht gelöscht.')
            return self.render_to_response(self.get_context_data())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        obj = self.object
        tx_count = obj.transactions.count()
        filename = obj.filename
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Import '{filename}' mit {tx_count} Transaktion(en) wurde gelöscht.",
        )
        return response


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
    from .services.euer import position_summary
    year = int(request.GET.get('year', timezone.now().year))
    positions = EuerPosition.objects.filter(year=year).prefetch_related(
        'transactions', 'transactions__categories__category', 'transactions__meta'
    )
    rows = []
    totals = {'betrag': 0, 'täglich': 0, 'wöchentlich': 0, 'monatlich': 0, 'jährlich': 0}
    for pos in positions:
        summary = position_summary(pos)
        rows.append({'position': pos, 'summary': summary})
        for k in totals:
            totals[k] += summary[k]

    return render(request, 'transactions/report_euer.html', {
        'year': year,
        'rows': rows,
        'totals': totals,
        'years': range(year - 5, year + 2),
    })


@method_decorator(never_cache, name='dispatch')
class EuerWizardStep1View(FormView):
    template_name = 'transactions/euer_wizard_step1.html'
    form_class = EuerPositionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        edit_id = self.request.GET.get('edit') or self.request.session.get('wizard_position_id')
        if edit_id:
            try:
                kwargs['instance'] = EuerPosition.objects.get(pk=int(edit_id))
            except (ValueError, EuerPosition.DoesNotExist):
                pass
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        edit_id = self.request.GET.get('edit')
        if edit_id:
            try:
                pos = EuerPosition.objects.get(pk=int(edit_id))
                initial.update({
                    'name': pos.name,
                    'year': pos.year,
                    'hint': pos.hint,
                    'category': pos.category_id,
                    'art': pos.art,
                    'intervall': pos.intervall,
                    'prioritaet': pos.prioritaet,
                })
                return initial
            except (ValueError, EuerPosition.DoesNotExist):
                pass
        year = self.request.GET.get('year') or self.request.session.get('wizard_year')
        if year:
            try:
                initial['year'] = int(year)
            except ValueError:
                pass
        if not initial.get('year'):
            initial['year'] = timezone.now().year
        # restore values from session if returning from step2
        for key in ['wizard_name', 'wizard_hint', 'wizard_category', 'wizard_art', 'wizard_intervall', 'wizard_prioritaet']:
            sess_val = self.request.session.get(key)
            if sess_val is not None:
                field = key.replace('wizard_', '')
                if field == 'name' and 'name' not in initial:
                    initial['name'] = sess_val
                elif field == 'hint' and 'hint' not in initial:
                    initial['hint'] = sess_val
                elif field not in initial:
                    initial[field] = sess_val
        return initial

    def form_valid(self, form):
        self.request.session['wizard_name'] = form.cleaned_data['name'].strip()
        self.request.session['wizard_year'] = form.cleaned_data['year']
        self.request.session['wizard_hint'] = form.cleaned_data.get('hint') or ''
        self.request.session['wizard_category'] = form.cleaned_data.get('category').pk if form.cleaned_data.get('category') else None
        self.request.session['wizard_art'] = form.cleaned_data.get('art') or ''
        self.request.session['wizard_intervall'] = form.cleaned_data.get('intervall') or ''
        self.request.session['wizard_prioritaet'] = form.cleaned_data.get('prioritaet') or ''
        self.request.session['wizard_position_id'] = None
        edit_id = self.request.GET.get('edit')
        if edit_id:
            try:
                pos = EuerPosition.objects.get(pk=int(edit_id))
                self.request.session['wizard_position_id'] = pos.pk
            except (ValueError, EuerPosition.DoesNotExist):
                pass
        return redirect('euer_wizard_step2')


@method_decorator(never_cache, name='dispatch')
class EuerWizardStep2View(FormView):
    template_name = 'transactions/euer_wizard_step2.html'
    form_class = PositionTransactionsForm

    def dispatch(self, request, *args, **kwargs):
        if 'wizard_name' not in request.session or 'wizard_year' not in request.session:
            messages.error(request, 'Bitte zuerst Position anlegen.')
            return redirect('euer_wizard_step1')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        year = self.request.session.get('wizard_year')
        pos_id = self.request.session.get('wizard_position_id')
        pos = None
        if pos_id:
            try:
                pos = EuerPosition.objects.get(pk=pos_id)
            except EuerPosition.DoesNotExist:
                pass
        kwargs['year'] = year
        kwargs['exclude_position'] = pos
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        tx_ids = self.request.session.get('wizard_tx_ids')
        if tx_ids is not None:
            initial['transaction_ids'] = [str(i) for i in tx_ids]
        else:
            pos_id = self.request.session.get('wizard_position_id')
            if pos_id:
                try:
                    pos = EuerPosition.objects.get(pk=pos_id)
                    initial['transaction_ids'] = [str(pk) for pk in pos.transactions.values_list('id', flat=True)]
                except EuerPosition.DoesNotExist:
                    pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wizard_name'] = self.request.session.get('wizard_name')
        context['wizard_year'] = self.request.session.get('wizard_year')
        pos_id = self.request.session.get('wizard_position_id')
        if pos_id:
            try:
                context['edit_position'] = EuerPosition.objects.get(pk=pos_id)
            except EuerPosition.DoesNotExist:
                pass
        return context

    def form_valid(self, form):
        self.request.session['wizard_tx_ids'] = form.cleaned_data['transaction_ids']
        return redirect('euer_wizard_step3')


@method_decorator(never_cache, name='dispatch')
class EuerWizardStep3View(FormView):
    template_name = 'transactions/euer_wizard_step3.html'
    form_class = django_forms.Form

    def dispatch(self, request, *args, **kwargs):
        if 'wizard_name' not in request.session:
            return redirect('euer_wizard_step1')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        from .services.euer import position_summary
        context = super().get_context_data(**kwargs)
        name = self.request.session.get('wizard_name')
        year = self.request.session.get('wizard_year')
        hint = self.request.session.get('wizard_hint', '')
        tx_ids = self.request.session.get('wizard_tx_ids', [])
        txs = list(Transaction.objects.filter(pk__in=tx_ids).prefetch_related('categories__category', 'meta'))
        context['wizard_name'] = name
        context['wizard_year'] = year
        context['wizard_hint'] = hint
        context['wizard_txs'] = txs
        if txs:
            from decimal import Decimal
            from .services.euer import normalize_amount, _quantize
            from .models import Category as CatModel
            betrag = sum((tx.value for tx in txs), Decimal('0'))
            # position values from wizard session (authoritative)
            cat_id = self.request.session.get('wizard_category')
            typ = self.request.session.get('wizard_art') or ''
            intervall = self.request.session.get('wizard_intervall') or ''
            prioritaet = self.request.session.get('wizard_prioritaet') or ''
            cat = CatModel.objects.filter(pk=cat_id).first() if cat_id else None
            if cat and cat.parent:
                kategorie = cat.parent.name
                sub_kategorie = cat.name
            elif cat:
                kategorie = cat.name
                sub_kategorie = ''
            else:
                kategorie = sub_kategorie = ''
            first = sorted(txs, key=lambda t: t.date)[0]
            konto = first.src_konto or ''
            if intervall == 'abgelaufen':
                täglich = wöchentlich = monatlich = jährlich = _quantize(betrag)
            else:
                täglich = normalize_amount(betrag, intervall, 'täglich')
                wöchentlich = normalize_amount(betrag, intervall, 'wöchentlich')
                monatlich = normalize_amount(betrag, intervall, 'monatlich')
                jährlich = normalize_amount(betrag, intervall, 'jährlich')
            warnings = []
            if len({tx.src_konto for tx in txs}) > 1:
                warnings.append('konto')
            # compare each tx's values against position's values (only if tx has value)
            pos_cat_path = cat.get_full_path() if cat else ''
            for tx in txs:
                tx_cat = list(tx.categories.select_related('category').all())
                tx_cat_path = tx_cat[0].category.get_full_path() if tx_cat else ''
                if tx_cat_path and pos_cat_path and tx_cat_path != pos_cat_path and 'kategorie' not in warnings:
                    warnings.append('kategorie')
                m = getattr(tx, 'meta', None)
                if m:
                    if m.art and typ and m.art != typ and 'typ' not in warnings:
                        warnings.append('typ')
                    if m.intervall and intervall and m.intervall != intervall and 'intervall' not in warnings:
                        warnings.append('intervall')
                    if m.prioritaet and prioritaet and m.prioritaet != prioritaet and 'prioritaet' not in warnings:
                        warnings.append('prioritaet')
            summary = {
                'betrag': _quantize(betrag), 'kategorie': kategorie, 'sub_kategorie': sub_kategorie,
                'typ': typ, 'intervall': intervall, 'prioritaet': prioritaet, 'konto': konto,
                'täglich': täglich, 'wöchentlich': wöchentlich, 'monatlich': monatlich, 'jährlich': jährlich,
                'warnings': warnings, 'has_warning': bool(warnings),
            }
            context['preview'] = summary
            context['total_betrag'] = summary['betrag']
        else:
            context['preview'] = None
            context['total_betrag'] = 0
        pos_id = self.request.session.get('wizard_position_id')
        if pos_id:
            try:
                context['edit_position'] = EuerPosition.objects.get(pk=pos_id)
            except EuerPosition.DoesNotExist:
                pass
        return context

    def form_valid(self, form):
        from django.db import transaction as db_transaction
        name = self.request.session.get('wizard_name')
        year = self.request.session.get('wizard_year')
        hint = self.request.session.get('wizard_hint', '')
        cat_id = self.request.session.get('wizard_category')
        art = self.request.session.get('wizard_art', '')
        intervall = self.request.session.get('wizard_intervall', '')
        prioritaet = self.request.session.get('wizard_prioritaet', '')
        tx_ids = self.request.session.get('wizard_tx_ids', [])
        pos_id = self.request.session.get('wizard_position_id')
        with db_transaction.atomic():
            if pos_id:
                try:
                    pos = EuerPosition.objects.get(pk=pos_id)
                    pos.name = name
                    pos.year = year
                    pos.hint = hint
                    pos.category_id = cat_id
                    pos.art = art
                    pos.intervall = intervall
                    pos.prioritaet = prioritaet
                    pos.save()
                except EuerPosition.DoesNotExist:
                    pos = EuerPosition.objects.create(name=name, year=year, hint=hint, category_id=cat_id, art=art, intervall=intervall, prioritaet=prioritaet)
            else:
                pos = EuerPosition.objects.create(name=name, year=year, hint=hint, category_id=cat_id, art=art, intervall=intervall, prioritaet=prioritaet)
            already = set(
                EuerPosition.objects.filter(year=year)
                .exclude(pk=pos.pk)
                .values_list('transactions__id', flat=True)
            )
            already.discard(None)
            valid_ids = [i for i in tx_ids if i not in already]
            pos.transactions.set(valid_ids)
            if len(valid_ids) < len(tx_ids):
                messages.warning(self.request, f"{len(tx_ids) - len(valid_ids)} Transaktion(en) waren bereits zugeordnet und wurden übersprungen.")
        for key in ['wizard_name', 'wizard_year', 'wizard_hint', 'wizard_category', 'wizard_art', 'wizard_intervall', 'wizard_prioritaet', 'wizard_tx_ids', 'wizard_position_id']:
            self.request.session.pop(key, None)
        messages.success(self.request, f"Position '{pos.name}' für {pos.year} wurde gespeichert.")
        return redirect(f"{reverse('report_euer')}?year={pos.year}")


@method_decorator(never_cache, name='dispatch')
class EuerPositionHintView(UpdateView):
    model = EuerPosition
    form_class = EuerPositionForm
    template_name = 'transactions/euer_hint_form.html'

    def get_success_url(self):
        return f"{reverse('report_euer')}?year={self.object.year}"

    def form_valid(self, form):
        messages.success(self.request, f"Position '{form.instance.name}' wurde aktualisiert.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Bitte Eingaben korrigieren.')
        return super().form_invalid(form)


@method_decorator(never_cache, name='dispatch')
class EuerPositionDeleteView(DeleteView):
    model = EuerPosition
    template_name = 'transactions/euer_confirm_delete.html'

    def get_success_url(self):
        return f"{reverse('report_euer')}?year={self.object.year}"

    def form_valid(self, form):
        messages.success(self.request, f"Position '{self.object.name}' wurde gelöscht.")
        return super().form_valid(form)
