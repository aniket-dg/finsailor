from django import forms

from data_import.models import TradeBook


class TradeBookForm(forms.ModelForm):
    class Meta:
        model = TradeBook
        fields = "__all__"
