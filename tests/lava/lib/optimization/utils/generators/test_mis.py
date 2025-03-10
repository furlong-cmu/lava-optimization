# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
# See: https://spdx.org/licenses/

import unittest
import numpy as np

from lava.lib.optimization.solvers.generic.solver import OptimizationSolver
from lava.lib.optimization.utils.generators.mis import MISProblem


class TestMISProblem(unittest.TestCase):
    """Unit tests for MISProblem class."""

    def setUp(self):
        self.num_vertices = 10
        self.connection_prob = 0.75
        self.seed = 42
        self.problem = MISProblem(num_vertices=self.num_vertices,
                                  connection_prob=self.connection_prob,
                                  seed=self.seed)

    def test_create_obj(self):
        """Tests correct instantiation of MISProblem object."""
        self.assertIsInstance(self.problem, MISProblem)

    def test_num_vertices_prop(self):
        """Tests correct value of num_vertices property."""
        self.assertEqual(self.problem.num_vertices, self.num_vertices)

    def test_connection_prob_prop(self):
        """Tests correct value of connection_prob property."""
        self.assertEqual(self.problem.connection_prob, self.connection_prob)

    def test_seed_prob(self):
        """Tests correct value of seed property."""
        self.assertEqual(self.problem.seed, self.seed)

    def test_get_graph(self):
        """Tests that the graph contains the correct number of nodes and
        edges."""
        graph = self.problem.get_graph()
        number_of_nodes = 10
        number_of_edges = 37
        self.assertEqual(graph.number_of_nodes(), number_of_nodes)
        self.assertEqual(graph.number_of_edges(), number_of_edges)

    def test_get_graph_matrix(self):
        """Tests the correct adjacency matrix is returned."""
        matrix = self.problem.get_graph_matrix()
        correct_matrix = np.array([[0, 0, 1, 1, 1, 1, 1, 0, 1, 1],
                                   [0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
                                   [1, 0, 0, 1, 1, 0, 1, 1, 1, 1],
                                   [1, 1, 1, 0, 0, 0, 1, 1, 1, 1],
                                   [1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
                                   [1, 1, 0, 0, 1, 0, 1, 1, 1, 1],
                                   [1, 1, 1, 1, 1, 1, 0, 0, 1, 0],
                                   [0, 1, 1, 1, 1, 1, 0, 0, 1, 1],
                                   [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                                   [1, 1, 1, 1, 1, 1, 0, 1, 1, 0]])
        self.assertTrue((correct_matrix == matrix).all())

    def test_get_complement_graph(self):
        """Tests that the complement graph contains the correct number of
        nodes and edges."""
        graph = self.problem.get_complement_graph()
        number_of_nodes = 10
        number_of_edges = 8
        self.assertEqual(graph.number_of_nodes(), number_of_nodes)
        self.assertEqual(graph.number_of_edges(), number_of_edges)

    def test_get_complement_graph_matrix(self):
        """Tests the correct complement graph adjacency matrix is returned."""
        matrix = self.problem.get_complement_graph_matrix()
        correct_matrix = np.array([[0, 1, 0, 0, 0, 0, 0, 1, 0, 0, ],
                                   [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, ],
                                   [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, ],
                                   [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, ],
                                   [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ],
                                   [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, ],
                                   [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, ],
                                   [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, ],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
                                   [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, ]])
        self.assertTrue((correct_matrix == matrix).all())

    def test_get_as_qubo(self):
        """Tests the conversion to QUBO returns the correct cost matrix."""
        w_diag = 1.0
        w_off = 4.0
        qubo = self.problem.get_as_qubo(w_diag, w_off)
        correct_matrix = np.array([[-1, 0, 2, 2, 2, 2, 2, 0, 2, 2],
                                   [0, -1, 0, 2, 2, 2, 2, 2, 2, 2],
                                   [2, 0, -1, 2, 2, 0, 2, 2, 2, 2],
                                   [2, 2, 2, -1, 0, 0, 2, 2, 2, 2],
                                   [2, 2, 2, 0, -1, 2, 2, 2, 2, 2],
                                   [2, 2, 0, 0, 2, -1, 2, 2, 2, 2],
                                   [2, 2, 2, 2, 2, 2, -1, 0, 2, 0],
                                   [0, 2, 2, 2, 2, 2, 0, -1, 2, 2],
                                   [2, 2, 2, 2, 2, 2, 2, 2, -1, 2],
                                   [2, 2, 2, 2, 2, 2, 0, 2, 2, -1]])
        self.assertTrue((correct_matrix == qubo.q).all())

    def test_find_maximum_independent_set(self):
        """Tests the correct maximum independent set is returned."""
        mis = self.problem.find_maximum_independent_set()
        correct_mis = np.array([0, 0, 0, 0, 0, 0, 1, 0, 0, 1])
        self.assertTrue((correct_mis == mis).all())

    def test_qubo_solution(self):
        """Tests that a solution with the optimal cost is found by
        OptimizationSolver with the QUBO formulation."""
        optimal_cost = -2
        qubo = self.problem.get_as_qubo(w_diag=1, w_off=4)

        params = {"timeout": 1000,
                  "target_cost": optimal_cost,
                  "backend": "CPU",
                  "hyperparameters": {
                      "steps_to_fire": 11,
                      "noise_amplitude": 1,
                      "noise_precision": 4,
                      "step_size": 11,
                  }}

        solver = OptimizationSolver(qubo)
        solution = solver.solve(**params)
        self.assertEqual(qubo.evaluate_cost(solution), optimal_cost)


if __name__ == "__main__":
    unittest.main()
