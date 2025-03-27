from campers.models import CamperBunkAssignment
from django.contrib import admin
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from .forms import BunkLogAdminForm
from .forms import BunkSelectionForm
from .models import BunkLog


@admin.register(BunkLog)
class BunkLogAdmin(admin.ModelAdmin):
    form = BunkLogAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Update the queryset based on the bunk
        if "bunk_assignment" in form.base_fields:
            bunk_id = request.GET.get("bunk")
            if bunk_id:
                form.base_fields[
                    "bunk_assignment"
                ].queryset = CamperBunkAssignment.objects.filter(
                    bunk_id=bunk_id,
                    is_active=True,
                ).select_related("camper")
        return form

    list_display = ("date", "get_camper_name", "get_bunk_name", "counselor")
    list_filter = ("date", "bunk_assignment__bunk", "counselor")
    search_fields = (
        "bunk_assignment__camper__first_name",
        "bunk_assignment__camper__last_name",
        "date",
        "counselor",
        "bunk_assignment__bunk__name",
    )

    @admin.display(
        description=_("Camper"),
    )
    def get_camper_name(self, obj):
        return obj.bunk_assignment.camper

    @admin.display(
        description=_("Bunk"),
    )
    def get_bunk_name(self, obj):
        return obj.bunk_assignment.bunk.name

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "select-bunk/",
                self.admin_site.admin_view(self.select_bunk_view),
                name="bunklog_select_bunk",
            ),
        ]
        return custom_urls + urls

    def select_bunk_view(self, request):
        """View for selecting a bunk before adding a bunk log."""
        if request.method == "POST":
            form = BunkSelectionForm(request.POST)
            if form.is_valid():
                bunk_id = form.cleaned_data["bunk"].id
                return redirect(f"../add/?bunk={bunk_id}")
        else:
            form = BunkSelectionForm()

        context = {
            "form": form,
            "title": _("Select Bunk"),
            "opts": self.opts,  # Changed from self.model._meta to self.opts
        }
        return render(request, "admin/bunklogs/select_bunk.html", context)

    def add_view(self, request, form_url="", extra_context=None):
        """Override add view to check for bunk parameter and filter assignments."""
        bunk_id = request.GET.get("bunk")
        if not bunk_id:
            # If no bunk is selected, redirect to bunk selection
            return redirect("../select-bunk/")
        return super().add_view(request, form_url, extra_context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter bunk assignments based on selected bunk and active status."""
        if db_field.name == "bunk_assignment":
            bunk_id = request.GET.get("bunk")
            if bunk_id:
                kwargs["queryset"] = CamperBunkAssignment.objects.filter(
                    bunk_id=bunk_id,
                    is_active=True,  # Only show active assignments
                    bunk__is_active=True,  # Only from active bunks
                ).select_related("camper")
            else:
                # Even without a specific bunk selected, only show active assignments
                kwargs["queryset"] = CamperBunkAssignment.objects.filter(
                    is_active=True,
                    bunk__is_active=True,
                ).select_related("camper")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
