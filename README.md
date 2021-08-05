# Bot Twitter

Bot qui envoie automatiquement des réponses ennuyante quand les personnes que tu suis finissent leur tweet par mot spécial.
| Mot   | Réponse
--------|-
quoi    | feur (ou équivalent)
oui     | stiti (ou équivalent)
non     | bril (ou équivalent)
nan     | cy (ou équivalent)
hein    | deux (ou équivalent)
ci      | tron (ou équivalent)
con     | combre (ou équivalent)
ok      | sur glace (ou équivalent)
ouais   | stern (ou équivalent)
comment | tateur (ou équivalent)
mais    | on (ou équivalent)
fort    | boyard (ou équivalent)

N'hésitez pas à ouvrir un ticket ou faire une merge request pour ajouter des mots/réponses.

Pour le lancer, complète le `.envexample` et renomme le en `.env`.
| Variable      | Explication et où elle se trouve
----------------|-
TOKEN           | Token d'accès disponible dans la section `Authentication Tokens` sous la sous-rubrique `Access Token and Secret`
TOKEN_SECRET    | Token d'accès secret disponible dans la section `Authentication Tokens` sous la sous-rubrique `Access Token and Secret`
CONSUMER_KEY    | Clé API disponible dans la section `Consumer Keys`
CONSUMER_SECRET | Clé secrète API disponible dans la section `Consumer Keys`
PSEUDOS         | Pseudos du ou des compte.s que vous voulez écouter pour le snipe (a séparer avec une virgule **sans** espaces)
WHITELIST       | Pseudos des comptes qui ne seront pas touché par le Bot (facultatif, a séparer avec une virgule **sans** espaces, par défaut la liste est vide)
VERBOSE         | Affiche plus de messages dans la console [False\|True] (facultatif, par défaut sur False)

Ensuite installe les dépendances avec `pip install -r requirements.txt`.

Et enfin  `python3 main.py`.
