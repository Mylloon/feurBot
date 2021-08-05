# Bot Twitter

Bot qui envoie automatiquement des réponses ennuyante quand les personnes que tu suis finissent leur tweet par mot spécial.
| Mot | Réponse               | ¦ | Mot     | Réponse                   | ¦ | Mot     | Réponse
------|-----------------------|:-:|---------|---------------------------|:-:|---------|-
quoi  | feur (ou équivalent)  | ¦ | con     | combre (ou équivalent)    | ¦ | coup    | teau (ou équivalent)
oui   | stiti (ou équivalent) | ¦ | ok      | sur glace (ou équivalent) | ¦ | ca      | pristi (ou équivalent)
non   | bril (ou équivalent)  | ¦ | ouais   | stern (ou équivalent)     | ¦ | bon     | jour/soir (ou équivalent, dépend de l'heure)
nan   | cy (ou équivalent)    | ¦ | comment | tateur (ou équivalent)    | ¦ | qui     | wi (ou équivalent)
hein  | deux (ou équivalent)  | ¦ | mais    | on (ou équivalent)        | ¦ |
ci    | tron (ou équivalent)  | ¦ | fort    | boyard (ou équivalent)    | ¦ |

N'hésitez pas à ouvrir un ticket ou faire une merge request pour ajouter des mots/réponses.

## Lancer le Bot

Donner la permission `Read and Write` (ou `Read + Write + Direct Messages` mais aucun DM n'est envoyé) au Bot dans `Settings` puis `App permissions`.

Détails des variables d'environnement :
| Variable      | Explication et où elle se trouve
----------------|-
TOKEN           | Token d'accès disponible dans la section `Authentication Tokens` sous la sous-rubrique `Access Token and Secret`
TOKEN_SECRET    | Token d'accès secret disponible dans la section `Authentication Tokens` sous la sous-rubrique `Access Token and Secret`
CONSUMER_KEY    | Clé API disponible dans la section `Consumer Keys`
CONSUMER_SECRET | Clé secrète API disponible dans la section `Consumer Keys`
PSEUDOS         | Pseudos du ou des compte.s que vous voulez écouter pour le snipe (a séparer avec une virgule **sans** espaces)
WHITELIST       | Pseudos des comptes qui ne seront pas touché par le Bot (facultatif, a séparer avec une virgule **sans** espaces, par défaut la liste est vide)
VERBOSE         | Affiche plus de messages dans la console [False\|True] (facultatif, par défaut sur False)

### En local

Pour le lancer, complètez le `.envexample` et renomme le en `.env`.

Ensuite, installez les dépendances avec `pip install -r requirements.txt`.

Et enfin lancez `python3 main.py`.

### Avec Docker

Avec une ligne de commande :
```bash
docker run -d \
    --name="feurBot" \
    registry.gitlab.com/mylloon/feurbot:latest \
    --TOKEN="" \
    --TOKEN_SECRET="" \
    --CONSUMER_KEY="" \
    --CONSUMER_SECRET="" \
    --PSEUDOS=""
```
Ou avec un `docker-compose.yml` :
```bash
version: "2.1"
services:
  feurBot:
    image: registry.gitlab.com/mylloon/feurbot:latest
    container_name: feurBot
    environment:
      - TOKEN=
      - TOKEN_SECRET=
      - CONSUMER_KEY=
      - CONSUMER_SECRET=
      - PSEUDOS=
    restart: unless-stopped
```
