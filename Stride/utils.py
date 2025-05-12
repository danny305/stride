from pathlib import Path
from typing import Optional
from tempfile import TemporaryDirectory

import gemmi



def convert_cif_to_pdb(cif: Path, temp_dir: Optional[TemporaryDirectory] = None) -> Path:
    assert isinstance (cif, Path), f"cif must be a Path object: {cif}"
    assert cif.is_file(), f"cif not found: {cif.resolve()}"
    assert cif.suffix == ".cif", f"cif must be a cif file: {cif}"

    cif = cif.resolve()

    if temp_dir is None:
        out_pdb = cif.with_suffix(".pdb")

    else:
        assert isinstance(temp_dir, TemporaryDirectory), f"temp_dir must be a TemporaryDirectory object: {temp_dir}"
        out_pdb = Path(temp_dir.name) / cif.with_suffix(".pdb").name

    st = gemmi.read_structure(str(cif))

    st.write_pdb(str(out_pdb))

    return out_pdb
