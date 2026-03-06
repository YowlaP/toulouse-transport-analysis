import unittest
import sys
from pathlib import Path

# Ajouter le dossier src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from interrogation_donnees_pandas import *

class TestInterrogationDonneesPandas(unittest.TestCase):
    def setUp(self):
        # DataFrame de test principal
        self.df = pd.DataFrame({
            'A': [1, 2, 2, 3, np.nan, 5],
            'B': ['x', 'y', 'x', 'z', 'x', 'y'],
            'C': [10, 20, 30, 40, 50, 60]
        })
        # DataFrame complémentaire pour les tests de jointure
        self.df_join1 = pd.DataFrame({
            'key': [1, 2, 3, 2],
            'val1': ['a', 'b', 'c', 'd']
        })
        self.df_join2 = pd.DataFrame({
            'key': [2, 2, 3, 4],
            'val2': ['e', 'f', 'g', 'h']
        })
        # Petit DataFrame pour tester les fonctions "distinct"
        self.df_identique = pd.DataFrame({
            'X': [1, 1, 1, 1],
            'Y': ['a', 'a', 'a', 'a']
        })

    # --- Tests pour projection_simple ---
    def test_projection_simple_existant_A(self):
        # Test que la colonne 'A' est bien retournée
        s = projection_simple(self.df, 'A')
        self.assertTrue(isinstance(s, pd.Series))
        pd.testing.assert_series_equal(s, self.df['A'])

    def test_projection_simple_existant_B(self):
        s = projection_simple(self.df, 'B')
        self.assertEqual(s.tolist(), self.df['B'].tolist())

    def test_projection_simple_longueur(self):
        s = projection_simple(self.df, 'C')
        self.assertEqual(len(s), len(self.df))

    def test_projection_simple_column_not_found(self):
        with self.assertRaises(KeyError):
            _ = projection_simple(self.df, 'D')

    def test_projection_simple_dtype(self):
        s = projection_simple(self.df, 'C')
        self.assertTrue(np.issubdtype(s.dtype, np.number))

    # --- Tests pour projection_multiple ---
    def test_projection_multiple_existant_A_B(self):
        df_proj = projection_multiple(self.df, ['A', 'B'])
        expected = self.df[['A', 'B']]
        pd.testing.assert_frame_equal(df_proj, expected)

    def test_projection_multiple_type(self):
        df_proj = projection_multiple(self.df, ['B', 'C'])
        self.assertTrue(isinstance(df_proj, pd.DataFrame))

    def test_projection_multiple_shape(self):
        df_proj = projection_multiple(self.df, ['A', 'C'])
        self.assertEqual(df_proj.shape, (self.df.shape[0], 2))

    def test_projection_multiple_erreur_colonne(self):
        with self.assertRaises(KeyError):
            _ = projection_multiple(self.df, ['A', 'D'])

    def test_projection_multiple_valeurs(self):
        df_proj = projection_multiple(self.df, ['B'])
        self.assertListEqual(df_proj['B'].tolist(), self.df['B'].tolist())

    # --- Tests pour projection_simple_distinct ---
    def test_projection_simple_distinct_B(self):
        s = projection_simple_distinct(self.df, 'B')
        expected = self.df['B'].drop_duplicates()
        pd.testing.assert_series_equal(s.reset_index(drop=True),
                                       expected.reset_index(drop=True))

    def test_projection_simple_distinct_A(self):
        s = projection_simple_distinct(self.df, 'A')
        # Pour A, on s'attend à retrouver [1,2,3, NaN, 5] (l'ordre est préservé)
        expected = self.df['A'].drop_duplicates()
        pd.testing.assert_series_equal(s.reset_index(drop=True),
                                       expected.reset_index(drop=True))

    def test_projection_simple_distinct_type(self):
        s = projection_simple_distinct(self.df, 'B')
        self.assertTrue(isinstance(s, pd.Series))

    def test_projection_simple_distinct_uniques(self):
        s = projection_simple_distinct(self.df_identique, 'X')
        self.assertEqual(len(s.unique()), 1)

    def test_projection_simple_distinct_vide(self):
        df_vide = pd.DataFrame({'Z': []})
        s = projection_simple_distinct(df_vide, 'Z')
        self.assertEqual(len(s), 0)

    # --- Tests pour projection_multiple_distinct ---
    def test_projection_multiple_distinct_existant(self):
        df_proj = projection_multiple_distinct(self.df, ['A', 'B'])
        expected = self.df[['A', 'B']].drop_duplicates()
        pd.testing.assert_frame_equal(df_proj.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_projection_multiple_distinct_type(self):
        df_proj = projection_multiple_distinct(self.df, ['B', 'C'])
        self.assertTrue(isinstance(df_proj, pd.DataFrame))

    def test_projection_multiple_distinct_nombre_colonnes(self):
        df_proj = projection_multiple_distinct(self.df, ['A', 'B'])
        self.assertEqual(df_proj.shape[1], 2)

    def test_projection_multiple_distinct_uniques(self):
        df_proj = projection_multiple_distinct(self.df_identique, ['X', 'Y'])
        self.assertEqual(len(df_proj), 1)

    def test_projection_multiple_distinct_erreur_colonne(self):
        with self.assertRaises(KeyError):
            _ = projection_multiple_distinct(self.df, ['A', 'D'])

    # --- Tests pour selection_simple ---
    def test_selection_simple_egalite(self):
        df_sel = selection_simple(self.df, 'A', '==', 2)
        expected = self.df[self.df['A'] == 2]
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_selection_simple_inegalite(self):
        df_sel = selection_simple(self.df, 'B', '!=', 'x')
        expected = self.df[self.df['B'] != 'x']
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_selection_simple_superieur(self):
        df_sel = selection_simple(self.df, 'C', '>', 25)
        expected = self.df[self.df['C'] > 25]
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_selection_simple_inferieur_egale(self):
        df_sel = selection_simple(self.df, 'C', '<=', 40)
        expected = self.df[self.df['C'] <= 40]
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_selection_simple_string(self):
        df_sel = selection_simple(self.df, 'B', '==', 'y')
        expected = self.df[self.df['B'] == 'y']
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    # --- Tests pour selection_multiple ---
    def test_selection_multiple_and(self):
        conditions = [('A', '>', 1), ('C', '<', 50)]
        df_sel = selection_multiple(self.df, conditions, 'and')
        expected = self.df[(self.df['A'] > 1) & (self.df['C'] < 50)]
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_selection_multiple_or(self):
        conditions = [('A', '==', 2), ('C', '==', 60)]
        df_sel = selection_multiple(self.df, conditions, 'or')
        expected = self.df[(self.df['A'] == 2) | (self.df['C'] == 60)]
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_selection_multiple_condition_unique(self):
        conditions = [('B', '==', 'z')]
        df_sel = selection_multiple(self.df, conditions, 'and')
        expected = self.df[self.df['B'] == 'z']
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_selection_multiple_vide(self):
        conditions = [('A', '>', 100), ('C', '<', 0)]
        df_sel = selection_multiple(self.df, conditions, 'and')
        self.assertEqual(len(df_sel), 0)

    def test_selection_multiple_string(self):
        conditions = [('B', '!=', 'x'), ('B', '==', 'y')]
        df_sel = selection_multiple(self.df, conditions, 'and')
        expected = self.df[(self.df['B'] != 'x') & (self.df['B'] == 'y')]
        pd.testing.assert_frame_equal(df_sel.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    # --- Tests pour minimum ---
    def test_minimum_A(self):
        self.assertEqual(minimum(self.df, 'A'), 1)

    def test_minimum_C(self):
        self.assertEqual(minimum(self.df, 'C'), 10)

    def test_minimum_B(self):
        # Pour une colonne de chaînes, le min renvoie le plus petit en ordre lexicographique
        self.assertEqual(minimum(self.df, 'B'), 'x')

    def test_minimum_identique(self):
        self.assertEqual(minimum(self.df_identique, 'X'), 1)

    def test_minimum_vide(self):
        vide = pd.DataFrame({'Z': []})
        self.assertTrue(np.isnan(minimum(vide, 'Z')))

    # --- Tests pour maximum ---
    def test_maximum_A(self):
        self.assertEqual(maximum(self.df, 'A'), 5)

    def test_maximum_C(self):
        self.assertEqual(maximum(self.df, 'C'), 60)

    def test_maximum_B(self):
        self.assertEqual(maximum(self.df, 'B'), 'z')

    def test_maximum_identique(self):
        self.assertEqual(maximum(self.df_identique, 'Y'), 'a')

    def test_maximum_vide(self):
        vide = pd.DataFrame({'Z': []})
        self.assertTrue(np.isnan(maximum(vide, 'Z')))

    # --- Tests pour compte ---
    def test_compte_A(self):
        # La colonne 'A' contient 5 valeurs non nulles sur 6
        self.assertEqual(compte(self.df, 'A'), 5)

    def test_compte_B(self):
        self.assertEqual(compte(self.df, 'B'), len(self.df))

    def test_compte_identique(self):
        self.assertEqual(compte(self.df_identique, 'X'), 4)

    def test_compte_vide(self):
        vide = pd.DataFrame({'Z': []})
        self.assertEqual(compte(vide, 'Z'), 0)

    def test_compte_type(self):
        self.assertIsInstance(compte(self.df, 'C'), int)

    # --- Tests pour somme ---
    def test_somme_A(self):
        # NaN est ignoré dans la somme
        self.assertEqual(somme(self.df, 'A'), 1 + 2 + 2 + 3 + 5)

    def test_somme_C(self):
        self.assertEqual(somme(self.df, 'C'), sum(self.df['C']))

    def test_somme_vide(self):
        vide = pd.DataFrame({'Z': []})
        self.assertEqual(somme(vide, 'Z'), 0)

    def test_somme_identique(self):
        self.assertEqual(somme(self.df_identique, 'X'), 4)

    def test_somme_type(self):
        self.assertTrue(isinstance(somme(self.df, 'C'), (int, float)))

    # --- Tests pour moyenne ---
    def test_moyenne_A(self):
        # Moyenne de [1, 2, 2, 3, 5] -> (1+2+2+3+5)/5 = 13/5
        self.assertAlmostEqual(moyenne(self.df, 'A'), 13 / 5)

    def test_moyenne_C(self):
        self.assertAlmostEqual(moyenne(self.df, 'C'), sum(self.df['C']) / len(self.df['C']))

    def test_moyenne_identique(self):
        self.assertAlmostEqual(moyenne(self.df_identique, 'X'), 1)

    def test_moyenne_vide(self):
        vide = pd.DataFrame({'Z': []})
        self.assertTrue(np.isnan(moyenne(vide, 'Z')))

    def test_moyenne_type(self):
        self.assertTrue(isinstance(moyenne(self.df, 'C'), float))

    # --- Tests pour ordonne ---
    def test_ordonne_ascendant(self):
        df_sorted = ordonne(self.df, 'A', 'asc')
        expected = self.df.sort_values(by='A', ascending=True)
        pd.testing.assert_frame_equal(df_sorted.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_ordonne_descendant(self):
        df_sorted = ordonne(self.df, 'A', 'desc')
        expected = self.df.sort_values(by='A', ascending=False)
        pd.testing.assert_frame_equal(df_sorted.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_ordonne_string(self):
        df_sorted = ordonne(self.df, 'B', 'asc')
        expected = self.df.sort_values(by='B', ascending=True)
        pd.testing.assert_frame_equal(df_sorted.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_ordonne_inchange_donnees(self):
        # Vérifie que l'ordre de self.df n'est pas modifié par la fonction
        _ = ordonne(self.df, 'C', 'asc')
        self.assertEqual(len(self.df), 6)

    def test_ordonne_type(self):
        df_sorted = ordonne(self.df, 'C', 'asc')
        self.assertTrue(isinstance(df_sorted, pd.DataFrame))

    # --- Tests pour ordonne_multiple ---
    def test_ordonne_multiple_ascendant(self):
        df_sorted = ordonne_multiple(self.df, ['B', 'A'], 'asc')
        expected = self.df.sort_values(by=['B', 'A'], ascending=True)
        pd.testing.assert_frame_equal(df_sorted.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_ordonne_multiple_descendant(self):
        df_sorted = ordonne_multiple(self.df, ['B', 'C'], 'desc')
        expected = self.df.sort_values(by=['B', 'C'], ascending=False)
        pd.testing.assert_frame_equal(df_sorted.reset_index(drop=True),
                                      expected.reset_index(drop=True))

    def test_ordonne_multiple_shape(self):
        df_sorted = ordonne_multiple(self.df, ['A', 'C'], 'asc')
        self.assertEqual(df_sorted.shape, self.df.shape)

    def test_ordonne_multiple_type(self):
        df_sorted = ordonne_multiple(self.df, ['B', 'A'], 'asc')
        self.assertTrue(isinstance(df_sorted, pd.DataFrame))

    def test_ordonne_multiple_valeurs(self):
        df_sorted = ordonne_multiple(self.df_identique, ['X', 'Y'], 'asc')
        # Comme toutes les valeurs sont identiques, le résultat doit être égal à l'original
        pd.testing.assert_frame_equal(df_sorted.reset_index(drop=True),
                                      self.df_identique.reset_index(drop=True))

    # --- Tests pour jointure ---
    def test_jointure_classique(self):
        df_joined = jointure(self.df_join1, self.df_join2, 'key')
        # La jointure interne doit contenir uniquement les lignes dont la clé est présente dans les deux DataFrames
        expected = pd.merge(self.df_join1, self.df_join2, on='key', how='inner')
        pd.testing.assert_frame_equal(df_joined.sort_values(by=['key', 'val1', 'val2']).reset_index(drop=True),
                                      expected.sort_values(by=['key', 'val1', 'val2']).reset_index(drop=True))

    def test_jointure_no_match(self):
        # Test d'une jointure sans correspondance
        df1 = pd.DataFrame({'k': [1, 2], 'val': ['a', 'b']})
        df2 = pd.DataFrame({'k': [3, 4], 'val2': ['c', 'd']})
        df_joined = jointure(df1, df2, 'k')
        self.assertTrue(df_joined.empty)


    def test_jointure_duplication(self):
        # Les clés en double devraient être correctement jointes
        df_joined = jointure(self.df_join1, self.df_join2, 'key')
        self.assertTrue(len(df_joined) >= 1)
        self.assertIn('val1', df_joined.columns)
        self.assertIn('val2', df_joined.columns)

    def test_jointure_type(self):
        df_joined = jointure(self.df_join1, self.df_join2, 'key')
        self.assertTrue(isinstance(df_joined, pd.DataFrame))

    def test_jointure_controle_colonnes(self):
        df_joined = jointure(self.df_join1, self.df_join2, 'key')
        # Vérifie que la colonne de jointure est présente et que toutes les colonnes issues des deux DataFrames le sont également
        expected_cols = set(self.df_join1.columns).union(set(self.df_join2.columns))
        self.assertEqual(set(df_joined.columns), expected_cols)

      
  

if __name__ == '__main__':
    # Vérifier que suffisamment d'arguments ont été fournis
    if len(sys.argv) < 4:
        raise ValueError("Veuillez fournir les chemins des trois fichiers CSV en arguments.")

    # Extraire les chemins des fichiers passés en arguments
    fichier1 = sys.argv[1]
    fichier2 = sys.argv[2]
    fichier3 = sys.argv[3]

    
    # Supprimer les arguments pour éviter les conflits avec unittest
    # Cause: unittest gère ses propres arguments et ne supporte pas les arguments supplémentaires
    sys.argv = sys.argv[:1]
    unittest.main()