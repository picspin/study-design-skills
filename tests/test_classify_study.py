import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "study-design-skills" / "scripts" / "classify_study.py"
SPEC = importlib.util.spec_from_file_location("classify_study", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SAMPLE_SCRIPT = SCRIPT.parent / "sample_size.py"
SAMPLE_SPEC = importlib.util.spec_from_file_location("sample_size", SAMPLE_SCRIPT)
SAMPLE_MODULE = importlib.util.module_from_spec(SAMPLE_SPEC)
SAMPLE_SPEC.loader.exec_module(SAMPLE_MODULE)


class StudyTriageTests(unittest.TestCase):
    def test_parallel_rct_sample_size_reports_analyzable_and_recruited(self):
        result = SAMPLE_MODULE.estimate_sample_size({"sample_size": {
            "method": "parallel_proportions",
            "control_event_rate": 0.25,
            "intervention_event_rate": 0.38,
            "alpha": 0.05,
            "power": 0.80,
            "loss_fraction": 0.15,
        }})
        self.assertEqual(result["status"], "estimated")
        self.assertGreater(result["recruited_n"], result["analyzable_n"])
        self.assertGreater(result["analyzable_n"], 350)

    def test_paired_sample_size_requires_directional_discordance(self):
        result = SAMPLE_MODULE.estimate_sample_size({"sample_size": {
            "method": "paired_binary",
            "discordant_control_only": 0.075,
            "discordant_intervention_only": 0.075,
        }})
        self.assertEqual(result["status"], "assumptions_required")

    def test_paired_imaging_does_not_trigger_ai_overlay(self):
        spec = {
            "proposal": "Prospective paired comparative imaging study with randomized order",
            "confirmed_design": "comparative_diagnostic_accuracy",
            "answers": {
                "primary_aim": "diagnostic_accuracy",
                "diagnostic_comparison": "paired",
                "data_source": "prospective_primary",
                "primary_outcome_family": "accuracy",
                "analysis_unit": "patient",
            },
        }

        result = MODULE.triage(spec)

        self.assertFalse(any("DECIDE-AI" in item for item in result["guideline_overlays"]))

    def test_asks_one_question_first(self):
        result = MODULE.triage({"proposal": "引入LLM智能体质控和监测预警系统，与传统工作流比较不良事件"})
        self.assertEqual(result["stage"], "clarify")
        self.assertEqual(result["next_question"]["id"], "rollout_structure")
        self.assertEqual(result["inferred_answers"]["primary_aim"], "intervention_effect")
        self.assertNotIn("questions", result)

    def test_retrospective_ehr_is_inferred_without_reasking(self):
        spec = {
            "proposal": "回顾性电子病历记录和影像学资料，评价LLM预警系统分阶段上线后的不良事件变化",
            "answers": {"rollout_structure": "nonrandom_staggered", "concurrent_control": "partial"},
        }
        result = MODULE.triage(spec)
        self.assertEqual(result["inferred_answers"]["data_source"], "retrospective_ehr")
        self.assertNotEqual(result["next_question"]["id"], "data_source")

    def test_llm_quality_control_converges_to_cits(self):
        spec = {
            "proposal": "引入LLM智能体质控和监测预警系统，与传统工作流比较不良事件",
            "answers": {
                "primary_aim": "intervention_effect",
                "rollout_structure": "fixed_date_series",
                "concurrent_control": "yes",
                "data_source": "retrospective_ehr",
                "primary_outcome_family": "clinical_safety",
                "analysis_unit": "time_period",
            },
        }
        result = MODULE.triage(spec)
        self.assertEqual(result["recommended_design"]["design_id"], "controlled_interrupted_time_series")
        self.assertIn("SQUIRE 2.0", result["guideline_overlays"])
        self.assertIn("TREND", result["guideline_overlays"])
        self.assertIn("RECORD", result["guideline_overlays"])
        self.assertEqual(result["stage"], "confirm")

    def test_prediction_uses_validation_not_psm(self):
        spec = {
            "proposal": "开发模型预测30天死亡风险",
            "answers": {
                "primary_aim": "prediction",
                "prediction_stage": "development",
                "data_source": "prospective_primary",
                "primary_outcome_family": "prediction_performance",
                "analysis_unit": "patient",
            },
            "confirmed_design": "prediction_model_development",
        }
        result = MODULE.triage(spec)
        self.assertEqual(result["stage"], "ready")
        methods = " ".join(result["recommended_design"]["methods"]).lower()
        self.assertIn("bootstrap", methods)
        self.assertNotIn("propensity", methods)

    def test_comparative_diagnostic_selects_quadas_c(self):
        spec = {
            "proposal": "比较两种影像AI的诊断准确性",
            "answers": {
                "primary_aim": "diagnostic_accuracy",
                "diagnostic_comparison": "paired",
                "data_source": "prospective_primary",
                "primary_outcome_family": "accuracy",
                "analysis_unit": "patient",
            },
            "confirmed_design": "comparative_diagnostic_accuracy",
        }
        result = MODULE.triage(spec)
        self.assertEqual(result["recommended_design"]["design_id"], "comparative_diagnostic_accuracy")
        self.assertIn("QUADAS-C", " ".join(result["recommended_design"]["bias_tools"]))

    def test_systematic_review_uses_characteristics_table(self):
        spec = {
            "proposal": "汇总多篇文献评价干预效果",
            "answers": {"primary_aim": "evidence_synthesis", "review_target": "intervention", "review_scope": "quantitative_meta", "data_source": "published_literature"},
            "confirmed_design": "systematic_review_meta_analysis",
        }
        result = MODULE.triage(spec)
        self.assertEqual(result["stage"], "ready")
        self.assertIn("study-characteristics", result["recommended_design"]["table"])

    def test_user_can_confirm_plausible_alternative(self):
        spec = {
            "proposal": "固定日期上线质控系统并观察多个前后时间点",
            "answers": {
                "primary_aim": "intervention_effect", "rollout_structure": "fixed_date_series",
                "concurrent_control": "no", "data_source": "retrospective_ehr",
                "primary_outcome_family": "clinical_quality", "analysis_unit": "time_period",
            },
            "confirmed_design": "interrupted_time_series",
        }
        result = MODULE.triage(spec)
        self.assertEqual(result["stage"], "ready")
        self.assertEqual(result["recommended_design"]["design_id"], "interrupted_time_series")

    def test_design_study_stops_before_confirmation(self):
        root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(
                ["python3", str(root / "study-design-skills/scripts/design_study.py"), str(root / "examples/llm_quality_proposal.json"), "--out-dir", temp_dir],
                check=True,
                capture_output=True,
                text=True,
            )
            files = {path.name for path in Path(temp_dir).iterdir()}
            self.assertEqual(files, {"study-intake.md", "study-intake.json"})
            result = json.loads((Path(temp_dir) / "study-intake.json").read_text(encoding="utf-8"))
            self.assertEqual(result["next_question"]["id"], "rollout_structure")

    def test_prediction_package_omits_smd(self):
        root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(
                ["python3", str(root / "study-design-skills/scripts/design_study.py"), str(root / "examples/prediction_model_confirmed.json"), "--out-dir", temp_dir, "--formats", "csv,md"],
                check=True,
                capture_output=True,
                text=True,
            )
            csv_path = next(Path(temp_dir).glob("*-table1.csv"))
            header = csv_path.read_text(encoding="utf-8-sig").splitlines()[0]
            self.assertNotIn("SMD", header)
            memo = next(Path(temp_dir).glob("*-memo.md")).read_text(encoding="utf-8")
            self.assertIn("PROBAST+AI", memo)
            self.assertIn("bootstrap", memo.lower())

    def test_systematic_review_package_uses_study_characteristics(self):
        root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(
                ["python3", str(root / "study-design-skills/scripts/design_study.py"), str(root / "examples/systematic_review_confirmed.json"), "--out-dir", temp_dir, "--formats", "xlsx,csv"],
                check=True,
                capture_output=True,
                text=True,
            )
            from openpyxl import load_workbook
            workbook = load_workbook(next(Path(temp_dir).glob("*-package.xlsx")), read_only=True)
            self.assertEqual(workbook.sheetnames[0], "Study Characteristics")
            header = next(Path(temp_dir).glob("*-table1.csv")).read_text(encoding="utf-8-sig").splitlines()[0]
            self.assertIn("Study,Year,Country/setting,Design", header)

    def test_exact_journal_target_outranks_non_ai_specialty_derivative(self):
        root = Path(__file__).parents[1]
        spec = {
            "study_title": "Paired MRI comparison",
            "study_type": "Comparative diagnostic accuracy study",
            "journal": "RADIOLOGY",
            "target_jcr_category": "RADIOLOGY, NUCLEAR MEDICINE & MEDICAL IMAGING",
            "groups": [{"label": "Sequence A"}, {"label": "Sequence B"}],
            "variables": [{"name": "age", "label": "Age", "type": "continuous"}],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            spec_path = Path(temp_dir) / "spec.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            subprocess.run(
                ["python3", str(root / "study-design-skills/scripts/design_study.py"), str(spec_path), "--out-dir", temp_dir, "--formats", "xlsx"],
                check=True,
                capture_output=True,
                text=True,
            )
            from openpyxl import load_workbook
            workbook = load_workbook(next(Path(temp_dir).glob("*-package.xlsx")), read_only=True)
            journal_sheet = workbook["Journal Fit"]
            self.assertEqual(journal_sheet["A5"].value, "RADIOLOGY")


if __name__ == "__main__":
    unittest.main()
