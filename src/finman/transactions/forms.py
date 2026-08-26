from django import forms

from .models import (
    ART_CHOICES,
    INTERVALL_CHOICES,
    PRIORITAET_CHOICES,
    FilterRule,
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
