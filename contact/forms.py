from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot field: invisible to human users, traps spam bots that fill all form fields
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "style": "display:none !important; position:absolute !important; left:-9999px !important;",
            "tabindex": "-1",
            "autocomplete": "off",
            "aria-hidden": "true",
        })
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "organization", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/60 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-sm transition",
                "placeholder": "Your name or team",
                "required": True,
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/60 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-sm transition",
                "placeholder": "name@example.com",
                "required": True,
            }),
            "organization": forms.TextInput(attrs={
                "class": "w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/60 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-sm transition",
                "placeholder": "Company, university, or lab (optional)",
            }),
            "subject": forms.TextInput(attrs={
                "class": "w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/60 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-sm transition",
                "placeholder": "Technical inquiry, collaboration, or opportunity",
                "required": True,
            }),
            "message": forms.Textarea(attrs={
                "class": "w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/60 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-sm transition resize-y",
                "placeholder": "Describe your project, question, or technical challenge...",
                "rows": 5,
                "required": True,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        honeypot = cleaned_data.get("website")
        if honeypot:
            # Bot detected: raise error or discard silently
            raise forms.ValidationError("Spam detection triggered.")
        return cleaned_data
