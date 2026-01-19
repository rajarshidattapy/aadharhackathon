import argparse
from pathlib import Path

from .merge import build_final_dataset


def write_csv(df, output_path: str, index: bool = False) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=index)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean, merge, and aggregate UIDAI Aadhaar datasets.")
    parser.add_argument(
        "--enrol-dir",
        default="api_data_aadhar_enrolment",
        help="Directory containing enrolment CSV chunks.",
    )
    parser.add_argument(
        "--demo-dir",
        default="api_data_aadhar_demographic",
        help="Directory containing demographic CSV chunks.",
    )
    parser.add_argument(
        "--bio-dir",
        default="api_data_aadhar_biometric",
        help="Directory containing biometric CSV chunks.",
    )
    parser.add_argument(
        "--output",
        default="merged_aadhaar_data.csv",
        help="Output CSV file path for merged dataset.",
    )

    args = parser.parse_args(argv)

    df = build_final_dataset(args.enrol_dir, args.demo_dir, args.bio_dir)
    write_csv(df, args.output, index=False)

    print(f"Wrote merged dataset with shape {df.shape} to {args.output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

