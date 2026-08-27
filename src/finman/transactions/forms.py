from django import forms
from django.db.models import Q

from .models import (
    ART_CHOICES,
    ENTSCHEIDUNG_CHOICES,
    GEBRAUCHTKAUF_CHOICES,
    INTERVALL_CHOICES,
    PRIORITAET_CHOICES,
    EuerPosition,
    FilterRule,
    InvestmentDecision,
    PlannedInvestment,
    TransactionCategory,
    TransactionInfo,
    Category,
)


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_path()


class ImportForm(forms.Form):
    file = forms.FileField(
        required=False,
        label='CSV-Datei hochladen',
    )
    file_path = forms.CharField(
        required=False,
        label='Oder absoluter Dateipfad',
        widget=forms.TextInput(attrs={'placeholder': 'C:\\Pfad\\zur\\Datei.csv'}),
    )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('file') and not cleaned.get('file_path'):
            raise forms.ValidationError(
                'Bitte laden Sie eine Datei hoch oder geben Sie einen Dateipfad ein.'
            )
        return cleaned


class CategoryForm(forms.ModelForm):
    parent = CategoryChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='— Keine (Hauptkategorie) —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Category
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Category.objects.filter(parent__isnull=True)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        self.fields['parent'].queryset = queryset

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Bitte einen Namen angeben.')
        return name

    def clean(self):
        cleaned = super().clean()
        name = cleaned.get('name')
        parent = cleaned.get('parent')
        if not name:
            return cleaned
        qs = Category.objects.filter(name__iexact=name.strip())
        qs = qs.filter(parent__isnull=True) if parent is None else qs.filter(parent=parent)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            location = f"unter '{parent.get_full_path()}'" if parent else 'auf der obersten Ebene'
            raise forms.ValidationError(
                f"Eine Kategorie '{name.strip()}' existiert bereits {location}."
            )
        return cleaned


class ManualCategoryForm(forms.ModelForm):
    category = CategoryChoiceField(
        queryset=Category.objects.all(),
        empty_label='— Kategorie wählen —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = TransactionCategory
        fields = ['category']


class TransactionMetaForm(forms.Form):
    category = CategoryChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='— Keine Kategorie —',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    art = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + ART_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    prioritaet = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + PRIORITAET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    intervall = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + INTERVALL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )


class TransactionInfoForm(forms.ModelForm):
    class Meta:
        model = TransactionInfo
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class FilterRuleForm(forms.ModelForm):
    category = CategoryChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='— Keine Kategorie —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    art = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + ART_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    prioritaet = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + PRIORITAET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    intervall = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + INTERVALL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = FilterRule
        fields = [
            'name',
            'debitor_contains',
            'verwendung_contains',
            'category',
            'art',
            'prioritaet',
            'intervall',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'debitor_contains': forms.TextInput(attrs={'class': 'form-control'}),
            'verwendung_contains': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and not (self.instance and self.instance.pk):
            self.initial.setdefault('is_active', True)

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Bitte einen Namen angeben.')
        return name

    def clean_debitor_contains(self):
        return self.cleaned_data.get('debitor_contains', '').strip()

    def clean_verwendung_contains(self):
        return self.cleaned_data.get('verwendung_contains', '').strip()

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('debitor_contains') and not cleaned.get('verwendung_contains'):
            raise forms.ValidationError(
                'Bitte mindestens einen Suchbegriff für Debitor oder Verwendung angeben.'
            )
        return cleaned


class TransactionFilterForm(forms.Form):
    start = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}, format='%Y-%m-%d'),
    )
    end = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}, format='%Y-%m-%d'),
    )
    debitor = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Suche...'}),
    )
    category = CategoryChoiceField(
        queryset=Category.objects.filter(parent__isnull=True),
        required=False,
        empty_label='Alle',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    art = forms.ChoiceField(
        required=False,
        choices=[('', 'Alle')] + ART_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    prioritaet = forms.ChoiceField(
        required=False,
        choices=[('', 'Alle')] + PRIORITAET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    intervall = forms.ChoiceField(
        required=False,
        choices=[('', 'Alle')] + INTERVALL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )


CREATION_FORBIDDEN_INTERVALLS = {'einmalig', 'abgelaufen'}


class EuerPositionForm(forms.ModelForm):
    category = CategoryChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='— Keine Kategorie —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    art = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + ART_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Typ',
    )
    intervall = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + INTERVALL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    prioritaet = forms.ChoiceField(
        required=False,
        choices=[('', '— Keine Angabe —')] + PRIORITAET_CHOICES,
        label='Priorität',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = EuerPosition
        fields = ['name', 'year', 'category', 'art', 'intervall', 'prioritaet', 'hint']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'hint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'category': 'Kategorie',
            'hint': 'Hinweis',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Bitte einen Namen angeben.')
        return name

    def clean(self):
        cleaned = super().clean()
        name = cleaned.get('name')
        year = cleaned.get('year')
        if name and year:
            qs = EuerPosition.objects.filter(name__iexact=name.strip(), year=year)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f"Eine Position '{name.strip()}' existiert bereits für Jahr {year}."
                )
        return cleaned


class PlannedInvestmentForm(forms.ModelForm):
    new_euer_position_name = forms.CharField(
        required=False,
        label='Neue Position Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'z.B. Neue Heizungsanlage'}),
    )
    new_euer_position_year = forms.IntegerField(
        required=False,
        label='Jahr',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'z.B. 2026'}),
    )

    class Meta:
        model = PlannedInvestment
        fields = [
            'investitionsobjekt', 'datum', 'kategorie', 'prioritaet', 'nutzniesser', 'roi', 'aktuelle_loesung',
            'nutzung_ab', 'intervall', 'zeitaufwand_min', 'zeitaufwand_max', 'nutzungsdauer_min', 'nutzungsdauer_max',
            'diy_workaround', 'gebrauchtkauf_status', 'gebrauchtkauf_begruendung', 'mietmoeglichkeit',
            'mietkosten_min', 'mietkosten_max', 'anschaffungspreis_min', 'anschaffungspreis_max',
            'preis_entwicklung', 'folgeanschaffungen', 'folgeanschaffungen_min', 'folgeanschaffungen_max',
            'inbetriebnahme_zeit_min', 'inbetriebnahme_zeit_max', 'inbetriebnahme_kosten_min', 'inbetriebnahme_kosten_max',
            'betriebskosten_min', 'betriebskosten_max', 'instandhaltung_min', 'instandhaltung_max',
            'reinigung_min', 'reinigung_max', 'versicherung_min', 'versicherung_max', 'reparatur_min', 'reparatur_max',
            'entsorgung_min', 'entsorgung_max', 'wiederverkauf_prozent', 'letzte_ueberpruefung', 'euer_position',
        ]
        widgets = {
            'investitionsobjekt': forms.TextInput(attrs={'class': 'form-control'}),
            'datum': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'kategorie': forms.Select(attrs={'class': 'form-select'}),
            'prioritaet': forms.Select(attrs={'class': 'form-select'}),
            'nutzniesser': forms.Select(attrs={'class': 'form-select'}),
            'roi': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'aktuelle_loesung': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'nutzung_ab': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'intervall': forms.Select(attrs={'class': 'form-select'}),
            'zeitaufwand_min': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'z.B. 0:30'}),
            'zeitaufwand_max': forms.TextInput(attrs={'class': 'form-control'}),
            'nutzungsdauer_min': forms.TextInput(attrs={'class': 'form-control'}),
            'nutzungsdauer_max': forms.TextInput(attrs={'class': 'form-control'}),
            'diy_workaround': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'gebrauchtkauf_status': forms.Select(attrs={'class': 'form-select'}),
            'gebrauchtkauf_begruendung': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'mietmoeglichkeit': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'preis_entwicklung': forms.TextInput(attrs={'class': 'form-control'}),
            'folgeanschaffungen': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'wiederverkauf_prozent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'letzte_ueberpruefung': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'euer_position': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = EuerPosition.objects.filter(investment__isnull=True)
        if self.instance and self.instance.pk and self.instance.euer_position_id:
            qs = EuerPosition.objects.filter(Q(investment__isnull=True) | Q(pk=self.instance.euer_position_id))
        self.fields['euer_position'].queryset = qs
        self.fields['euer_position'].required = False
        self.fields['euer_position'].empty_label = '— keine —'

    def clean(self):
        cleaned = super().clean()
        pairs = [
            ('mietkosten_min', 'mietkosten_max'), ('anschaffungspreis_min', 'anschaffungspreis_max'),
            ('folgeanschaffungen_min', 'folgeanschaffungen_max'),
            ('inbetriebnahme_kosten_min', 'inbetriebnahme_kosten_max'),
            ('betriebskosten_min', 'betriebskosten_max'), ('instandhaltung_min', 'instandhaltung_max'),
            ('reinigung_min', 'reinigung_max'), ('versicherung_min', 'versicherung_max'),
            ('reparatur_min', 'reparatur_max'), ('entsorgung_min', 'entsorgung_max'),
        ]
        for f_min, f_max in pairs:
            vmin = cleaned.get(f_min)
            vmax = cleaned.get(f_max)
            if vmin is not None and vmax is not None and vmax < vmin:
                self.add_error(f_max, 'Max darf nicht kleiner als Min sein.')
        if cleaned.get('zeitaufwand_min') and cleaned.get('zeitaufwand_max') and cleaned['zeitaufwand_max'] < cleaned['zeitaufwand_min']:
            self.add_error('zeitaufwand_max', 'Max darf nicht kleiner als Min sein.')
        if cleaned.get('inbetriebnahme_zeit_min') and cleaned.get('inbetriebnahme_zeit_max') and cleaned['inbetriebnahme_zeit_max'] < cleaned['inbetriebnahme_zeit_min']:
            self.add_error('inbetriebnahme_zeit_max', 'Max darf nicht kleiner als Min sein.')
        # EÜR-Position: entweder auswählen oder neu anlegen, nicht beides
        new_name = (cleaned.get('new_euer_position_name') or '').strip()
        new_year = cleaned.get('new_euer_position_year')
        existing = cleaned.get('euer_position')
        if new_name or new_year is not None:
            if existing:
                self.add_error('euer_position', 'Bitte entweder bestehende Position wählen oder neue anlegen – nicht beides.')
            if not new_name:
                self.add_error('new_euer_position_name', 'Name erforderlich.')
            if new_year is None:
                self.add_error('new_euer_position_year', 'Jahr erforderlich.')
            if new_name and new_year is not None:
                if EuerPosition.objects.filter(name__iexact=new_name, year=new_year).exists():
                    # beim Edit eigene Position ausnehmen
                    qs = EuerPosition.objects.filter(name__iexact=new_name, year=new_year)
                    if self.instance and self.instance.pk and self.instance.euer_position_id:
                        qs = qs.exclude(pk=self.instance.euer_position_id)
                    if qs.exists():
                        self.add_error('new_euer_position_name', f"Position '{new_name}' existiert bereits für Jahr {new_year}.")
        return cleaned

    def save(self, commit=True):
        new_name = (self.cleaned_data.get('new_euer_position_name') or '').strip()
        new_year = self.cleaned_data.get('new_euer_position_year')
        if new_name and new_year is not None:
            pos = EuerPosition.objects.create(name=new_name, year=new_year)
            self.instance.euer_position = pos
        return super().save(commit=commit)


class InvestmentDecisionForm(forms.ModelForm):
    class Meta:
        model = InvestmentDecision
        fields = ['status', 'datum', 'begruendung']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'datum': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'begruendung': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PositionTransactionsForm(forms.Form):
    transaction_ids = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, year=None, exclude_position=None, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import EuerPosition, Transaction
        assigned_ids = set(
            EuerPosition.objects.filter(year=year)
            .exclude(pk=exclude_position.pk if exclude_position else None)
            .values_list('transactions__id', flat=True)
        )
        assigned_ids.discard(None)
        base_qs = list(Transaction.objects.order_by('-date')[:500])
        base_ids = {tx.pk for tx in base_qs}
        choices = []
        for tx in base_qs:
            if tx.pk not in assigned_ids:
                choices.append((str(tx.pk), f"{tx.date} | {tx.debitor[:40]} | {tx.value} €"))
        if exclude_position:
            missing = []
            for tx in exclude_position.transactions.select_related().all():
                if tx.pk not in base_ids and tx.pk not in assigned_ids:
                    missing.append(tx)
            for tx in sorted(missing, key=lambda t: t.date, reverse=True):
                choices.append((str(tx.pk), f"{tx.date} | {tx.debitor[:40]} | {tx.value} € (zugeordnet)"))
        self.fields['transaction_ids'].choices = choices

    def clean_transaction_ids(self):
        return [int(v) for v in self.cleaned_data.get('transaction_ids') or []]
