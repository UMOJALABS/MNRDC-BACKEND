from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import ContenuObjet, LANGUAGE_CHOICES, ObjetMusee
from .serializers import ContenuObjetPublicSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def objet_par_qr(request, valeur):
    objet = get_object_or_404(ObjetMusee, qr_valeur=valeur, qr_actif=True)
    langue_demandee = (request.query_params.get("langue") or "fr").strip().lower()
    contenu = objet.contenus.filter(langue__iexact=langue_demandee).first()
    fallback = False
    if contenu is None and langue_demandee != "fr":
        contenu = objet.contenus.filter(langue__iexact="fr").first()
        fallback = contenu is not None
    if contenu is None:
        return Response({"detail": "Aucun contenu disponible dans cette langue ni en français."}, status=404)
    data = ContenuObjetPublicSerializer(contenu, context={"request": request}).data
    data.update({"langue_demandee": langue_demandee, "fallback_langue": fallback, "description_format": "html"})
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def langues(request):
    present = set(ContenuObjet.objects.order_by().values_list("langue", flat=True).distinct())
    return Response([
        {"code": code, "nom": name}
        for code, name in LANGUAGE_CHOICES
        if code in present
    ])


@api_view(["GET"])
@permission_classes([AllowAny])
def langues_objet(request, valeur):
    objet = get_object_or_404(ObjetMusee, qr_valeur=valeur, qr_actif=True)
    present = set(objet.contenus.order_by().values_list("langue", flat=True).distinct())
    return Response([
        {"code": code, "nom": name}
        for code, name in LANGUAGE_CHOICES
        if code in present
    ])
