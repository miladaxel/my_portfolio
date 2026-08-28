from django import forms

from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = (
            "name",
            "email",
            "telegram_id",
            "phone",
            "subject",
            "message",
        )

    def clean(self):
        # The same invariant also exists as a database constraint. Handling it
        # here gives API clients a field-level validation response before save.
        cleaned_data = self.cleaned_data
        if not any(
            cleaned_data.get(field)
            for field in ("email", "telegram_id", "phone")
        ):
            raise forms.ValidationError(
                "At least one contact method is required: email, Telegram ID, or phone."
            )
        return cleaned_data
