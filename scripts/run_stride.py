from pathlib import Path
from pprint import pprint
from time import time

from Stride import Stride


def runtime():
    PDB_DIR = Path("/scratch/projects/cgai/ambient_proteins/pdbs")

    pdbs = list(PDB_DIR.glob("part_001/*.pdb"))

    print(len(pdbs))

    times = []
    for i in range(10):
        stride = Stride()
        t_start = time()
        for pdb in pdbs[:100]:
            stride.input_file = pdb
            stride.assign_ss()
            # pprint(stride.ss)
            # print(f"Finished: {pdb.name}")
        times.append(round(time() - t_start, 2))
        print(f"Elapsed time: {time() - t_start:.2f} s")

    print(times)
    print(f"Average time: {sum(times) / len(times):.2f} s")


def test():
    PDB_DIR = Path("/scratch/projects/cgai/ambient_proteins/pdbs")
    TRIM_DIR = Path("/scratch/projects/cgai/ambient_proteins/trimmed_pdbs/588K")

    stride = Stride()

    # stride.input_file = PDB_DIR / "part_001/AF-A0A016VMT3-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_001/AF-A0A015LDF4-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_052/AF-A0A0N8KN46-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_075/AF-A0A090SFX8-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_001/AF-A0A013VRS2-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_001/AF-A0A023XN37-F1-model_v4.pdb"
    stride.input_file = TRIM_DIR / "part_001/AF-A0A023XN37-F1-model_v4_trimmed.pdb"

    stride.assign_ss()
    pprint(stride.ss)

    print(stride.ss_str)
    print(stride.formatted_ss_str)
    print(stride.ss_counts)
    print(stride.ss_lens)
    print(stride.helix_tensor)
    print(stride.strand_tensor)
    print(stride.turn_tensor)
    print(stride.coil_tensor)
    print(stride.residue_ss(10))
    print(stride.residue_ss_tensor(10))


if __name__ == "__main__":

    # runtime()
    test()
