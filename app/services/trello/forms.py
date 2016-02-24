from django import forms
from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _


class ConfigForm(forms.Form):
    board = forms.ChoiceField(
        widget=Select,
        label=_('Select a board'),
        required=False
    )

    def __init__(self, boards, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)

        if boards:
            self.fields['board'].choices = [
                ('', '')] + [
                (board['id'], board['name']) for board in boards
            ]
