LOGIQUE DES DÉFAUTS : CALCUL D'EXTENSIONS
=========================================

Application Python avec interface graphique pour la logique des défauts (Reiter).
Elle permet de saisir un monde W et des défauts D, de calculer toutes les extensions
de la théorie (W, D), de tester si une formule est conséquence sceptique ou crédule,
et de sauvegarder / recharger une théorie.

Mini-projet 1 du module Représentation de Connaissances et Raisonnement (4-ING-IA, USTHB),
encadré par Dr Naoual Mebtouche.

Fonctionnalités
---------------

- Saisie des faits (W) et des défauts (D), avec vérification de la syntaxe et messages d'erreur
- Avertissement si une justification est incohérente (par exemple x & ~x)
- Vérification de la cohérence de W
- Calcul de toutes les extensions d'une théorie des défauts
- Test des conséquences sceptique et crédule d'une formule
- Sauvegarde et chargement d'une théorie (fichier JSON), extensions comprises
- Menu d'exemples prêts à charger (Tweety, Pingouin, Nixon, exemple du sujet, théorie sans extension)
- Interface moderne avec mode clair et mode sombre
- Fonctionnalités supplémentaires (étape 6) : comparaison « Et si j'ajoute ce fait ? » et schéma des extensions

Installation
------------

Prérequis :

- Python 3.9 ou plus récent (testé avec Python 3.12)
- pip
- Linux uniquement : le module graphique tkinter, à installer avec sudo apt install python3-tk
  (il est déjà inclus avec Python sur Windows et macOS)

Étapes :

1. Récupérer le projet :

   git clone https://github.com/<votre-compte>/default-logic-solver.git
   cd default-logic-solver

   Si vous avez téléchargé l'archive .zip, décompressez-la puis ouvrez un terminal dans le dossier
   qui contient main.py.

2. *(Facultatif mais conseillé)* Créer un environnement virtuel :

   python -m venv venv

   Puis l'activer :

   - Windows : venv\Scripts\activate
   - Linux / macOS : source venv/bin/activate

3. Installer les dépendances :

   pip install -r requirements.txt

   ou, directement : pip install sympy customtkinter

Lancer l'application
--------------------

Depuis le dossier qui contient main.py :

python main.py

Sous Linux ou macOS, utilisez python3 main.py si la commande python n'existe pas.

Utilisation
-----------

1. Dans Monde W, saisissez un fait et cliquez sur Ajouter (ou appuyez sur Entrée).
2. Dans Défauts D, renseignez le prérequis, les justifications (séparées par une virgule)
   et le conséquent, puis cliquez sur Ajouter défaut.
3. Cliquez sur ▶ Générer les extensions : les extensions s'affichent dans la zone Résultats,
   avec leurs littéraux.
4. Saisissez une formule dans Formule φ, puis cliquez sur Sceptique ? ou Crédule ?.
5. Utilisez Enregistrer et Ouvrir pour sauvegarder et recharger une théorie.

Exemple rapide : Nixon :

Menu Exemples, puis Nixon, puis Générer les extensions.

- W = Q, R (Nixon est quaker et républicain)
- D = Q : P / P (un quaker est en général pacifiste) et R : ~P / ~P (un républicain ne l'est en général pas)
- Résultat : 2 extensions, l'une contenant P, l'autre ~P
- P est crédule (vraie dans au moins une extension) mais pas sceptique (pas vraie dans toutes)
- Q est à la fois crédule et sceptique

Syntaxe :

  Écriture  |  Signification
  `~p`  |  non p
  `p & q`  |  p et q
  `p  |  q`  |  p ou q
  `p -> q`  |  p implique q
  `p <-> q`  |  p équivaut à q
  `P(karim)`  |  prédicat (traité comme une proposition atomique)

Un défaut s'écrit prérequis : just1, just2 / conséquent. Le prérequis peut être vide.

Attention : les majuscules et minuscules comptent. Vole et vole sont deux lettres différentes.

Format de sauvegarde
--------------------

Les théories sont enregistrées en JSON :

{
  "version": 1,
  "faits": ["Q", "R"],
  "defauts": ["Q : P / P", "R : ~P / ~P"],
  "extensions": [["Q", "R", "P"], ["Q", "R", "~P"]]
}

Le champ extensions vaut null tant qu'elles n'ont pas été calculées.

Tests
-----

Les tests du calcul (lecture des formules, exemples de référence, sceptique / crédule, sauvegarde)
s'exécutent en console, sans interface :

python tests_console.py

Toutes les lignes doivent commencer par OK.

Structure du projet
-------------------

.
├── main.py                 point d'entrée
├── requirements.txt        dépendances
├── tests_console.py        tests automatiques du backend
├── backend/
│   ├── models.py           classes RegleDeDefaut et BaseDeConnaissance
│   ├── parser.py           lecture et vérification des formules et des défauts
│   ├── logic.py            cohérence et déduction
│   ├── extensions.py       calcul des extensions
│   ├── inference.py        conséquences sceptique et crédule, littéraux
│   ├── storage.py          sauvegarde et chargement (JSON)
│   └── exemples.py         exemples du menu
└── gui/
    └── app.py              interface graphique (customtkinter)

Principe : l'interface ne fait aucun calcul logique. Elle lit la saisie, appelle les fonctions
du dossier backend/ et affiche leurs résultats.

Dépannage
---------

  Message  |  Solution
  `No module named 'sympy'` ou `'customtkinter'`  |  `pip install -r requirements.txt`
  `No module named 'tkinter'` (Linux)  |  `sudo apt install python3-tk`
  `No module named 'backend.xxx'`  |  le fichier `xxx.py` manque dans le dossier `backend/`
  `python` n'est pas reconnu (Windows)  |  réinstaller Python en cochant « Add Python to PATH »

Limites
-------

- Logique propositionnelle : un prédicat comme P(karim) est traité comme une simple lettre.
- Si W est incohérent, aucune extension n'est renvoyée.
- Quand il n'y a aucune extension, la conséquence sceptique est déclarée fausse.
- Le calcul est exponentiel dans le pire cas (nombre de défauts).

Auteurs
-------

- [NOM1 Prénom]
- [NOM2 Prénom]

USTHB, Faculté d'Informatique, 4-ING-IA, année universitaire 2026/2027.