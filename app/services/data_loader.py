import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


class DataLoader:
    """Load and manage local legal datasets"""

    def __init__(self):
        # Base dataset directory
        self.base_dir = Path(r"C:\Users\Bindu\Downloads\CARA Bot\dataset")

        # Dataset paths
        self.cuad_dir = self.base_dir / "CUAD_v1"
        self.indian_acts_dir = self.base_dir / "annotatedCentralActs"

        self.cuad_data: Optional[Dict] = None
        self.indian_acts: Optional[List[Dict]] = None

    # ---------------------------
    # CUAD DATASET
    # ---------------------------
    def load_cuad_dataset(self) -> Dict:
        """
        Load CUAD dataset from local directory.
        Expected: JSON files inside CUAD_v1 folder
        """
        print("Loading CUAD dataset from local disk...")

        if not self.cuad_dir.exists():
            print(f"⚠️ CUAD directory not found: {self.cuad_dir}")
            print("Continuing without CUAD data.")
            self.cuad_data = {"contracts": [], "count": 0}
            return self.cuad_data

        cuad_records = []

        for json_file in self.cuad_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                cuad_records.append(data)

        self.cuad_data = {
            "contracts": cuad_records,
            "count": len(cuad_records)
        }

        print(f"✅ Loaded {len(cuad_records)} CUAD contracts")
        return self.cuad_data

    # ---------------------------
    # INDIAN CENTRAL ACTS
    # ---------------------------
    def load_indian_acts(self) -> List[Dict]:
        """
        Load Indian Central Acts from local directory.
        Expected: JSON files inside annotatedCentralActs folder
        """
        print("Loading Indian Central Acts from local disk...")

        if not self.indian_acts_dir.exists():
            print(f"⚠️ Indian Acts directory not found: {self.indian_acts_dir}")
            print("Continuing without local acts data — LLM will use its own legal knowledge.")
            self.indian_acts = []
            return []

        acts = []

        for json_file in self.indian_acts_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                act = json.load(f)
                act["_source_file"] = json_file.name
                acts.append(act)

        self.indian_acts = acts
        print(f"✅ Loaded {len(acts)} Indian Central Acts")
        return acts

    # ---------------------------
    # CLAUSE EXAMPLES (CUAD)
    # ---------------------------
    def get_clause_examples(self, clause_type: str, limit: int = 10) -> List[str]:
        """
        Get example clauses of a specific type from CUAD.
        NOTE: This assumes CUAD JSON structure contains clause labels.
        """
        if not self.cuad_data:
            self.load_cuad_dataset()

        examples = []

        for contract in self.cuad_data["contracts"]:
            clauses = contract.get("clauses", [])
            for clause in clauses:
                if clause.get("type", "").lower() == clause_type.lower():
                    examples.append(clause.get("text", ""))
                    if len(examples) >= limit:
                        return examples

        return examples

    # ---------------------------
    # SEARCH INDIAN ACTS
    # ---------------------------
    def search_acts(self, keyword: str) -> List[Dict]:
        """
        Search Indian Acts by keyword
        """
        if not self.indian_acts:
            self.load_indian_acts()

        keyword = keyword.lower()
        results = []

        for act in self.indian_acts:
            if keyword in json.dumps(act).lower():
                results.append(act)

        return results