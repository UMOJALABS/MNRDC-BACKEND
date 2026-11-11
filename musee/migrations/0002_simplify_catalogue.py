import django.db.models.deletion
from django.db import migrations, models


def copy_qr_and_language_data(apps, schema_editor):
    Objet = apps.get_model("musee", "ObjetMusee")
    Contenu = apps.get_model("musee", "ContenuObjet")
    QR = apps.get_model("musee", "QRCode")
    Langue = apps.get_model("musee", "Langue")

    for item in QR.objects.select_related("objet"):
        Objet.objects.filter(pk=item.objet_id).update(
            qr_valeur=item.valeur,
            qr_actif=item.actif,
            qr_date_generation=item.date_generation,
        )
    for content in Contenu.objects.all().iterator():
        try:
            code = Langue.objects.get(pk=content.langue_id).code
        except Langue.DoesNotExist:
            code = "fr"
        Contenu.objects.filter(pk=content.pk).update(langue_code=code)


class Migration(migrations.Migration):
    dependencies = [("musee", "0001_initial")]

    operations = [
        migrations.AddField("objetmusee", "qr_valeur", models.CharField(blank=True, db_index=True, max_length=128, null=True, unique=True)),
        migrations.AddField("objetmusee", "qr_actif", models.BooleanField(default=True)),
        migrations.AddField("objetmusee", "qr_date_generation", models.DateTimeField(blank=True, null=True)),
        migrations.AddField("contenuobjet", "langue_code", models.CharField(blank=True, max_length=10, null=True)),
        migrations.RunPython(copy_qr_and_language_data, migrations.RunPython.noop),
        migrations.RemoveConstraint("contenuobjet", "unique_contenu_objet_langue"),
        migrations.RemoveField("contenuobjet", "langue"),
        migrations.RenameField("contenuobjet", "langue_code", "langue"),
        migrations.AlterField("contenuobjet", "langue", models.CharField(help_text="Code de langue, par exemple fr ou ln.", max_length=10)),
        migrations.RemoveField("objetmusee", "categorie"),
        migrations.RemoveField("objetmusee", "origines"),
        migrations.RemoveField("objetmusee", "periode"),
        migrations.RemoveField("objetmusee", "salle"),
        migrations.RemoveField("objetmusee", "sources"),
        migrations.AlterUniqueTogether("salle", set()),
        migrations.RemoveField("salle", "musee"),
        migrations.DeleteModel("Categorie"),
        migrations.DeleteModel("Langue"),
        migrations.DeleteModel("Musee"),
        migrations.DeleteModel("OrigineCulturelle"),
        migrations.DeleteModel("PeriodeHistorique"),
        migrations.DeleteModel("QRCode"),
        migrations.DeleteModel("Salle"),
        migrations.DeleteModel("SourceDocumentaire"),
        migrations.AlterModelOptions("contenuobjet", {"ordering": ["langue"], "verbose_name": "contenu traduit", "verbose_name_plural": "contenus traduits"}),
        migrations.AddConstraint("contenuobjet", models.UniqueConstraint(fields=("objet", "langue"), name="unique_contenu_objet_langue")),
    ]
