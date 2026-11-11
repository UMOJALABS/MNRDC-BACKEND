from django.urls import path

from . import api

app_name = "musee"

urlpatterns = [
    path("objets/qr/<str:valeur>/langues/", api.langues_objet, name="langues-objet"),
    path("objets/qr/<str:valeur>/", api.objet_par_qr, name="objet-par-qr"),
    path("langues/", api.langues, name="langues"),
]
