import logging
import time
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import ContactForm

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Retrieve client IP respecting reverse proxy headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class ContactView(View):
    template_name = "contact/index.html"

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        is_htmx = request.headers.get("HX-Request") == "true"

        # Rate Limiting: Max 3 submissions per 5 minutes per session
        now = time.time()
        submissions = [t for t in request.session.get("contact_timestamps", []) if now - t < 300]
        if len(submissions) >= 3:
            msg = "Rate limit reached: Maximum 3 inquiries per 5 minutes. Please wait a moment before sending another transmission."
            if is_htmx:
                return render(request, "contact/partials/form_status.html", {
                    "success": False,
                    "rate_limited": True,
                    "error_message": msg,
                })
            messages.error(request, msg)
            return redirect("contact:index")

        form = ContactForm(request.POST)

        if form.is_valid():
            contact_msg = form.save(commit=False)
            contact_msg.ip_address = get_client_ip(request)
            contact_msg.save()

            # Record submission timestamp
            submissions.append(now)
            request.session["contact_timestamps"] = submissions

            # Optional email notification
            notification_target = getattr(settings, "CONTACT_NOTIFICATION_EMAIL", "")
            if notification_target:
                try:
                    send_mail(
                        subject=f"[Portfolio Contact] {contact_msg.subject}",
                        message=(
                            f"New inquiry received from: {contact_msg.name} ({contact_msg.email})\n"
                            f"Organization: {contact_msg.organization or 'N/A'}\n\n"
                            f"Message:\n{contact_msg.message}"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[notification_target],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.warning(f"Could not send email notification: {e}")

            if is_htmx:
                return render(request, "contact/partials/form_status.html", {
                    "success": True,
                    "name": contact_msg.name,
                })

            messages.success(request, f"Thank you {contact_msg.name}, your message has been received.")
            return redirect("contact:index")

        if is_htmx:
            return render(request, "contact/partials/form_status.html", {
                "success": False,
                "form": form,
            })

        messages.error(request, "Please correct the errors in the form below.")
        return render(request, self.template_name, {"form": form})
