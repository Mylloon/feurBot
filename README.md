# Bot Twitter

Bot qui envoie automatiquement des réponses ennuyantes quand les personnes que tu suis finissent leur tweet par un mot spécial.

Certains mots peuvent servir de "trigger" sans être dans la liste, example : `aussi` n'est pas dans la liste, mais en retirant `aus`, on obtient `si`, qui est dans la liste.
| Mot | Réponse    | ¦ | Mot     | Réponse   | ¦ | Mot  | Réponse                       | ¦ | Mot                     | Réponse    | ¦ | Mot   | Réponse
------|---------   |:-:|---------|-----------|:-:|------|-------------------------------|:-:|-------------------------|------------|:-:|-------|-
quoi  | feur       | ¦ | con     | combre    | ¦ | coup | teau                          | ¦ | ka                      | pitaine    | ¦ | moi   | tié/sson/sissure
oui   | stiti/fi   | ¦ | ok      | sur glace | ¦ | ca   | pristi                        | ¦ | fais                    | rtile      | ¦ | toi   | lette/ture
non   | bril       | ¦ | ouais   | stern     | ¦ | bon  | jour/soir (dépend de l'heure) | ¦ | tant (ou autre syntaxe) | gente      | ¦ | top   | inambour
nan   | cy         | ¦ | comment | tateur    | ¦ | qui  | wi/mono                       | ¦ | et                      | eint/ain   | ¦ | jour  | nal
hein  | deux       | ¦ | mais    | on        | ¦ | sur  | prise                         | ¦ | la                      | vabo/vande | ¦ | ya/yo | hourt/yo
ci    | tron       | ¦ | fort    | boyard    | ¦ | pas  | nini/steur                    | ¦ | tki                     | la         | ¦ |

N'hésitez pas à ouvrir un ticket ou faire une merge-request pour contribuer au projet.

## Lancer le Bot

Donner la permission `Read and Write` (ou `Read + Write + Direct Messages` mais aucun DM n'est envoyé) au bot dans `Settings` puis `App permissions`.

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
