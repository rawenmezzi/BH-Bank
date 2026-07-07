"""
analyzer.py

Module d'analyse de la question utilisateur.

Rôle :
- Nettoyer la question
- Extraire les mots-clés
- Détecter les tables concernées
- Détecter la période
- Détecter le type de requête
- Retourner un objet structuré
"""

import re


class QuestionAnalyzer:

    def __init__(self):

        # Mots vides français
        self.stop_words = {
            "le", "la", "les", "de", "du", "des", "un", "une",
            "et", "ou", "dans", "sur", "par", "pour", "avec",
            "au", "aux", "en", "ce", "cette", "ces",
            "quel", "quelle", "quels", "quelles",
            "est", "sont", "a", "ont", "fait",
            "faire", "donne", "donner", "affiche",
            "afficher", "liste", "moi","ci"
        }

        # Correspondance mot → table
        self.table_keywords = {

            "client": "CUSTOMER",
            "clients": "CUSTOMER",

            "compte": "ACCOUNT",
            "comptes": "ACCOUNT",

            "transaction": "TRANSACTION",
            "transactions": "TRANSACTION",

            "carte": "CARD",
            "cartes": "CARD",

            "agence": "BRANCH",
            "agences": "BRANCH",

            "solde": "BALANCE_HISTORY",
            "historique": "BALANCE_HISTORY"
        }

    # ----------------------------------------------------

    def clean_text(self, question):

        question = question.lower()

        question = re.sub(r"[^\w\s]", " ", question)

        words = question.split()

        keywords = [
            word
            for word in words
            if word not in self.stop_words
        ]

        return keywords

    # ----------------------------------------------------

    def detect_tables(self, keywords):

        tables = []

        for word in keywords:

            if word in self.table_keywords:

                table = self.table_keywords[word]

                if table not in tables:
                    tables.append(table)

        return tables

    # ----------------------------------------------------

    def detect_period(self, question):

        q = question.lower()

        if "aujourd" in q:
            return "aujourd'hui"

        if "hier" in q:
            return "hier"

        if "ce mois" in q:
            return "mois en cours"

        if "mois dernier" in q:
            return "mois précédent"

        if "cette année" in q:
            return "année en cours"

        if "année dernière" in q:
            return "année précédente"

        return None

    # ----------------------------------------------------

    def detect_query_type(self, question):

        q = question.lower()

        if any(word in q for word in [
            "combien",
            "nombre",
            "count"
        ]):
            return "COUNT"

        if any(word in q for word in [
            "moyenne",
            "average"
        ]):
            return "AVG"

        if any(word in q for word in [
            "maximum",
            "max",
            "plus grand"
        ]):
            return "MAX"

        if any(word in q for word in [
            "minimum",
            "min"
        ]):
            return "MIN"

        return "SELECT"

    # ----------------------------------------------------

    def analyze(self, question):

        keywords = self.clean_text(question)

        analysis = {

            "question_originale": question,

            "mots_cles": keywords,

            "tables": self.detect_tables(keywords),

            "periode": self.detect_period(question),

            "type_requete": self.detect_query_type(question)

        }

        return analysis