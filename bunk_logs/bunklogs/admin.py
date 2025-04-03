from campers.models import CamperBunkAssignment
import tempfile
from pathlib import Path

from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from .forms import BunkLogAdminForm
from .forms import BunkSelectionForm
from .forms import BunkLogCsvImportForm
from .models import BunkLog
from .services.imports import import_bunk_logs_from_csv, generate_sample_csv


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
            path("import-bunklogs/", self.import_bunklogs, name="bunklog_import_csv"),
        ]
        return custom_urls + urls

    def select_bunk_view(self, request):
        """View for selecting a bunk before adding a bunk log."""
        if request.method == "POST":
            form = BunkSelectionForm(request.POST)
            if form.is_valid():
                bunk_id = form.cleaned_data["bunk"].id
                add_url = reverse("admin:bunklogs_bunklog_add")  # Assuming 'bunklogs_bunklog_add' is the correct name
                return redirect(f"{add_url}?bunk={bunk_id}")
        else:
            form = BunkSelectionForm()

        context = {
            "form": form,
            "title": _("Select Bunk"),
            "opts": self.opts,  # Changed from self.model._meta to self.opts
            'list_url': 'admin:bunklogs_bunklog_changelist',
        }
        return render(request, "admin/bunklogs/select_bunk.html", context)

    def import_bunklogs(self, request):
        if request.method == "POST":
            form = BunkLogCsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_file"]
                dry_run = form.cleaned_data["dry_run"]

                # Save the uploaded file to a secure temporary file
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = Path(temp_file.name)
                    for chunk in csv_file.chunks():
                        temp_file.write(chunk)

                # Process the CSV file
                try:
                    # Get the current user as default counselor if they're staff
                    default_counselor_email = request.user.email if request.user.is_staff else None
                
                    result = import_bunk_logs_from_csv(
                        temp_path, 
                        dry_run=dry_run,
                        default_counselor_email=default_counselor_email
                    )
                
                    if dry_run:
                        messages.info(
                            request,
                            "Dry run completed. "
                            f"{result['success_count']} bunklogs would be imported.",
                        )
                    else:
                        messages.success(
                            request,
                            f"Successfully imported {result['success_count']} bunklogs.",
                        )

                    if result["error_count"] > 0:
                        for error in result["errors"]:
                            messages.error(
                                request,
                                f"Error in row {error['row']}: {error['error']}",
                            )
                except Exception as e:
                    messages.error(request, f"Import failed: {str(e)}")
                finally:
                    # Clean up the temporary file
                    temp_path.unlink(missing_ok=True)

                    return redirect("admin:bunklogs_bunklog_changelist")
        else:
            form = BunkLogCsvImportForm()

        context = {
            "form": form,
            "title": "Import BunkLogs from CSV",
            "opts": self.model._meta,
            "app_label": self.model._meta.app_label,
            "model_name": self.model._meta.model_name,
            "sample_csv": generate_sample_csv(),  # Add sample CSV content
        }
        return render(request, "admin/csv_form.html", context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["import_bunklogs"] = reverse("admin:bunklog_import_csv")
        return super().changelist_view(request, extra_context=extra_context)

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
