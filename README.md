# [Bot Twitter](https://twitter.com/Myshawii)

Bot qui envoie automatiquement des réponses ennuyantes quand les personnes que tu suis finissent leur tweet par un mot spécial.

Certains mots peuvent servir de "trigger" sans être dans la liste, example : `aussi` n'est pas dans la liste, mais en retirant `aus`, on obtient `si`, qui est dans la liste.
| Mot | Réponse    | ¦ | Mot     | Réponse   | ¦ | Mot  | Réponse                       | ¦ | Mot                     | Réponse    | ¦ | Mot   | Réponse           | ¦ | Mot   | Réponse
------|---------   |:-:|---------|-----------|:-:|------|-------------------------------|:-:|-------------------------|------------|:-:|-------|------------------ |:-:|-------|-
quoi  | feur       | ¦ | con     | combre    | ¦ | coup | teau                          | ¦ | ka                      | pitaine    | ¦ | moi   | tié/sson/sissure  | ¦ | ni    | cotine
oui   | stiti/fi   | ¦ | ok      | sur glace | ¦ | ça   | pristi/perlipopette/von       | ¦ | fais                    | rtile      | ¦ | toi   | lette/ture        | ¦ | quand | dide/tal/didat
non   | bril       | ¦ | ouais   | stern     | ¦ | bon  | jour/soir (dépend de l'heure) | ¦ | tant (ou autre syntaxe) | gente      | ¦ | top   | inambour          | ¦ | sol   | itaire
nan   | cy         | ¦ | comment | tateur    | ¦ | qui  | wi/mono                       | ¦ | et                      | eint/ain   | ¦ | jour  | nal               | ¦ | vois  | ture
hein  | deux       | ¦ | mais    | on        | ¦ | sur  | prise                         | ¦ | la                      | vabo/vande | ¦ | ya/yo | hourt/yo          | ¦ | akhy  | nator
ci    | tron       | ¦ | fort    | boyard    | ¦ | pas  | nini/steur                    | ¦ | tki                     | la         | ¦ | re    | pas/veil/tourne   | ¦ |

N'hésitez pas à ouvrir un ticket ou faire une merge-request pour contribuer au projet.

## Lancer le Bot

Donner la permission `Read and Write` (ou `Read + Write + Direct Messages` mais aucun DM n'est envoyé) au bot dans `Settings` puis `App permissions`.

Les codes fourni par l'API de Twitter sont généralements disponible dans la page `Keys and tokens`.

Détails des variables d'environnement :
| Variable      | Explication et où elle se trouve
----------------|-
TOKEN           | Token d'accès disponible dans la section `Authentication Tokens` sous la sous-rubrique `Access Token and Secret`
TOKEN_SECRET    | Token d'accès secret disponible dans la section `Authentication Tokens` sous la sous-rubrique `Access Token and Secret`
CONSUMER_KEY    | Clé API disponible dans la section `Consumer Keys` sous la sous-rubrique `API Key and Secret`
CONSUMER_SECRET | Clé secrète API disponible dans la section `Consumer Keys` sous la sous-rubrique `API Key and Secret`
BEARER_TOKEN    | Token disponible dans la section `Authentication Tokens` sous la sous-rubrique `Bearer Token`
PSEUDOS         | Pseudos du ou des compte.s que vous voulez écouter pour le snipe (a séparer avec une virgule **sans** espaces)
WHITELIST       | Pseudos des comptes qui ne seront pas touché par le Bot (facultatif, a séparer avec une virgule **sans** espaces, par défaut la liste est vide)
VERBOSE         | Affiche plus de messages dans la console [False\|True] (facultatif, par défaut sur False)
FORCELIST       | Force le bot à écouter certains comptes (séparer les comptes avec une virgule **sans** espaces, par défaut la liste est vide)

### En local

Pour le lancer, renommez le `.envexample` en `.env` et complètez-le.

Ensuite, installez les dépendances avec `pip install -r requirements.txt`.

Et enfin lancez le bot avec `python3 main.py`.

### Avec Docker

Avec une ligne de commande :
```bash
docker build https://git.kennel.ml/Anri/feurBot.git#main --tag feurbot:main && \
docker run -d \
    --name="feurBot" \
    feurbot:main \
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
  feurbot:
    build: https://git.kennel.ml/Anri/feurBot.git#main
    container_name: feurBot
    environment:
      - TOKEN=
      - TOKEN_SECRET=
      - CONSUMER_KEY=
      - CONSUMER_SECRET=
      - PSEUDOS=
    restart: unless-stopped
```
