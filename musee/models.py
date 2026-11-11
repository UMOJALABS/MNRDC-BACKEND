import secrets

from django.db import models
from django.utils import timezone

LANGUAGE_CHOICES = [
    ("fr", "Français"),
    ("ln", "Lingala"),
    ("sw", "Swahili"),
    ("en", "Anglais"),
]


class ObjetMusee(models.Model):
    nom = models.CharField(max_length=250)
    numero_inventaire = models.PositiveBigIntegerField(
        unique=True,
        null=True,
        blank=True,
    )
    date_acquisition = models.DateField(null=True, blank=True)
    qr_valeur = models.CharField(max_length=128, unique=True, null=True, blank=True, db_index=True)
    qr_actif = models.BooleanField(default=True)
    qr_date_generation = models.DateTimeField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "objet du musée"
        verbose_name_plural = "objets du musée"

    def save(self, *args, **kwargs):
        if not self.qr_valeur:
            self.qr_valeur = secrets.token_urlsafe(18)
            self.qr_date_generation = timezone.now()
        elif self.qr_date_generation is None:
            self.qr_date_generation = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class ContenuObjet(models.Model):
    objet = models.ForeignKey(ObjetMusee, on_delete=models.CASCADE, related_name="contenus")
    langue = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        help_text="Langue de cette traduction.",
    )
    titre = models.CharField(max_length=250)
    resume = models.TextField(help_text="Bref texte destiné à la synthèse vocale.")
    description = models.TextField(help_text="Description complète mise en forme avec l'éditeur riche.")

    class Meta:
        ordering = ["langue"]
        constraints = [models.UniqueConstraint(fields=["objet", "langue"], name="unique_contenu_objet_langue")]
        verbose_name = "contenu traduit"
        verbose_name_plural = "contenus traduits"

    def save(self, *args, **kwargs):
        self.langue = self.langue.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.objet} — {self.langue}"
