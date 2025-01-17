from pathlib import Path
import argparse

from Stride import Stride


def cli():
    parser = argparse.ArgumentParser(
        description="STRIDE: Secondary Structure Assignment"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--pdb-file",
        type=Path,
        help="Input PDB file",
    )
    group.add_argument(
        "-d",
        "--directory",
        type=Path,
        help="Directory containing PDB files",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory",
    )

    parser.add_argument(
        "-b",
        "--binary",
        type=Path,
        default=None,
        help="Directory containing the stride binary",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    return args


def main():
    args = cli()

    if args.pdb_file:
        stride = Stride(
            input_file=args.pdb_file,
            output_file=args.output_dir,
            binary=args.binary,
            keep_files=True,
        )
        stride.assign_ss()
    elif args.directory:
        for pdb_file in args.directory.glob("*.pdb"):
            stride = Stride(
                input_file=pdb_file,
                output_file=args.output_dir,
                binary=args.binary,
                bin_dirkeep_files=True,
            )
            stride.assign_ss()


if __name__ == "__main__":
    main()
