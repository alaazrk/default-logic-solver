"""

Installation :  pip install customtkinter sympy
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog

from backend.models import BaseDeConnaissance
from backend.parser import parser_formule, parser_defaut
from backend.logic import est_coherent
from backend.extensions import calculer_extensions
from backend.inference import (
    est_consequence_sceptique, est_consequence_credule, litteraux,
)
from backend.storage import sauvegarder, charger, base_depuis_textes
from backend.exemples import EXEMPLES

TYPES_FICHIER = [("Théorie (JSON)", "*.json"), ("Tous les fichiers", "*.*")]


ACCENT = "#4F46E5"
ACCENT_SURVOL = "#4338CA"
GRIS = ("#E5E7EB", "#374151")
GRIS_SURVOL = ("#D1D5DB", "#4B5563")
TEXTE = ("#111827", "#F3F4F6")
TEXTE_DISCRET = ("#6B7280", "#9CA3AF")
FOND_CARTE = ("#FFFFFF", "#1F2937")
BORDURE = ("#E5E7EB", "#374151")
SELECTION = ("#E0E7FF", "#3730A3")
TONS = {                                   # (fond, texte) des bandeaux de message
    "info": (("#E0E7FF", "#312E81"), ("#3730A3", "#C7D2FE")),
    "ok": (("#DCFCE7", "#14532D"), ("#166534", "#BBF7D0")),
    "alerte": (("#FEE2E2", "#7F1D1D"), ("#991B1B", "#FECACA")),
}


def bouton_principal(parent, texte, commande, **options):
    return ctk.CTkButton(parent, text=texte, command=commande, height=38, corner_radius=10,
                         fg_color=ACCENT, hover_color=ACCENT_SURVOL, text_color="white",
                         font=ctk.CTkFont(size=14, weight="bold"), **options)


def bouton_secondaire(parent, texte, commande, **options):
    return ctk.CTkButton(parent, text=texte, command=commande, height=34, corner_radius=10,
                         fg_color=GRIS, hover_color=GRIS_SURVOL, text_color=TEXTE, **options)


class ListeSelectionnable(ctk.CTkScrollableFrame):
    """Une liste dont on peut cliquer une ligne (remplace tk.Listbox, qui fait « ancien »)."""

    def __init__(self, parent, texte_vide, **options):
        super().__init__(parent, fg_color=("#F9FAFB", "#111827"), corner_radius=10, **options)
        self.texte_vide = texte_vide
        self.lignes = []
        self.index = None

    def remplir(self, textes):
        for widget in self.winfo_children():
            widget.destroy()
        self.lignes, self.index = [], None
        if not textes:
            ctk.CTkLabel(self, text=self.texte_vide, text_color=TEXTE_DISCRET).pack(pady=24)
            return
        police = ctk.CTkFont(family="Consolas", size=14)
        for i, texte in enumerate(textes):
            ligne = ctk.CTkButton(self, text=texte, anchor="w", height=34, corner_radius=8,
                                  fg_color="transparent", hover_color=GRIS, text_color=TEXTE,
                                  font=police, command=lambda i=i: self.choisir(i))
            ligne.pack(fill="x", padx=2, pady=2)
            self.lignes.append(ligne)

    def choisir(self, i):
        self.index = i
        for j, ligne in enumerate(self.lignes):
            ligne.configure(fg_color=SELECTION if j == i else "transparent")

    def selection(self):
        return self.index

    def taille(self):
        return len(self.lignes)


class Application(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("light")
        super().__init__()
        self.title("Logique des défauts")
        self.geometry("1120x880")
        self.minsize(940, 740)

        # Les seules données de l'application :
        self.base = BaseDeConnaissance()   # la théorie (W, D)
        self.extensions = None             # None = pas encore calculées
        self.journal = []                  # texte brut de ce qui est affiché (pour les tests)

        self.grid_columnconfigure((0, 1), weight=1, uniform="col")
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(3, weight=3)

        self._entete()
        self._carte_monde()
        self._carte_defauts()
        self._barre_actions()
        self._zone_resultats()
        self.rafraichir_listes()
        self.message_accueil()

    
    # Construction de la fenêtre
 
    def _entete(self):
        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(16, 4))
        entete.grid_columnconfigure(0, weight=1)

        titres = ctk.CTkFrame(entete, fg_color="transparent")
        titres.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titres, text="Logique des défauts",
                     font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXTE).pack(anchor="w")
        ctk.CTkLabel(titres, text="Extensions, conséquences sceptiques et crédules",
                     text_color=TEXTE_DISCRET).pack(anchor="w")

        outils = ctk.CTkFrame(entete, fg_color="transparent")
        outils.grid(row=0, column=1, sticky="e")
        bouton_secondaire(outils, "Nouveau", self.nouveau, width=90).pack(side="left", padx=3)
        bouton_secondaire(outils, "Ouvrir", self.ouvrir, width=90).pack(side="left", padx=3)
        bouton_secondaire(outils, "Enregistrer", self.enregistrer, width=110).pack(side="left", padx=3)

        self.menu_exemples = ctk.CTkOptionMenu(
            outils, values=list(EXEMPLES), command=self._choix_exemple, width=130, height=34,
            corner_radius=10, fg_color=ACCENT, button_color=ACCENT_SURVOL,
            button_hover_color=ACCENT_SURVOL)
        self.menu_exemples.set("Exemples")
        self.menu_exemples.pack(side="left", padx=(8, 3))

        self.interrupteur = ctk.CTkSwitch(outils, text="Sombre", command=self.changer_theme,
                                          progress_color=ACCENT)
        self.interrupteur.pack(side="left", padx=(14, 0))

    def _carte(self, ligne, colonne, marges):
        carte = ctk.CTkFrame(self, corner_radius=16, fg_color=FOND_CARTE,
                             border_width=1, border_color=BORDURE)
        carte.grid(row=ligne, column=colonne, sticky="nsew", padx=marges, pady=8)
        carte.grid_columnconfigure(0, weight=1)
        return carte

    def _titre_carte(self, carte, titre, sous_titre):
        bloc = ctk.CTkFrame(carte, fg_color="transparent")
        bloc.grid(row=0, column=0, sticky="w", padx=18, pady=(14, 8))
        ctk.CTkLabel(bloc, text=titre, font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=TEXTE).pack(anchor="w")
        ctk.CTkLabel(bloc, text=sous_titre, text_color=TEXTE_DISCRET).pack(anchor="w")

    def _entree(self, parent, indice):
        return ctk.CTkEntry(parent, placeholder_text=indice, height=36, corner_radius=10,
                            font=ctk.CTkFont(family="Consolas", size=14))

    def _carte_monde(self):
        carte = self._carte(1, 0, (20, 8))
        carte.grid_rowconfigure(2, weight=1)
        self._titre_carte(carte, "Monde W", "Les faits certains")

        saisie = ctk.CTkFrame(carte, fg_color="transparent")
        saisie.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
        saisie.grid_columnconfigure(0, weight=1)
        self.entree_formule = self._entree(saisie, "ex.  p -> o")
        self.entree_formule.grid(row=0, column=0, sticky="ew")
        self.entree_formule.bind("<Return>", lambda e: self.ajouter_formule())
        bouton_principal(saisie, "Ajouter", self.ajouter_formule, width=90).grid(
            row=0, column=1, padx=(8, 0))

        self.liste_w = ListeSelectionnable(carte, "Aucun fait pour l'instant")
        self.liste_w.grid(row=2, column=0, sticky="nsew", padx=18)

        bas = ctk.CTkFrame(carte, fg_color="transparent")
        bas.grid(row=3, column=0, sticky="ew", padx=18, pady=14)
        bouton_secondaire(bas, "Supprimer", self.supprimer_formule, width=100).pack(side="left")
        bouton_secondaire(bas, "Vérifier la cohérence de W", self.verifier_coherence).pack(side="right")

    def _carte_defauts(self):
        carte = self._carte(1, 1, (8, 20))
        carte.grid_rowconfigure(2, weight=1)
        self._titre_carte(carte, "Défauts D", "Des règles vraies « en général »")

        saisie = ctk.CTkFrame(carte, fg_color="transparent")
        saisie.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
        saisie.grid_columnconfigure((0, 1, 2), weight=1, uniform="champ")
        self.entree_prerequis = self._entree(saisie, "Prérequis")
        self.entree_justifs = self._entree(saisie, "Justifications")
        self.entree_conclusion = self._entree(saisie, "Conséquent")
        for colonne, entree in enumerate((self.entree_prerequis, self.entree_justifs,
                                          self.entree_conclusion)):
            entree.grid(row=0, column=colonne, sticky="ew", padx=(0 if colonne == 0 else 6, 0))
        self.entree_conclusion.bind("<Return>", lambda e: self.ajouter_defaut())

        self.liste_d = ListeSelectionnable(carte, "Aucun défaut pour l'instant")
        self.liste_d.grid(row=2, column=0, sticky="nsew", padx=18)

        bas = ctk.CTkFrame(carte, fg_color="transparent")
        bas.grid(row=3, column=0, sticky="ew", padx=18, pady=14)
        bouton_secondaire(bas, "Supprimer", self.supprimer_defaut, width=100).pack(side="left")
        bouton_principal(bas, "Ajouter défaut", self.ajouter_defaut, width=130).pack(side="right")

    def _barre_actions(self):
        barre = ctk.CTkFrame(self, corner_radius=16, fg_color=FOND_CARTE,
                             border_width=1, border_color=BORDURE)
        barre.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=4)
        barre.grid_columnconfigure(2, weight=1)

        bouton_principal(barre, "▶  Générer les extensions", self.generer_extensions).grid(
            row=0, column=0, padx=14, pady=12)
        ctk.CTkLabel(barre, text="Formule φ", text_color=TEXTE_DISCRET).grid(
            row=0, column=1, padx=(14, 6))
        self.entree_phi = self._entree(barre, "ex.  P")
        self.entree_phi.grid(row=0, column=2, sticky="ew")
        self.entree_phi.bind("<Return>", lambda e: self.tester("crédule"))
        bouton_secondaire(barre, "Sceptique ?", lambda: self.tester("sceptique"),
                          width=110).grid(row=0, column=3, padx=(10, 4))
        bouton_secondaire(barre, "Crédule ?", lambda: self.tester("crédule"),
                          width=110).grid(row=0, column=4, padx=(4, 14))

    def _zone_resultats(self):
        carte = ctk.CTkFrame(self, corner_radius=16, fg_color=FOND_CARTE,
                             border_width=1, border_color=BORDURE)
        carte.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=20, pady=(8, 20))
        carte.grid_columnconfigure(0, weight=1)
        carte.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(carte, text="Résultats", font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=TEXTE).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 4))
        self.zone_res = ctk.CTkScrollableFrame(carte, fg_color="transparent")
        self.zone_res.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

  
    # Zone Résultats : tout ce qui s'affiche passe par ces petites méthodes

    def effacer_resultats(self):
        for widget in self.zone_res.winfo_children():
            widget.destroy()
        self.journal = []

    def _defiler_en_bas(self):
        try:
            self.update_idletasks()
            self.zone_res._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def ajouter_message(self, texte, ton="info"):
        fond, couleur = TONS[ton]
        ctk.CTkLabel(self.zone_res, text=texte, fg_color=fond, text_color=couleur,
                     corner_radius=10, anchor="w", justify="left", wraplength=900,
                     padx=14, pady=10).pack(fill="x", padx=4, pady=4)
        self.journal.append(texte)
        self._defiler_en_bas()

    def ajouter_titre(self, texte):
        ctk.CTkLabel(self.zone_res, text=texte, font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXTE, anchor="w").pack(fill="x", padx=6, pady=(2, 4))
        self.journal.append(texte)

    def ajouter_carte_extension(self, numero, extension):
        contenu = ", ".join(extension)
        lits = litteraux(extension)

        carte = ctk.CTkFrame(self.zone_res, corner_radius=12, fg_color=("#F9FAFB", "#111827"),
                             border_width=1, border_color=BORDURE)
        carte.pack(fill="x", padx=4, pady=4)
        carte.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(carte, text=f"E{numero}", width=44, height=30, corner_radius=8,
                     fg_color=ACCENT, text_color="white",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=(12, 10), pady=(12, 6), sticky="w")
        ctk.CTkLabel(carte, text=f"Th({{{contenu}}})", anchor="w", justify="left",
                     wraplength=820, text_color=TEXTE,
                     font=ctk.CTkFont(family="Consolas", size=14)).grid(
            row=0, column=1, sticky="w", pady=(12, 6))

        puces = ctk.CTkFrame(carte, fg_color="transparent")
        puces.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 12))
        ctk.CTkLabel(puces, text="littéraux", text_color=TEXTE_DISCRET).pack(side="left", padx=(0, 8))
        for lit in lits:
            fond, couleur = TONS["alerte" if lit.startswith("~") else "ok"]
            ctk.CTkLabel(puces, text=f" {lit} ", height=26, corner_radius=13, fg_color=fond,
                         text_color=couleur, font=ctk.CTkFont(family="Consolas", size=13)).pack(
                side="left", padx=3)
        if not lits:
            ctk.CTkLabel(puces, text="aucun", text_color=TEXTE_DISCRET).pack(side="left")

        self.journal.append(f"E{numero} = Th({{{contenu}}})   littéraux : {', '.join(lits) or 'aucun'}")

    def ajouter_reponse(self, phi, mode, reponse, sans_extension):
        carte = ctk.CTkFrame(self.zone_res, corner_radius=12, fg_color=("#F9FAFB", "#111827"),
                             border_width=1, border_color=BORDURE)
        carte.pack(fill="x", padx=4, pady=4)
        carte.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(carte, text=phi, font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
                     text_color=TEXTE).grid(row=0, column=0, padx=(14, 10), pady=12)
        note = "   (il n'y a aucune extension)" if sans_extension else ""
        ctk.CTkLabel(carte, text=f"conséquence {mode}{note}", text_color=TEXTE_DISCRET,
                     anchor="w").grid(row=0, column=1, sticky="w")
        fond, couleur = TONS["ok" if reponse else "alerte"]
        ctk.CTkLabel(carte, text="OUI" if reponse else "NON", width=64, height=30, corner_radius=15,
                     fg_color=fond, text_color=couleur,
                     font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=2, padx=14)

        self.journal.append(f"{phi} : conséquence {mode} → {'OUI' if reponse else 'NON'}{note}")
        self._defiler_en_bas()

    def message_accueil(self):
        self.ajouter_message("Saisissez des faits (W) et des défauts (D), ou chargez un exemple "
                             "depuis le menu « Exemples », puis cliquez sur « Générer les extensions ».")

   
    # Petits outils
  
    def rafraichir_listes(self):
        """Recopie la théorie (self.base) dans les deux listes affichées."""
        self.liste_w.remplir([f"{i}. {fait}" for i, fait in enumerate(self.base.facts, 1)])
        self.liste_d.remplir([f"d{i} : {d.en_texte()}" for i, d in enumerate(self.base.defauts, 1)])

    def theorie_modifiee(self):
        """Après toute modification, les extensions calculées ne sont plus valables."""
        self.extensions = None
        self.rafraichir_listes()

    def changer_theme(self):
        ctk.set_appearance_mode("dark" if self.interrupteur.get() else "light")

    def _occupe(self, oui):
        try:
            self.configure(cursor="watch" if oui else "")
            self.update_idletasks()
        except Exception:
            pass

   
    # Zone W : les faits
    
    def ajouter_formule(self):
        texte = self.entree_formule.get().strip()
        try:
            parser_formule(texte)            # le parseur vérifie la syntaxe
        except ValueError as erreur:
            messagebox.showerror("Formule incorrecte", str(erreur))
            return
        self.base.facts.append(texte)
        self.entree_formule.delete(0, "end")
        self.theorie_modifiee()

    def supprimer_formule(self):
        index = self.liste_w.selection()
        if index is None:
            messagebox.showinfo("Supprimer", "Cliquez d'abord sur une formule dans la liste.")
            return
        del self.base.facts[index]
        self.theorie_modifiee()

    def verifier_coherence(self):
        if not self.base.facts:
            self.ajouter_message("W est vide : il est cohérent.", "ok")
        elif est_coherent(self.base.facts):
            self.ajouter_message("W est cohérent (il a au moins un modèle).", "ok")
        else:
            self.ajouter_message("W est INCOHÉRENT : aucune interprétation ne le rend vrai.", "alerte")


    # Zone D : les défauts

    def ajouter_defaut(self):
        prerequis = self.entree_prerequis.get().strip()
        justifs = self.entree_justifs.get().strip()
        conclusion = self.entree_conclusion.get().strip()
        texte = f"{prerequis} : {justifs} / {conclusion}"   # forme attendue par le parseur
        try:
            defaut, avertissements = parser_defaut(texte)
        except ValueError as erreur:
            messagebox.showerror("Défaut incorrect", str(erreur))
            return
        if avertissements:
            messagebox.showwarning("Avertissement", "\n".join(avertissements))
        self.base.defauts.append(defaut)
        for entree in (self.entree_prerequis, self.entree_justifs, self.entree_conclusion):
            entree.delete(0, "end")
        self.theorie_modifiee()

    def supprimer_defaut(self):
        index = self.liste_d.selection()
        if index is None:
            messagebox.showinfo("Supprimer", "Cliquez d'abord sur un défaut dans la liste.")
            return
        del self.base.defauts[index]
        self.theorie_modifiee()

    # Calcul et questions
   
    def generer_extensions(self):
        self._occupe(True)
        try:
            self.extensions = calculer_extensions(self.base)
        except Exception as erreur:   # sécurité : l'application ne doit pas planter
            self.extensions = None
            messagebox.showerror("Erreur de calcul", str(erreur))
            return
        finally:
            self._occupe(False)
        self.afficher_extensions()

    def afficher_extensions(self):
        self.effacer_resultats()
        if not self.extensions:
            self.ajouter_message("Aucune extension.", "alerte")
            return
        n = len(self.extensions)
        self.ajouter_titre(f"{n} extension{'s' if n > 1 else ''} trouvée{'s' if n > 1 else ''}")
        for numero, extension in enumerate(self.extensions, 1):
            self.ajouter_carte_extension(numero, extension)

    def tester(self, mode):
        """mode = « sceptique » ou « crédule »."""
        if self.extensions is None:
            messagebox.showwarning("Extensions", "Générez d'abord les extensions.")
            return
        phi = self.entree_phi.get().strip()
        if not phi:
            messagebox.showwarning("Formule", "Saisissez une formule φ.")
            return
        try:
            if mode == "sceptique":
                reponse = est_consequence_sceptique(self.extensions, phi)
            else:
                reponse = est_consequence_credule(self.extensions, phi)
        except ValueError as erreur:
            messagebox.showerror("Formule incorrecte", str(erreur))
            return
        self.ajouter_reponse(phi, mode, reponse, sans_extension=not self.extensions)

    # ------------------------------------------------------------------
    # Nouveau / Ouvrir / Enregistrer / Exemples
    # ------------------------------------------------------------------
    def nouveau(self):
        if (self.base.facts or self.base.defauts) and not messagebox.askyesno(
                "Nouveau", "Effacer la théorie actuelle ?"):
            return
        self.base = BaseDeConnaissance()
        self.theorie_modifiee()
        self.effacer_resultats()
        self.message_accueil()

    def ouvrir(self):
        chemin = filedialog.askopenfilename(title="Ouvrir une théorie", filetypes=TYPES_FICHIER)
        if not chemin:
            return
        try:
            base, extensions = charger(chemin)
        except (OSError, ValueError) as erreur:
            messagebox.showerror("Ouverture impossible", str(erreur))
            return
        self.base = base
        self.rafraichir_listes()
        self.extensions = extensions
        if extensions is None:
            self.effacer_resultats()
            self.ajouter_message("Théorie chargée. Cliquez sur « Générer les extensions ».")
        else:
            self.afficher_extensions()

    def enregistrer(self):
        chemin = filedialog.asksaveasfilename(title="Enregistrer la théorie",
                                              defaultextension=".json", filetypes=TYPES_FICHIER)
        if not chemin:
            return
        try:
            sauvegarder(chemin, self.base, self.extensions)
        except OSError as erreur:
            messagebox.showerror("Enregistrement impossible", str(erreur))
            return
        self.ajouter_message(f"Théorie enregistrée : {chemin}", "ok")

    def _choix_exemple(self, nom):
        self.menu_exemples.set("Exemples")   # le menu redevient « Exemples » : on peut rechoisir
        self.charger_exemple(nom)

    def charger_exemple(self, nom):
        exemple = EXEMPLES[nom]
        self.base = base_depuis_textes(exemple["faits"], exemple["defauts"])
        self.theorie_modifiee()
        self.effacer_resultats()
        self.ajouter_titre(f"Exemple « {nom} »")
        self.ajouter_message(exemple["description"])
        self.ajouter_message("Cliquez maintenant sur « Générer les extensions ».")


def lancer():
    Application().mainloop()