import unittest
from unittest.mock import MagicMock, patch
from src.reasoning.orchestrator import ReasoningOrchestrator
from src.reasoning.strategy import StrategyInput
from src.output.generator import ReportGenerator

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.strategy = StrategyInput(
            objective="Test Acquisition",
            time_horizon_months=12,
            risk_tolerance="medium"
        )

    @patch("src.reasoning.orchestrator.OllamaClient")
    @patch("src.reasoning.orchestrator.GraphConnector")
    def test_end_to_end_workflow(self, MockGraph, MockOllama):
        # Setup Mocks
        mock_llm = MockOllama.return_value
        mock_graph = MockGraph.return_value
        
        # Mock LLM generating Cypher
        mock_llm.generate.side_effect = [
            "MATCH (c:Company) RETURN c",  # 1. Cypher generation
            "Based on the analysis, Company X matches the criteria. Revenue is $10M [node_1]." # 2. Report draft
        ]
        
        # Mock Graph returning data
        mock_graph.run_query.return_value = [
            {"n": {"id": "node_1", "name": "Company X", "revenue": 10000000}}
        ]

        # Initialize Orchestrator
        orchestrator = ReasoningOrchestrator()
        
        # Run Generation
        report = orchestrator.generate_report(self.strategy, "Evaluate Company X")
        
        # Validation
        self.assertIsNotNone(report)
        self.assertIn("Company X", report)
        self.assertIn("$10M", report)
        self.assertIn("[node_1]", report) # Traceability check

        # Verify formatting
        generator = ReportGenerator()
        final_md = generator.format_to_markdown(report, self.strategy, validation_status=True)
        self.assertIn("**Status:** ✅ VERIFIED", final_md)
        self.assertNotIn("Expected revenue", final_md)

    def test_validation_failure(self):
        validator = ReasoningOrchestrator().validator
        text = "Company X has $50M revenue [invalid_node]." # Invalid reference!
        allowed_numbers = {50000000.0}
        valid_refs = {"node_1"}
        
        self.assertFalse(validator.validate(text, allowed_numbers, valid_refs))

    def test_validation_success(self):
        validator = ReasoningOrchestrator().validator
        text = "Company X has $50M revenue [node_1]."
        allowed_numbers = {50000000.0}
        valid_refs = {"node_1"}
        
        self.assertTrue(validator.validate(text, allowed_numbers, valid_refs))

if __name__ == "__main__":
    unittest.main()
