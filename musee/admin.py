import io
import zipfile

from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.text import slugify
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin, StackedInline

from .models import ContenuObjet, ImageObjet, ObjetMusee
from .qr_codes import build_qr_png


class ContenuObjetForm(forms.ModelForm):
    class Meta:
        model = ContenuObjet
        fields = "__all__"
        widgets = {
            "description": TinyMCE(attrs={"cols": 100, "rows": 30}, mce_attrs={
                "height": 560,
                "menubar": True,
                "plugins": "lists link table code",
                "toolbar": "undo redo | blocks | bold italic underline | bullist numlist | blockquote | link table | removeformat | code",
                "language": "fr_FR",
            })}

    class Media:
        css = {"all": ("musee/admin-tinymce.css",)}
        js = ("musee/admin-tinymce.js",)


class ContenuObjetInline(StackedInline):
    model = ContenuObjet
    form = ContenuObjetForm
    collapsible = True
    extra = 0
    show_change_link = True
    fields = ("langue", "titre", "resume", "description")


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = {"class": "mnr-multiple-image-input", "accept": "image/*", **(attrs or {})}
        super().__init__(attrs)


class MultipleImageField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleImageField, self).clean(file, initial) for file in files]


class ObjetMuseeAdminForm(forms.ModelForm):
    images_carousel = MultipleImageField(
        required=False,
        label="Images du carousel",
        help_text="Sélectionnez une ou plusieurs images.",
    )

    class Meta:
        model = ObjetMusee
        fields = "__all__"

    class Media:
        js = ("musee/admin-multiple-images.js",)


@admin.register(ObjetMusee)
class ObjetMuseeAdmin(ModelAdmin):
    change_list_template = "admin/musee/objetmusee/change_list.html"
    form = ObjetMuseeAdminForm
    list_display = ("nom", "numero_inventaire", "qr_actif", "qr_apercu")
    list_filter = ("qr_actif",)
    search_fields = ("nom", "numero_inventaire", "contenus__titre", "contenus__resume")
    ordering = ("nom",)
    list_per_page = 25
    date_hierarchy = "cree_le"
    inlines = (ContenuObjetInline,)
    readonly_fields = ("cree_le", "modifie_le", "qr_valeur", "qr_date_generation", "qr_preview")
    fields = (
        "nom", "numero_inventaire", "date_acquisition",
        "image_principale", "images_carousel",
        "qr_valeur", "qr_actif", "qr_date_generation", "qr_preview",
        "cree_le", "modifie_le",
    )

    @admin.display(boolean=True, description="QR actif")
    def qr_actif(self, obj):
        return obj.qr_actif

    @admin.display(description="QR Code")
    def qr_apercu(self, obj):
        if not obj.qr_valeur:
            return "Enregistrez l'objet pour générer son QR Code."
        return format_html(
            '<img src="{}" alt="QR Code" style="width:90px;height:90px">',
            f"{obj.pk}/qr/?preview=1",
        )

    @admin.display(description="Aperçu et téléchargement du QR Code")
    def qr_preview(self, obj):
        if not obj or not obj.qr_valeur:
            return "Le QR Code sera généré à l'enregistrement."
        url = "../qr/?preview=1"
        download = "../qr/"
        return format_html(
            '<div style="display:flex;align-items:center;gap:16px">'
            '<img src="{}" alt="Aperçu QR Code" style="width:180px;height:180px;border:1px solid #ddd;border-radius:8px">'
            '<a class="button" href="{}">Télécharger le PNG</a></div>', url, download
        )

    def get_urls(self):
        return [
            path("qr-codes.zip", self.admin_site.admin_view(self.qr_codes_zip), name="musee_objetmusee_qr_zip"),
            path("<path:object_id>/qr/", self.admin_site.admin_view(self.qr_image), name="musee_objet_qr"),
        ] + super().get_urls()

    def qr_codes_zip(self, request):
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for obj in ObjetMusee.objects.order_by("nom"):
                if not obj.qr_valeur:
                    obj.save()
                filename = slugify(obj.nom) or f"objet-{obj.pk}"
                zip_file.writestr(f"qr_{filename}_{obj.pk}.png", build_qr_png(obj.qr_valeur))

        response = HttpResponse(archive.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="qr-codes-musee.zip"'
        return response

    def qr_image(self, request, object_id):
        from django.shortcuts import get_object_or_404

        obj = get_object_or_404(ObjetMusee, pk=object_id)
        if not obj.qr_valeur:
            obj.save()
        response = HttpResponse(build_qr_png(obj.qr_valeur), content_type="image/png")
        disposition = "inline" if request.GET.get("preview") == "1" else "attachment"
        filename = slugify(obj.nom) or f"objet-{obj.pk}"
        response["Content-Disposition"] = f'{disposition}; filename="qr_{filename}.png"'
        return response

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for image in form.cleaned_data.get("images_carousel", []):
            ImageObjet.objects.create(objet=form.instance, image=image)


@admin.register(ContenuObjet)
class ContenuObjetAdmin(ModelAdmin):
    form = ContenuObjetForm
    list_display = ("titre", "objet", "langue")
    list_filter = ("langue",)
    search_fields = ("titre", "resume", "description", "objet__numero_inventaire")
    ordering = ("objet__nom", "langue")
    list_per_page = 25
    fields = ("objet", "langue", "titre", "resume", "description")


admin.site.site_header = "MNRDC · Administration du musée"
admin.site.site_title = "MNRDC Admin"
admin.site.index_title = "Gestion du catalogue"
admin.site.site_url = None
