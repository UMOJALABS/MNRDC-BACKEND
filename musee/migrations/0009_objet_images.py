from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("musee", "0008_alter_objetmusee_numero_inventaire"),
    ]

    operations = [
        migrations.AddField(
            model_name="objetmusee",
            name="image_principale",
            field=models.ImageField(blank=True, null=True, upload_to="musee/objets/principales/"),
        ),
        migrations.CreateModel(
            name="ImageObjet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="musee/objets/carousel/")),
                ("objet", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images_carousel", to="musee.objetmusee")),
            ],
            options={
                "verbose_name": "image du carousel",
                "verbose_name_plural": "images du carousel",
            },
        ),
    ]
