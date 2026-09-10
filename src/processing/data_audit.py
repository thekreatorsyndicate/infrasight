import json
from datetime import datetime
from pathlib import Path
from typing import Any
from collections import Counter, defaultdict

import pandas as pd


class DataAuditor:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.report_lines = []
        self.data = {}

    def load_dataset(self, name: str, data: list[dict[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame(data)
        self.data[name] = df
        return df

    def analyze_field_dictionary(self, df: pd.DataFrame, name: str) -> dict:
        info = {
            "dataset": name,
            "record_count": len(df),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "null_percentages": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            "unique_counts": df.nunique().to_dict(),
            "sample_values": {},
        }

        for col in df.columns:
            non_null = df[col].dropna()
            if len(non_null) > 0:
                info["sample_values"][col] = non_null.head(5).tolist()

        return info

    def analyze_amount_fields(self, df: pd.DataFrame, amount_columns: list[str]) -> dict:
        results = {}
        for col in amount_columns:
            if col in df.columns:
                series = pd.to_numeric(df[col], errors="coerce")
                results[col] = {
                    "count": series.notna().sum(),
                    "null_count": series.isna().sum(),
                    "min": float(series.min()) if series.notna().any() else None,
                    "max": float(series.max()) if series.notna().any() else None,
                    "mean": float(series.mean()) if series.notna().any() else None,
                    "median": float(series.median()) if series.notna().any() else None,
                    "negative_count": int((series < 0).sum()),
                    "zero_count": int((series == 0).sum()),
                }
        return results

    def analyze_date_fields(self, df: pd.DataFrame, date_columns: list[str]) -> dict:
        results = {}
        for col in date_columns:
            if col in df.columns:
                parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
                results[col] = {
                    "count": parsed.notna().sum(),
                    "null_count": parsed.isna().sum(),
                    "min": parsed.min().isoformat() if parsed.notna().any() else None,
                    "max": parsed.max().isoformat() if parsed.notna().any() else None,
                    "sample_formats": df[col].dropna().head(10).tolist(),
                }
        return results

    def analyze_id_fields(self, df: pd.DataFrame, id_columns: list[str]) -> dict:
        results = {}
        for col in id_columns:
            if col in df.columns:
                unique_count = df[col].nunique()
                total_count = len(df)
                duplicate_count = total_count - unique_count
                duplicate_values = df[col].value_counts()
                top_duplicates = duplicate_values[duplicate_values > 1].head(10).to_dict()
                results[col] = {
                    "total_records": total_count,
                    "unique_count": int(unique_count),
                    "duplicate_count": int(duplicate_count),
                    "duplicate_rate": round(duplicate_count / total_count * 100, 2) if total_count > 0 else 0,
                    "top_duplicates": {str(k): int(v) for k, v in top_duplicates.items()},
                }
        return results

    def analyze_workid_joins(self) -> dict:
        if "recommended" not in self.data or "completed" not in self.data or "expenditure" not in self.data:
            return {"error": "Not all datasets loaded"}

        rec_workids = set(self.data["recommended"].get("workId", pd.Series()).dropna().astype(str))
        comp_workids = set(self.data["completed"].get("workId", pd.Series()).dropna().astype(str))
        exp_workids = set(self.data["expenditure"].get("workId", pd.Series()).dropna().astype(str))

        all_workids = rec_workids | comp_workids | exp_workids

        join_results = {
            "recommended": {
                "count": len(rec_workids),
                "in_completed": len(rec_workids & comp_workids),
                "in_expenditure": len(rec_workids & exp_workids),
                "in_both": len(rec_workids & comp_workids & exp_workids),
                "only_in_recommended": len(rec_workids - comp_workids - exp_workids),
            },
            "completed": {
                "count": len(comp_workids),
                "in_recommended": len(comp_workids & rec_workids),
                "in_expenditure": len(comp_workids & exp_workids),
                "in_both": len(comp_workids & rec_workids & exp_workids),
                "only_in_completed": len(comp_workids - rec_workids - exp_workids),
            },
            "expenditure": {
                "count": len(exp_workids),
                "in_recommended": len(exp_workids & rec_workids),
                "in_completed": len(exp_workids & comp_workids),
                "in_both": len(exp_workids & rec_workids & comp_workids),
                "only_in_expenditure": len(exp_workids - rec_workids - comp_workids),
            },
            "overall": {
                "total_unique_workids": len(all_workids),
                "in_all_three": len(rec_workids & comp_workids & exp_workids),
                "in_two_or_more": len(
                    (rec_workids & comp_workids) |
                    (rec_workids & exp_workids) |
                    (comp_workids & exp_workids)
                ),
            }
        }

        return join_results

    def generate_report(self) -> str:
        lines = [
            f"# Data Quality Report — Run {self.run_id}",
            f"",
            f"Generated: {datetime.utcnow().isoformat()}Z",
            f"",
        ]

        for name, df in self.data.items():
            lines.extend([
                f"## Dataset: {name}",
                f"",
                f"- **Records**: {len(df)}",
                f"- **Columns**: {len(df.columns)}",
                f"",
                f"### Field Dictionary",
                f"",
            ])

            field_info = self.analyze_field_dictionary(df, name)
            for col in df.columns:
                lines.append(f"#### {col}")
                lines.append(f"- Type: {field_info['dtypes'].get(col, 'unknown')}")
                lines.append(f"- Nulls: {field_info['null_counts'].get(col, 0)} ({field_info['null_percentages'].get(col, 0):.1f}%)")
                lines.append(f"- Unique: {field_info['unique_counts'].get(col, 0)}")
                samples = field_info['sample_values'].get(col, [])
                if samples:
                    lines.append(f"- Samples: {', '.join(str(s) for s in samples[:3])}")
                lines.append(f"")

        if all(k in self.data for k in ["recommended", "completed", "expenditure"]):
            lines.extend([
                f"## WorkID Join Analysis",
                f"",
            ])
            join_analysis = self.analyze_workid_joins()
            for ds_name, stats in join_analysis.items():
                if ds_name == "overall":
                    continue
                lines.append(f"### {ds_name.capitalize()}")
                for k, v in stats.items():
                    lines.append(f"- {k}: {v}")
                lines.append(f"")

            lines.append(f"### Overall")
            for k, v in join_analysis.get("overall", {}).items():
                lines.append(f"- {k}: {v}")

        return "\n".join(lines)

    def save_report(self, output_dir: Path = None) -> Path:
        if output_dir is None:
            output_dir = Path("reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"data_quality_{self.run_id}.md"
        report_content = self.generate_report()
        report_path.write_text(report_content)
        return report_path


def run_data_audit(run_id: str, datasets: dict[str, list[dict]]) -> Path:
    auditor = DataAuditor(run_id)
    for name, data in datasets.items():
        auditor.load_dataset(name, data)
    return auditor.save_report()