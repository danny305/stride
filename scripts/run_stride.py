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

    stride = Stride()

    # stride.input_file = PDB_DIR / "part_001/AF-A0A016VMT3-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_001/AF-A0A015LDF4-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_052/AF-A0A0N8KN46-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_075/AF-A0A090SFX8-F1-model_v4.pdb"
    # stride.input_file = PDB_DIR / "part_001/AF-A0A013VRS2-F1-model_v4.pdb"
    stride.input_file = PDB_DIR / "part_001/AF-A0A023XN37-F1-model_v4.pdb"

    stride.assign_ss()
    pprint(stride.ss)


if __name__ == "__main__":

    # runtime()
    test()
