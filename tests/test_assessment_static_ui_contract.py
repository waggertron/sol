import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "assessment-mvp"


class AssessmentStaticUiContractTests(unittest.TestCase):
    def test_html_exposes_administer_and_workbench_controls(self) -> None:
        html = (APP / "index.html").read_text(encoding="utf-8")
        required_ids = [
            "nav-administer",
            "nav-workbench",
            "admin-view",
            "workbench-view",
            "export-current-session",
            "delete-current-session",
            "session-list",
            "workbench-atoms",
            "atom-filter",
        ]
        for element_id in required_ids:
            self.assertIn(f'id="{element_id}"', html)

    def test_css_contains_responsive_layout_guards(self) -> None:
        css = (APP / "styles.css").read_text(encoding="utf-8")
        self.assertIn("[hidden]", css)
        self.assertIn("@media (max-width: 1100px)", css)
        self.assertIn("@media (max-width: 720px)", css)
        self.assertIn(".session-card-header", css)
        self.assertIn("overflow-wrap: anywhere", css)

    def test_atom_editor_contract_is_present(self) -> None:
        script = (APP / "app.js").read_text(encoding="utf-8")
        self.assertIn("atomEditMarkup", script)
        self.assertIn('data-field="claim"', script)
        self.assertIn('data-field="user-note"', script)
        self.assertIn("original_claim", script)
        self.assertIn("review_history", script)
        self.assertIn("applyAtomEdit", script)


if __name__ == "__main__":
    unittest.main()
