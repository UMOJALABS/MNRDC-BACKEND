from rest_framework import serializers

from .models import ContenuObjet, ImageObjet


class ImageCarouselSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ImageObjet
        fields = ("url",)

    def get_url(self, obj):
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class ContenuObjetPublicSerializer(serializers.ModelSerializer):
    numero_inventaire = serializers.IntegerField(source="objet.numero_inventaire", read_only=True, allow_null=True)
    nom_objet = serializers.CharField(source="objet.nom", read_only=True)
    image_principale = serializers.SerializerMethodField()
    images_carousel = ImageCarouselSerializer(source="objet.images_carousel", many=True, read_only=True)

    class Meta:
        model = ContenuObjet
        fields = ("nom_objet", "numero_inventaire", "image_principale", "images_carousel", "titre", "langue", "resume", "description")

    def get_image_principale(self, obj):
        if not obj.objet.image_principale:
            return None
        request = self.context.get("request")
        url = obj.objet.image_principale.url
        return request.build_absolute_uri(url) if request else url
