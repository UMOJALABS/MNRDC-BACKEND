import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from musee.models import ContenuObjet, ObjetMusee

# Fiches pédagogiques fictives, sans création de comptes utilisateur.
DEMO_OBJECTS = [
    {
        "numero_inventaire": 990001,
        "nom": "Tambour cérémoniel (fiche pédagogique fictive)",
        "date_acquisition": "2020-01-15",
        "contenus": {
            "fr": ("Le tambour cérémoniel", "Un instrument de percussion utilisé lors de rassemblements.", "<p>Cette fiche pédagogique présente un tambour cérémoniel fictif. Sa caisse en bois et sa membrane tendue produisent des rythmes qui accompagnent des moments collectifs.</p><p>Les informations de cette fiche sont fictives et servent uniquement à tester le catalogue.</p>"),
            "ln": ("Ngoma ya milulu", "Nzembo ya kobeta oyo esalelamaka na makita.", "<p>Lokasa oyo ezali ya mateya mpe ya kosakana. Ngoma ezali esaleli ya kobeta oyo ekoki kosangana na milulu ya bato.</p>"),
            "sw": ("Ngoma ya sherehe", "Chombo cha kugonga kinachotumiwa katika mikusanyiko.", "<p>Ukurasa huu ni wa mafunzo na ni wa kubuni. Ngoma ni chombo cha muziki kinachoweza kuandamana na mikusanyiko ya jamii.</p>"),
            "en": ("Ceremonial drum", "A percussion instrument used during gatherings.", "<p>This fictional educational entry presents a ceremonial drum. Its wooden body and stretched membrane produce rhythms that accompany shared occasions.</p><p>All details on this entry are fictional and provided for catalogue testing.</p>"),
        },
    },
    {
        "numero_inventaire": 990002,
        "nom": "Panière tressée (fiche pédagogique fictive)",
        "date_acquisition": "2020-02-20",
        "contenus": {
            "fr": ("La panière tressée", "Un contenant fabriqué par entrecroisement de fibres végétales.", "<p>Cette fiche pédagogique fictive décrit une panière tressée. Les fibres sont entrecroisées pour former un contenant léger, utile au transport et au rangement.</p><p>Les informations de cette fiche sont fictives et servent uniquement à tester le catalogue.</p>"),
            "ln": ("Kitunga ya bansinga", "Eloko ya kotia biloko oyo esalemi na bansinga ya milona.", "<p>Lokasa oyo ezali ya mateya mpe ya kosakana. Bansinga ya milona ekangisami mpo na kosala kitunga ya pɛpɛlɛ.</p>"),
            "sw": ("Kikapu kilichosokotwa", "Chombo kilichotengenezwa kwa nyuzi za mimea zilizosokotwa.", "<p>Ukurasa huu ni wa mafunzo na ni wa kubuni. Nyuzi za mimea husokotwa ili kutengeneza kikapu chepesi cha kuhifadhi au kubeba vitu.</p>"),
            "en": ("Woven basket", "A container made by interlacing plant fibres.", "<p>This fictional educational entry describes a woven basket. Plant fibres are interlaced to form a light container for carrying or storing objects.</p><p>All details on this entry are fictional and provided for catalogue testing.</p>"),
        },
    },
    {
        "numero_inventaire": 990003,
        "nom": "Masque sculpté (fiche pédagogique fictive)",
        "date_acquisition": "2020-03-10",
        "contenus": {
            "fr": ("Le masque sculpté", "Un objet décoratif en bois présentant des formes stylisées.", "<p>Cette fiche pédagogique fictive présente un masque sculpté dans le bois. Les formes stylisées montrent comment les choix de lignes et de volumes peuvent créer une expression visuelle.</p><p>Cette pièce et son interprétation sont inventées pour les essais du catalogue.</p>"),
            "ln": ("Elili ya libaya", "Eloko ya kitoko ya libaya oyo ezali na bililingi ya ndenge na ndenge.", "<p>Lokasa oyo ezali ya mateya mpe ya kosakana. Elili oyo ya libaya ezali na bilembo ya kosala lolenge ya komonana.</p>"),
            "sw": ("Kinyago cha mbao", "Kitu cha mapambo cha mbao chenye maumbo yaliyosanifiwa.", "<p>Ukurasa huu ni wa mafunzo na ni wa kubuni. Kinyago cha mbao kina maumbo yaliyosanifiwa yanayoonyesha jinsi mistari na ujazo vinavyoweza kuunda mwonekano.</p>"),
            "en": ("Carved mask", "A decorative wooden object with stylized forms.", "<p>This fictional educational entry presents a carved wooden mask. Its stylized forms show how lines and volumes can create a visual expression.</p><p>The object and its interpretation are invented for catalogue testing.</p>"),
        },
    },
]

EXTRA_OBJECTS = [
    ("Lampe à huile en terre cuite", "Lampe à huile", "Un petit récipient en terre cuite conçu pour accueillir une mèche et de l'huile.", "La forme creuse de cet objet permet de contenir une petite quantité d'huile. Une mèche placée dans son ouverture sert à produire une lumière douce."),
    ("Mortier en bois", "Mortier en bois", "Un récipient robuste destiné à écraser ou broyer des matières.", "Le mortier est présenté avec son pilon assorti. La cavité centrale et les parois épaisses facilitent le broyage manuel."),
    ("Cloche de cérémonie", "Cloche de cérémonie", "Une cloche métallique dont le son peut marquer un rassemblement.", "La cloche est composée d'un corps creux et d'un battant. Sa sonorité dépend de sa taille, de son matériau et de la manière dont elle est frappée."),
    ("Pipe en terre cuite", "Pipe en terre cuite", "Un objet façonné en terre cuite, composé d'un foyer et d'un tuyau.", "Cette pièce permet d'observer une fabrication en terre cuite et l'assemblage de formes distinctes. Sa présentation est uniquement pédagogique."),
    ("Figurine en bois", "Figurine en bois", "Une petite sculpture représentant une silhouette humaine stylisée.", "Les volumes simples de cette figurine mettent en évidence le travail de taille et de polissage du bois. La pièce est inventée pour le catalogue de démonstration."),
    ("Pot de conservation", "Pot de conservation", "Un récipient en céramique destiné au rangement de matières sèches.", "Le corps arrondi et l'ouverture resserrée de ce pot illustrent une forme pensée pour contenir et protéger son contenu."),
    ("Cuillère sculptée", "Cuillère sculptée", "Un ustensile en bois doté d'un manche décoré.", "La cuillère associe une partie creuse fonctionnelle à un manche travaillé. Les motifs présentés sont fictifs et servent à illustrer une fiche de catalogue."),
    ("Bracelet de cuivre", "Bracelet de cuivre", "Un bijou circulaire en métal, façonné pour être porté au poignet.", "La surface du bracelet présente des marques régulières obtenues par martelage. Cette fiche décrit un objet fictif à des fins de démonstration."),
    ("Tissu à motifs géométriques", "Tissu à motifs géométriques", "Un échantillon textile décoré de formes répétées.", "Les formes et les couleurs de cet échantillon sont inventées. La fiche permet de présenter une pièce textile et d'expliquer la répétition d'un motif."),
    ("Boîte en fibres tressées", "Boîte en fibres tressées", "Un petit contenant dont les fibres entrelacées forment les parois et le couvercle.", "Le tressage croisé donne à la boîte sa structure. Son couvercle ajusté permet de ranger de petits objets."),
    ("Récipient à long col", "Récipient à long col", "Un vase en céramique avec une ouverture étroite et un col allongé.", "La silhouette de ce récipient facilite la présentation de différentes techniques de façonnage de l'argile. L'objet et sa provenance sont fictifs."),
    ("Sifflet en bois", "Sifflet en bois", "Un petit instrument à vent creusé dans une pièce de bois.", "L'air soufflé dans l'ouverture produit un son simple. Cette fiche présente le principe acoustique sans attribuer l'objet à une tradition réelle."),
    ("Assiette décorative", "Assiette décorative", "Une assiette en céramique ornée de lignes et de formes peintes.", "Le décor inventé est organisé autour du centre de l'assiette. Il permet d'observer la composition et l'application de pigments sur une surface."),
    ("Peigne sculpté", "Peigne sculpté", "Un peigne en bois avec des dents régulières et un manche orné.", "La pièce montre comment un objet du quotidien peut combiner usage et décor. Les détails de fabrication et d'origine sont fictifs."),
    ("Petit tambour à une membrane", "Petit tambour", "Un instrument de percussion compact composé d'une caisse et d'une membrane tendue.", "La membrane tendue sur la caisse produit un son lorsqu'on la frappe. Cette pièce fictive complète la présentation des objets sonores du catalogue."),
]

for offset, (nom, titre, resume, description) in enumerate(EXTRA_OBJECTS, start=4):
    DEMO_OBJECTS.append({
        "numero_inventaire": 990000 + offset,
        "nom": f"{nom} (fiche fictive)",
        "date_acquisition": f"2020-04-{offset - 3:02d}",
        "contenus": {
            "fr": (titre, resume, f"<p>{description}</p><p>Cette fiche et l'objet décrit sont fictifs. Ils servent uniquement à la démonstration du catalogue.</p>"),
        },
    })

with transaction.atomic():
    for item in DEMO_OBJECTS:
        obj, _ = ObjetMusee.objects.update_or_create(
            numero_inventaire=item["numero_inventaire"],
            defaults={
                "nom": item["nom"],
                "date_acquisition": item["date_acquisition"],
                "qr_actif": True,
            },
        )
        for langue, (titre, resume, description) in item["contenus"].items():
            ContenuObjet.objects.update_or_create(
                objet=obj,
                langue=langue,
                defaults={"titre": titre, "resume": resume, "description": description},
            )

print(f"Seed terminé : {len(DEMO_OBJECTS)} objets pédagogiques, sans nouvel utilisateur.")
