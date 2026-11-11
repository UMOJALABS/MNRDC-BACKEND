from rest_framework import serializers

from .models import ContenuObjet


class ContenuObjetPublicSerializer(serializers.ModelSerializer):
    numero_inventaire = serializers.IntegerField(source="objet.numero_inventaire", read_only=True, allow_null=True)
    nom_objet = serializers.CharField(source="objet.nom", read_only=True)

    class Meta:
        model = ContenuObjet
        fields = ("nom_objet", "numero_inventaire", "titre", "langue", "resume", "description")
