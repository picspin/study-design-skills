import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).parents[1] / "skills/study-design-skills" / "scripts"
sys.path.insert(0, str(SCRIPTS))
MODULE_SPEC = importlib.util.spec_from_file_location("jev_review", SCRIPTS / "jev_review.py")
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(MODULE)


class JevReviewTests(unittest.TestCase):
    def test_route_preserves_confirmed_design_and_records_judgment(self):
        source = {
            "proposal": "National cross-sectional questionnaire of blood-culture practices",
            "confirmed_design": "descriptive_observational",
        }

        def response(payload):
            criteria = payload["questions"]["study_design"]["criteria"]
            self.assertIn("descriptive_observational", criteria)
            return {
                "model": "jev-test",
                "answers": {"study_design": {
                    "type": "choice",
                    "choice": "descriptive_observational",
                    "probabilities": {"descriptive_observational": 0.9, "insufficient_information": 0.1},
                    "confidence": 0.8,
                }},
            }

        result = MODULE.route_judgment(source, response)
        self.assertEqual(result["selected_design"], "descriptive_observational")
        self.assertEqual(result["status"], "confirmed_design_preserved")

    def test_benchmark_uses_atomic_scores(self):
        def response(payload):
            self.assertEqual(len(payload["questions"]), 4)
            return {
                "model": "jev-test",
                "answers": {
                    key: {"type": "score", "score": 2.0, "confidence": 0.7, "probabilities": {"2": 1.0}}
                    for key in payload["questions"]
                },
            }

        result = MODULE.benchmark_judgment({
            "study_title": "Survey",
            "study_type": "Cross-sectional survey",
            "confirmed_design": "descriptive_observational",
            "primary_objective": "Estimate collection practices",
            "population": "Survey respondents",
        }, response)
        self.assertEqual(result["jev_score_10"], 5.0)
        self.assertEqual(result["status"], "completed")

    def test_unmapped_design_is_flagged_without_overriding_confirmed_route(self):
        def response(payload):
            self.assertIn("outside_current_registry", payload["questions"]["study_design"]["criteria"])
            return {"model": "jev-test", "answers": {"study_design": {
                "type": "choice", "choice": "outside_current_registry", "confidence": 0.9,
                "probabilities": {"outside_current_registry": 0.9},
            }}}

        result = MODULE.route_judgment({
            "proposal": "A specialized non-clinical experimental study",
            "confirmed_design": "descriptive_observational",
        }, response)
        self.assertEqual(result["selected_design"], "descriptive_observational")
        self.assertTrue(result["needs_route_extension"])


if __name__ == "__main__":
    unittest.main()
