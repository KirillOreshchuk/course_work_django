from django.forms import ModelForm

from newsletter.models import Message, MailingSettings


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = ('title', 'text',)


class MailingSettingsForm(StyleFormMixin, ModelForm):
    class Meta:
        model = MailingSettings
        fields = ('start_time', 'end_time', 'periodicity', 'clients', 'message',)
