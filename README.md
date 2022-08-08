# [Bot Twitter](https://twitter.com/Myshawii)

Bot qui envoie automatiquement des réponses ennuyantes quand les personnes que tu suis finissent leur tweet par un mot spécial.

N'hésitez pas à ouvrir un ticket ou faire une merge-request pour contribuer au projet.

## Lancer le Bot

Donner la permission au minimum `Read and Write` au bot dans `Settings` puis `App permissions`.

Les codes fourni par l'API de Twitter sont généralements disponible dans la page `Keys and tokens`.

Détails des variables d'environnement :
|     Variable    | Explication et où elle se trouve
| --------------- |-
| TOKEN           | Token d'accès disponible dans la section `Authentication Tokens` sous la sous-rubrique `Access Token and Secret`
| TOKEN_SECRET    | Token d'accès secret disponible dans la section `Authentication Tokens` sous la sous-rubrique `Access Token and Secret`
| CONSUMER_KEY    | Clé API disponible dans la section `Consumer Keys` sous la sous-rubrique `API Key and Secret`
| CONSUMER_SECRET | Clé secrète API disponible dans la section `Consumer Keys` sous la sous-rubrique `API Key and Secret`
| BEARER_TOKEN    | Token disponible dans la section `Authentication Tokens` sous la sous-rubrique `Bearer Token`
| PSEUDOS         | Pseudos du ou des compte.s que vous voulez écouter pour le snipe (a séparer avec une virgule **sans** espaces)
| WHITELIST       | Pseudos des comptes qui ne seront pas touché par le Bot (facultatif, a séparer avec une virgule **sans** espaces, par défaut la liste est vide)
| VERBOSE         | Affiche plus de messages dans la console [False\|True] (facultatif, par défaut sur False)
| FORCELIST       | Force le bot à écouter certains comptes (séparer les comptes avec une virgule **sans** espaces, par défaut la liste est vide)

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
    --BEARER_TOKEN="" \
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
      - BEARER_TOKEN=
      - PSEUDOS=
    restart: unless-stopped
```

## Liste des mots
Certains mots peuvent servir de déclencheur sans être dans la liste,
example : `aussi` n'est pas dans la liste, mais en retirant `aus`,
on obtient `si`, qui est dans la liste.

|           Mot           |             Réponse           |
| ----------------------- | ----------------------------- |
| quoi                    | feur/feuse                    |
| oui                     | stiti/fi                      |
| non                     | bril                          |
| nan                     | cy                            |
| hein                    | deux                          |
| ci                      | tron                          |
| con                     | combre                        |
| ok                      | sur glace                     |
| ouais                   | stern                         |
| comment                 | tateur                        |
| mais                    | on                            |
| fort                    | boyard                        |
| coup                    | teau                          |
| ça                      | pristi/perlipopette/von       |
| bon                     | jour/soir (dépend de l'heure) |
| qui                     | wi/mono                       |
| sur                     | prise                         |
| pas                     | nini/steur                    |
| ka                      | pitaine                       |
| fais                    | rtile                         |
| tant (ou autre syntaxe) | gente                         |
| et                      | eint/ain                      |
| la                      | vabo/vande                    |
| tki                     | la                            |
| moi                     | tié/sson/sissure              |
| toi                     | lette/ture                    |
| top                     | inambour                      |
| jour                    | nal                           |
| ya/yo                   | hourt/yo                      |
| re                      | pas/veil/tourne               |
| ni                      | cotine                        |
| quand                   | dide/tal/didat                |
| sol                     | itaire                        |
| vois                    | ture                          |
| akhy                    | nator                         |
