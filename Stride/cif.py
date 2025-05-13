from pathlib import Path
from typing import Optional
from tempfile import TemporaryDirectory

import gemmi

from Stride import Stride
from Stride.utils import convert_cif_to_pdb

class CifStride(Stride):

    @property
    def input_file(self):
        return self._input_file

    @input_file.setter
    def input_file(self, filepath: Path):
        assert isinstance(
            filepath, Path
        ), f"input_file must be a Path object: {filepath}"
        assert filepath.is_file(), f"input_file not found: {filepath.resolve()}"
        assert (
            filepath.suffix in {".cif", ".pdb"}
        ), f"input_file must be a PDB or CIF file: {filepath}"  # test if STRIDE works with cif file
        self._input_file = filepath

    def add_stride_to_cif(self, **kwargs) -> None:
        assert self.cif_file.is_file(), f"cif not found: {self.cif_file.resolve()}"

        doc = gemmi.cif.read_file(str(self.cif_file))
        block = doc.sole_block()

        # Create a new category in the CIF block for stride data
        loop = block.init_loop(
            "_stride.", 
            ["auth_asym_id", "label_seq_id", "auth_seq_id", "auth_comp_id", "ss_id", "ss_full_name"]
        )

        for res_metadata in self._res_metadata:
            loop.add_row(res_metadata)

        self.output_dir = kwargs.get("output_dir", self.output_dir)

        if self.output_dir is not None:
            out_cif = self.output_dir / self.cif_file.name
            out_cif = out_cif.with_suffix(".stride.cif")
            self.output_dir.mkdir(0o774, parents=True, exist_ok=True)

        else:
            out_cif = self.cif_file.with_suffix(".stride.cif")

        doc.write_file(str(out_cif), gemmi.cif.Style.Aligned)

        print(f"Stride data added to CIF file: {out_cif.resolve()}")

    def assign_ss(
        self,
        input_file: Optional[Path] = None,
        output_file: Optional[Path] = None,
        tmp_dir: Optional[TemporaryDirectory] = None,
        **kwargs,
    ) -> None:

        if input_file is not None:
            self.input_file = input_file

        assert (
            self.input_file.is_file()
        ), f"input_file not found: {self.input_file.resolve()}"

        # TODO refactor to use a temp directory
        if self.input_file.suffix == ".cif":
            self.cif_file = self.input_file
            self.pdb_file = convert_cif_to_pdb(self.cif_file, tmp_dir)

        super().assign_ss(
            input_file=self.pdb_file, output_file=self.output_file, **kwargs
        )

        # self.add_stride_to_cif()
