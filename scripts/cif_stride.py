from pathlib import Path
from tempfile import TemporaryDirectory


from Stride import CifStride
from Stride.utils import convert_cif_to_pdb



if __name__=="__main__":
    # Example usage
    cif_file = Path("../data/example/8uke.cif")


    stride = CifStride()
    stride.assign_ss(input_file=cif_file)
    stride.add_stride_to_cif()

    # tmp_dir = TemporaryDirectory()
    # pdb_file = convert_cif_to_pdb(cif_file, tmp_dir)
    # with open(pdb_file, 'r') as file:
    #     for line in file:
    #         print(line.strip())
    # print(f"Converted {cif_file} to {pdb_file}")

