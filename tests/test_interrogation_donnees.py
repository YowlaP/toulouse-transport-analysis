import unittest
import sys
from pathlib import Path

# Ajouter le dossier src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from interrogation_donnees import *

class TestInterrogationDonnees(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ici, vous devez charger vos fichiers de tests.
        # Par exemple, s'ils se nomment test1.csv, test2.csv et test3.csv dans le répertoire courant :
        try:
            cls.s_1 = charger_csv("test1.csv")
        except Exception:
            # Sinon, on définit des données par défaut pour les tests
            cls.s_1 = [
                {'a': '1', 'b': 'Alice'},
                {'a': '2', 'b': 'Bob'},
                {'a': '3', 'b': 'Alice'}
            ]
        try:
            cls.s_2 = charger_csv("test2.csv")
        except Exception:
            cls.s_2 = [
                {'id': '1', 'score': '10'},
                {'id': '2', 'score': '20'},
                {'id': '3', 'score': '15'}
            ]
        try:
            cls.s_3 = charger_csv("test3.csv")
        except Exception:
            cls.s_3 = [
                {'id_etudiant': '1', 'nom': 'Dupont', 'prenom': 'Jean', 'age': '20 '},
                {'id_etudiant': '2', 'nom': 'Martin', 'prenom': 'Marie', 'age': '23'},
                {'id_etudiant': '3', 'nom': 'Durand', 'prenom': 'Paul', 'age': '21'}
            ]

class TestProjectionSimple(unittest.TestCase):

    def test_extraction_normal(self):
        data = [{'col1': 'A', 'col2': 'B'}, {'col1': 'C', 'col2': 'D'}]
        expected = [{'col1': 'A'}, {'col1': 'C'}]
        self.assertEqual(projection_simple(data, 'col1'), expected)

    def test_missing_column(self):
        data = [{'col1': 'A'}, {'col2': 'B'}]
        expected = [{'col1': 'A'}]
        self.assertEqual(projection_simple(data, 'col1'), expected)

    def test_empty_list(self):
        data = []
        expected = []
        self.assertEqual(projection_simple(data, 'col1'), expected)

    def test_all_rows_present(self):
        data = [{'col': 'X'}, {'col': 'Y'}, {'col': 'Z'}]
        expected = [{'col': 'X'}, {'col': 'Y'}, {'col': 'Z'}]
        self.assertEqual(projection_simple(data, 'col'), expected)

class TestProjectionSimpleDistinct(unittest.TestCase):

    def test_distinct_integers(self):
        data = [{'id': '1'}, {'id': '2'}, {'id': '1'}, {'id': '3'}]
        expected = [{'id': 1}, {'id': 2}, {'id': 3}]
        self.assertEqual(projection_simple_distinct(data, 'id'), expected)

    def test_distinct_strings(self):
        data = [{'name': 'Alice'}, {'name': 'Bob'}, {'name': 'Alice'}]
        expected = [{'name': 'Alice'}, {'name': 'Bob'}]
        self.assertEqual(projection_simple_distinct(data, 'name'), expected)

    def test_mixed_conversion(self):
        data = [{'val': '10'}, {'val': ' 10 '}, {'val': '20'}, {'val': 'abc'}, {'val': 'abc'}]
        expected = [{'val': 10}, {'val': 20}, {'val': 'abc'}]
        self.assertEqual(projection_simple_distinct(data, 'val'), expected)

    def test_missing_key(self):
        data = [{'a': '1'}, {'a': '2'}]
        expected = []
        self.assertEqual(projection_simple_distinct(data, 'b'), expected)

class TestProjectionMultiple(unittest.TestCase):

    def test_multiple_columns_normal(self):
        data = [{'a': '1', 'b': 'X', 'c': 'foo'}, {'a': '2', 'b': 'Y', 'c': 'bar'}]
        expected = [{'a': '1', 'b': 'X'}, {'a': '2', 'b': 'Y'}]
        self.assertEqual(projection_multiple(data, ['a', 'b']), expected)

    def test_multiple_columns_missing(self):
        data = [{'a': '1', 'b': 'X'}, {'a': '2', 'c': 'bar'}]
        expected = [{'a': '1', 'b': 'X'}, {'a': '2'}]
        self.assertEqual(projection_multiple(data, ['a', 'b']), expected)

    def test_multiple_columns_empty(self):
        data = []
        expected = []
        self.assertEqual(projection_multiple(data, ['a', 'b']), expected)

    def test_all_columns_present(self):
        data = [{'a': '1', 'b': 'X'}, {'a': '2', 'b': 'Y'}, {'a': '3', 'b': 'Z'}]
        expected = [{'a': '1', 'b': 'X'}, {'a': '2', 'b': 'Y'}, {'a': '3', 'b': 'Z'}]
        self.assertEqual(projection_multiple(data, ['a', 'b']), expected)

    def test_extra_keys_ignored(self):
        data = [{'a': '1', 'b': 'X', 'c': 'foo'}, {'a': '2', 'b': 'Y', 'd': 'bar'}]
        expected = [{'a': '1', 'b': 'X'}, {'a': '2', 'b': 'Y'}]
        self.assertEqual(projection_multiple(data, ['a', 'b']), expected)

class TestSelectionSimple(unittest.TestCase):
    def test_equals(self):
        data = [
            {'id': 1, 'value': 10},
            {'id': 2, 'value': 20},
            {'id': 3, 'value': 10},
        ]
        expected = [
            {'id': 1, 'value': 10},
            {'id': 3, 'value': 10},
        ]
        self.assertEqual(selection_simple(data, 'value', '=', 10), expected)

    def test_not_equals(self):
        data = [
            {'id': 1, 'value': 10},
            {'id': 2, 'value': 20},
            {'id': 3, 'value': 10},
        ]
        expected = [
            {'id': 2, 'value': 20},
        ]
        self.assertEqual(selection_simple(data, 'value', '!=', 10), expected)

    def test_greater_than(self):
        data = [
            {'id': 1, 'value': 5},
            {'id': 2, 'value': 15},
            {'id': 3, 'value': 10},
        ]
        expected = [
            {'id': 2, 'value': 15},
        ]
        self.assertEqual(selection_simple(data, 'value', '>', 10), expected)

    def test_less_than_or_equal(self):
        data = [
            {'id': 1, 'value': 5},
            {'id': 2, 'value': 15},
            {'id': 3, 'value': 10},
        ]
        expected = [
            {'id': 1, 'value': 5},
            {'id': 3, 'value': 10},
        ]
        self.assertEqual(selection_simple(data, 'value', '<=', 10), expected)

class TestSelectionMultiple(unittest.TestCase):
    def test_and_condition(self):
        data = [
            {'id': 1, 'value': 10, 'flag': 'yes'},
            {'id': 2, 'value': 20, 'flag': 'no'},
            {'id': 3, 'value': 10, 'flag': 'yes'},
        ]
        conditions = [('value', '=', 10), ('flag', '=', 'yes')]
        expected = [
            {'id': 1, 'value': 10, 'flag': 'yes'},
            {'id': 3, 'value': 10, 'flag': 'yes'},
        ]
        self.assertEqual(selection_multiple(data, conditions, 'AND'), expected)

    def test_or_condition(self):
        data = [
            {'id': 1, 'value': 10, 'flag': 'yes'},
            {'id': 2, 'value': 20, 'flag': 'no'},
            {'id': 3, 'value': 10, 'flag': 'yes'},
        ]
        conditions = [('value', '=', 20), ('flag', '=', 'yes')]
        # Ici, la première ligne (value==10 et flag=='yes') satisfait la condition flag=='yes',
        # la deuxième (value==20) satisfait value==20, et la troisième flag=='yes'.
        expected = data
        self.assertEqual(selection_multiple(data, conditions, 'OR'), expected)


class TestCalculs(unittest.TestCase):

    # Tests pour minimum
    def test_minimum_normal(self):
        data = [
            {'score': '10'},
            {'score': '20'},
            {'score': '5'}
        ]
        self.assertEqual(minimum(data, 'score'), 5)

    def test_minimum_with_whitespace(self):
        data = [
            {'score': ' 10 '},
            {'score': '  20 '},
            {'score': '  5 '}
        ]
        self.assertEqual(minimum(data, 'score'), 5)

    def test_minimum_mixed_numeric(self):
        data = [
            {'score': '10'},
            {'score': '20.5'},
            {'score': '5'},
            {'score': 'abc'}  # non convertible, ignorée
        ]
        self.assertEqual(minimum(data, 'score'), 5)

    def test_minimum_all_invalid(self):
        data = [
            {'score': None},
            {'score': ''},
            {'score': '   '}
        ]
        self.assertIsNone(minimum(data, 'score'))

    # Tests pour maximum
    def test_maximum_normal(self):
        data = [
            {'score': '10'},
            {'score': '20'},
            {'score': '5'}
        ]
        self.assertEqual(maximum(data, 'score'), 20)

    def test_maximum_with_whitespace(self):
        data = [
            {'score': ' 10 '},
            {'score': ' 20 '},
            {'score': ' 5 '}
        ]
        self.assertEqual(maximum(data, 'score'), 20)

    def test_maximum_mixed_numeric(self):
        data = [
            {'score': '10'},
            {'score': '20.5'},
            {'score': '5'},
            {'score': 'abc'}  # ignorée
        ]
        self.assertEqual(maximum(data, 'score'), 20.5)

    def test_maximum_all_invalid(self):
        data = [
            {'score': None},
            {'score': ''},
            {'score': '   '}
        ]
        self.assertIsNone(maximum(data, 'score'))

    # Tests pour somme
    def test_somme_normal(self):
        data = [
            {'score': '10'},
            {'score': '20.5'},
            {'score': '30'}
        ]
        # 10 + 20.5 + 30 = 60.5
        self.assertEqual(somme(data, 'score'), 60.5)

    def test_somme_with_whitespace(self):
        data = [
            {'score': ' 10 '},
            {'score': '20'},
            {'score': ' 30 '}
        ]
        self.assertEqual(somme(data, 'score'), 60)

    def test_somme_mixed(self):
        data = [
            {'score': '10'},
            {'score': '20.5'},
            {'score': '5.5'},
            {'score': 'abc'}  # ignorée
        ]
        self.assertEqual(somme(data, 'score'), 36.0)

    def test_somme_all_invalid(self):
        data = [
            {'score': None},
            {'score': ''},
            {'score': '   '}
        ]
        self.assertIsNone(somme(data, 'score'))

    # Tests pour compte
    def test_compte_normal(self):
        data = [
            {'name': 'Alice'},
            {'name': ''},
            {'name': 'Bob'},
            {'name': None},
            {'name': 'Charlie'}
        ]
        # Seules "Alice", "Bob" et "Charlie" sont valides → 3
        self.assertEqual(compte(data, 'name'), 3)

    def test_compte_with_whitespace(self):
        data = [
            {'name': ' Alice '},
            {'name': '   '},
            {'name': 'Bob'}
        ]
        self.assertEqual(compte(data, 'name'), 2)

    def test_compte_all_invalid(self):
        data = [
            {'name': None},
            {'name': ''},
            {'name': '   '}
        ]
        self.assertIsNone(compte(data, 'name'))

    def test_compte_key_missing(self):
        data = [{'other': 'x'}, {'other': 'y'}]
        self.assertIsNone(compte(data, 'name'))

    # Tests pour moyenne
    def test_moyenne_normal(self):
        data = [
            {'score': '10'},
            {'score': '20'},
            {'score': '30'}
        ]
        self.assertEqual(moyenne(data, 'score'), 20)

    def test_moyenne_floats(self):
        data = [
            {'score': '10.5'},
            {'score': '20.5'},
            {'score': '30.0'}
        ]
        self.assertAlmostEqual(moyenne(data, 'score'), 20.333333333333332)

    def test_moyenne_mixed(self):
        data = [
            {'score': '10'},
            {'score': '20.5'},
            {'score': '30'},
            {'score': 'abc'}  # ignorée
        ]
        self.assertAlmostEqual(moyenne(data, 'score'), 20.166666666666668)

    def test_moyenne_all_invalid(self):
        data = [
            {'score': None},
            {'score': ''},
            {'score': '   '}
        ]
        self.assertIsNone(moyenne(data, 'score'))

# --- Tests pour ordonne ---
class TestOrdonne(unittest.TestCase):

    def test_ascending(self):
        data = [{'id': '3', 'name': 'Charlie'},
                {'id': '1', 'name': 'Alice'},
                {'id': '2', 'name': 'Bob'}]
        expected = [{'id': 1, 'name': 'Alice'},
                    {'id': 2, 'name': 'Bob'},
                    {'id': 3, 'name': 'Charlie'}]
        self.assertEqual(ordonne(data, 'id', 'croissant'), expected)

    def test_descending(self):
        data = [{'id': '3', 'name': 'Charlie'},
                {'id': '1', 'name': 'Alice'},
                {'id': '2', 'name': 'Bob'}]
        expected = [{'id': 3, 'name': 'Charlie'},
                    {'id': 2, 'name': 'Bob'},
                    {'id': 1, 'name': 'Alice'}]
        self.assertEqual(ordonne(data, 'id', 'decroissant'), expected)

    def test_empty_list(self):
        data = []
        expected = []
        self.assertEqual(ordonne(data, 'id', 'croissant'), expected)

    def test_same_values(self):
        data = [{'id': '1', 'name': 'Alice'},
                {'id': '1', 'name': 'Bob'}]
        expected = [{'id': 1, 'name': 'Alice'},
                    {'id': 1, 'name': 'Bob'}]
        self.assertEqual(ordonne(data, 'id', 'croissant'), expected)

    def test_non_numeric_sort(self):
        data = [{'name': 'Charlie'},
                {'name': 'Alice'},
                {'name': 'Bob'}]
        expected = [{'name': 'Alice'},
                    {'name': 'Bob'},
                    {'name': 'Charlie'}]
        self.assertEqual(ordonne(data, 'name', 'croissant'), expected)


# --- Tests pour ordonne_multiple ---
class TestOrdonneMultiple(unittest.TestCase):

    def test_multiple_criteria_ascending(self):
        data = [
            {'id': '2', 'name': 'Bob', 'age': '25'},
            {'id': '1', 'name': 'Alice', 'age': '30'},
            {'id': '3', 'name': 'Alice', 'age': '20'}
        ]
        # Tous les critères triés par ordre croissant :
        # Par 'name' : "Alice" < "Bob" ; parmi les "Alice", 20 < 30.
        expected = [
            {'id': 3, 'name': 'Alice', 'age': 20},
            {'id': 1, 'name': 'Alice', 'age': 30},
            {'id': 2, 'name': 'Bob', 'age': 25}
        ]
        result = ordonne_multiple(data, ['name', 'age'], 'croissant')
        self.assertEqual(result, expected)

    def test_multiple_criteria_descending(self):
        data = [
            {'id': '2', 'name': 'Bob', 'age': '25'},
            {'id': '1', 'name': 'Alice', 'age': '30'},
            {'id': '3', 'name': 'Alice', 'age': '20'}
        ]
        # Tous les critères triés par ordre décroissant :
        # Par 'name' : "Bob" > "Alice" ; parmi les "Alice", 30 > 20.
        expected = [
            {'id': 2, 'name': 'Bob', 'age': 25},
            {'id': 1, 'name': 'Alice', 'age': 30},
            {'id': 3, 'name': 'Alice', 'age': 20}
        ]
        result = ordonne_multiple(data, ['name', 'age'], 'decroissant')
        self.assertEqual(result, expected)

    def test_empty_list(self):
        data = []
        expected = []
        result = ordonne_multiple(data, ['name', 'age'], 'croissant')
        self.assertEqual(result, expected)

    def test_same_values(self):
        data = [
            {'id': '1', 'name': 'Alice', 'age': '30'},
            {'id': '2', 'name': 'Alice', 'age': '30'}
        ]
        expected = [
            {'id': 1, 'name': 'Alice', 'age': 30},
            {'id': 2, 'name': 'Alice', 'age': 30}
        ]
        result = ordonne_multiple(data, ['name', 'age'], 'croissant')
        self.assertEqual(result, expected)

    def test_non_numeric_sort(self):
        data = [
            {'id': '1', 'name': 'Charlie'},
            {'id': '2', 'name': 'Alice'},
            {'id': '3', 'name': 'Bob'}
        ]
        # Tri par 'name' en ordre croissant (après conversion, les chaînes restent inchangées)
        expected = [
            {'id': 2, 'name': 'Alice'},
            {'id': 3, 'name': 'Bob'},
            {'id': 1, 'name': 'Charlie'}
        ]
        result = ordonne_multiple(data, ['name'], 'croissant')
        self.assertEqual(result, expected)


# --- Tests pour jointure ---
class TestJointure(unittest.TestCase):

    def test_basic_join(self):
        s1 = [{'id': '1', 'name': 'Alice'},
              {'id': '2', 'name': 'Bob'},
              {'id': '3', 'name': 'Charlie'}]
        s2 = [{'id': '1', 'score': '10'},
              {'id': '2', 'score': '20'},
              {'id': '4', 'score': '30'}]
        expected = [{'id': 1, 'name': 'Alice', 'score': '10'},
                    {'id': 2, 'name': 'Bob', 'score': '20'}]
        self.assertEqual(jointure(s1, s2, 'id'), expected)

    def test_no_match(self):
        s1 = [{'id': '1', 'name': 'Alice'}]
        s2 = [{'id': '2', 'score': '20'}]
        expected = []
        self.assertEqual(jointure(s1, s2, 'id'), expected)

    def test_multiple_matches(self):
        s1 = [{'id': '1', 'name': 'Alice'},
              {'id': '1', 'name': 'Alice'}]
        s2 = [{'id': '1', 'score': '10'},
              {'id': '1', 'score': '15'}]
        expected = [{'id': 1, 'name': 'Alice', 'score': '10'},
                    {'id': 1, 'name': 'Alice', 'score': '15'},
                    {'id': 1, 'name': 'Alice', 'score': '10'},
                    {'id': 1, 'name': 'Alice', 'score': '15'}]
        self.assertEqual(jointure(s1, s2, 'id'), expected)

    def test_type_conversion(self):
        s1 = [{'id': '1', 'name': 'Alice'},
              {'id': '2', 'name': 'Bob'}]
        s2 = [{'id': '1', 'score': '10'},
              {'id': '2', 'score': '20'}]
        expected = [{'id': 1, 'name': 'Alice', 'score': '10'},
                    {'id': 2, 'name': 'Bob', 'score': '20'}]
        self.assertEqual(jointure(s1, s2, 'id'), expected)

    def test_missing_key(self):
        s1 = [{'id': '1', 'name': 'Alice'},
              {'id': '2', 'name': 'Bob'}]
        s2 = [{'id': '3', 'score': '30'}]
        expected = []
        self.assertEqual(jointure(s1, s2, 'id'), expected)  
   

if __name__ == '__main__':
    # Traiter les arguments CSV s'ils sont fournis
    if len(sys.argv) > 1:
        if len(sys.argv) < 4:
            print("Usage: python test_interrogation_donnees.py fichier1.csv fichier2.csv fichier3.csv")
            sys.exit(1)
        
        # Extraire les chemins des fichiers
        fichier1 = sys.argv[1]
        fichier2 = sys.argv[2]
        fichier3 = sys.argv[3]
        
        # Supprimer les arguments pour éviter les conflits avec unittest
        sys.argv = sys.argv[:1]
    
    # Lancer les tests
    unittest.main()