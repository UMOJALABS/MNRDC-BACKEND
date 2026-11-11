from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.text import slugify
from tinymce.widgets import TinyMCE

from .models import ContenuObjet, ObjetMusee
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


class ContenuObjetInline(admin.StackedInline):
    model = ContenuObjet
    form = ContenuObjetForm
    extra = 1
    fields = ("langue", "titre", "resume", "description")


@admin.register(ObjetMusee)
class ObjetMuseeAdmin(admin.ModelAdmin):
    list_display = ("nom", "numero_inventaire", "qr_actif", "qr_apercu")
    list_filter = ("qr_actif",)
    search_fields = ("nom", "numero_inventaire", "contenus__titre", "contenus__resume")
    inlines = (ContenuObjetInline,)
    readonly_fields = ("cree_le", "modifie_le", "qr_valeur", "qr_date_generation", "qr_preview")
    fields = (
        "nom", "numero_inventaire", "date_acquisition",
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
        return [path("<path:object_id>/qr/", self.admin_site.admin_view(self.qr_image), name="musee_objet_qr")] + super().get_urls()

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


@admin.register(ContenuObjet)
class ContenuObjetAdmin(admin.ModelAdmin):
    form = ContenuObjetForm
    list_display = ("titre", "objet", "langue")
    list_filter = ("langue",)
    search_fields = ("titre", "resume", "description", "objet__numero_inventaire")
    fields = ("objet", "langue", "titre", "resume", "description")


admin.site.site_header = "MNRDC · Administration du musée"
admin.site.site_title = "MNRDC Admin"
admin.site.index_title = "Gestion du catalogue"
admin.site.site_url = None
