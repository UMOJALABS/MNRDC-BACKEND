# MNRDC — Modèle de données (UML)

Musée National de la République Démocratique du Congo.

## Le principe

1. L'administrateur enregistre les objets du musée (description, médias) et génère un QR Code pour chacun.
2. Le visiteur scanne le QR Code avec l'application. **Pas de compte, pas de connexion.**
3. L'application affiche l'avatar.
4. En arrière-plan, la description de l'objet est lue à voix haute par une **synthèse vocale** (comme la lecture à voix haute d'Edge pour un PDF).
5. L'avatar ne fait que **donner l'illusion** de raconter l'histoire.

## Règles

- Il y a **un seul avatar par défaut**, utilisé pour tous les objets. Ce n'est pas une IA.
- Il n'y a **pas de conversation** : le visiteur écoute, c'est tout.
- Seul l'**administrateur** a un compte. Il gère les objets, le contenu et les QR Codes.
- Un objet a plusieurs descriptions : **une par langue**.
- Si la description n'existe pas dans la langue choisie, l'application utilise le français.
- Un objet a au plus **un QR Code** (unique), et un QR Code identifie **un seul objet**.

## Diagramme de classes

```mermaid
classDiagram
    class Administrateur {
        +int id
        +String nom
        +String email
        +String motDePasse
        +creerObjet()
        +modifierObjet()
        +supprimerObjet()
        +genererQRCode()
    }

    class Musee {
        +int id
        +String nom
        +String ville
        +String pays
    }

    class Salle {
        +int id
        +String nom
        +int etage
    }

    class ObjetMusee {
        +int id
        +String numeroInventaire
        +Date dateAcquisition
        +String etatConservation
    }

    class Description {
        +String titre
        +String texte
    }

    class Langue {
        +String code
        +String nom
    }

    class Media {
        +int id
        +String type
        +String url
    }

    class QRCode {
        +int id
        +String valeur
        +Date dateGeneration
        +boolean actif
    }

    class Avatar {
        +int id
        +String nom
        +String image
    }

    class Categorie {
        +int id
        +String nom
    }

    class PeriodeHistorique {
        +int id
        +String nom
        +int anneeDebut
        +int anneeFin
    }

    class OrigineCulturelle {
        +int id
        +String nom
        +String region
    }

    class SourceDocumentaire {
        +int id
        +String titre
        +String auteur
        +String reference
    }

    Musee "1" *-- "0..*" Salle : contient
    Salle "0..1" o-- "0..*" ObjetMusee : expose
    Categorie "1" --> "0..*" ObjetMusee : classe
    PeriodeHistorique "0..1" --> "0..*" ObjetMusee : date
    OrigineCulturelle "0..*" -- "0..*" ObjetMusee : origine

    ObjetMusee "1" *-- "1..*" Description : decrit par
    Langue "1" --> "0..*" Description : ecrite en
    ObjetMusee "1" *-- "0..*" Media : illustre par
    ObjetMusee "1" -- "0..1" QRCode : identifie par
    ObjetMusee "0..*" -- "0..*" SourceDocumentaire : s'appuie sur

    Avatar "1" --> "0..*" ObjetMusee : presente

    Administrateur "1" --> "0..*" ObjetMusee : gere
    Administrateur ..> QRCode : genere
```

## Parcours du visiteur

```mermaid
sequenceDiagram
    actor V as Visiteur
    participant APP as Application mobile
    participant API as Serveur
    participant BD as Base de données

    V->>APP: Scanne le QR Code
    APP->>API: Envoie la valeur du QR Code et la langue
    API->>BD: Cherche l'objet
    BD-->>API: Objet, description et médias
    API-->>APP: Données de l'objet
    APP->>APP: Affiche l'avatar
    APP->>APP: Lit la description avec la synthèse vocale
    APP-->>V: L'avatar semble raconter l'histoire
```

## Parcours de l'administrateur

```mermaid
flowchart LR
    A["Connexion de l'administrateur"] --> B["Ajoute ou modifie un objet"]
    B --> C["Saisit une description par langue et ajoute les médias"]
    C --> D["Génère le QR Code de l'objet"]
    D --> E["Imprime le QR Code et le place près de l'objet"]
```