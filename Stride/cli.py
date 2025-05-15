from pathlib import Path
import argparse

from Stride import Stride, CifStride


def cli():
    parser = argparse.ArgumentParser(
        description="STRIDE: Secondary Structure Assignment"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--file",
        type=Path,
        help="Input PDB file",
    )
    group.add_argument(
        "-d",
        "--directory",
        type=Path,
        help="Directory containing PDB files",
    )

    file_type = parser.add_mutually_exclusive_group(required=True)
    file_type.add_argument(
        "-p",
        "--pdb",
        action="store_true",
        help="Input file is a PDB file",
    )

    file_type.add_argument(
        "-c",
        "--cif",
        action="store_true",
        help="Input file is a CIF file",
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
    parser.add_argument(
        "-n",
        "--n_threads",
        type=int,
        default=1,
        help="Number of threads to use",
    )

    args = parser.parse_args()

    return args

# TODO out_file as a directory currently does not work, need to implement
def main():
    args = cli()

    if args.file:
        if args.pdb:
            assert (
                args.file.suffix == ".pdb"
            ), f"Input file must be a PDB file: {args.file}"
            stride = Stride(
                input_file=args.file,
                output_dir=args.output_dir,
                binary=args.binary,
                keep_file=True,
            )
            stride.assign_ss()

        elif args.cif:
            assert (
                args.file.suffix == ".cif"
            ), f"Input file must be a CIF file: {args.file}"
            stride = CifStride(
                input_file=args.file,
                output_dir=args.output_dir,
                binary=args.binary,
                keep_file=True,
            )
            stride.assign_ss()
            stride.add_stride_to_cif()
        else:
            raise ValueError("Unsupported file type. Use --pdb or --cif.")

    elif args.directory:
        if args.pdb:
            for pdb_file in args.directory.glob("*.pdb"):
                stride = Stride(
                    input_file=pdb_file,
                    output_dir=args.output_dir,
                    binary=args.binary,
                    keep_file=True,
                )
                stride.assign_ss()

        elif args.cif:
            if args.n_threads == 1:
                for cif_file in args.directory.glob("*.cif"):
                    stride = CifStride(
                        input_file=cif_file,
                        output_dir=args.output_dir,
                        binary=args.binary,
                        keep_file=True,
                    )
                    stride.assign_ss()
                    stride.add_stride_to_cif()
            else:
                if not "pymp" in dir():
                    import pymp
                cif_files = list(args.directory.glob("*.cif"))
                with pymp.Parallel(args.n_threads) as p:
                    for i in p.range(len(cif_files)):
                        cif_file = cif_files[i]
                        
                        stride = CifStride(
                            input_file=cif_file,
                            output_dir=args.output_dir,
                            binary=args.binary,
                            keep_file=True,
                        )
                        stride.assign_ss()
                        stride.add_stride_to_cif()

        else:
            raise ValueError("Unsupported file type. Use --pdb or --cif.")


if __name__ == "__main__":
    main()
