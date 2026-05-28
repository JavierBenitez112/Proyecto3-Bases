import unittest
from src.solver import armar_rompecabezas
from src.db import Neo4jConnection
from src.loader import cargar_puzzle
import json


class TestSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conn = Neo4jConnection()
        cls.session = conn.session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def test_puzzle_exists(self):
        result = self.session.run("""
            MATCH (p:Puzzle {id:'puzzle_excavator'})
            RETURN p.nombre as nombre
        """).single()
        self.assertIsNotNone(result)
        self.assertEqual(result['nombre'], 'Excavator')

    def test_piezas_loaded(self):
        result = self.session.run("""
            MATCH (p:Pieza {cluster_id:'cluster_excavator_1'})
            RETURN count(p) as total
        """).single()
        self.assertEqual(result['total'], 10)

    def test_conexiones_exist(self):
        result = self.session.run("""
            MATCH (a:Pieza)-[r:CONECTA_CON]->(b:Pieza)
            WHERE a.cluster_id = 'cluster_excavator_1'
            RETURN count(r) as total
        """).single()
        self.assertGreater(result['total'], 0)

    def test_clusters_exist(self):
        result = self.session.run("""
            MATCH (c:Cluster)-[:PERTENECE_A]->(p:Puzzle)
            RETURN count(c) as total_clusters
        """).single()
        self.assertGreater(result['total_clusters'], 0)

    def test_multi_cluster_support(self):
        result = self.session.run("""
            MATCH (c:Cluster)-[:PERTENECE_A]->(p:Puzzle {id:'puzzle_monsters'})
            RETURN count(c) as clusters
        """).single()
        self.assertEqual(result['clusters'], 3)


if __name__ == '__main__':
    unittest.main()
