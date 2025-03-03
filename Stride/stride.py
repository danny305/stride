#!/usr/bin/env python

from pathlib import Path
from typing import Any, Optional
from itertools import groupby
import re
import os
import subprocess

import torch


class Stride:
    input_file: Optional[Path] = None
    output_file: Optional[Path] = None
    binary: Optional[Path] = None
    _ss = dict()

    remove_file = True

    def __init__(
        self,
        input_file: Optional[Path] = None,
        output_file: Optional[Path] = None,
        binary: Optional[Path] = None,
        keep_file: bool = False,
        use_cache: bool = False,
        verbose: bool = False,
    ):

        assert isinstance(keep_file, bool), f" must be a boolean: {keep_file}"
        assert isinstance(use_cache, bool), f"use_cache must be a boolean: {use_cache}"
        assert isinstance(verbose, bool), f"verbose must be a boolean: {verbose}"

        self.remove_file = not keep_file
        self.use_cache = use_cache
        self.verbose = verbose

        if input_file is not None:
            self.input_file = input_file

        if output_file is not None:
            assert isinstance(
                output_file, Path
            ), f"output_file must be a Path object: {output_file}"
            self.remove_file = False
            self.output_file = output_file

        if binary is not None:
            self.binary = binary
        else:
            self._binary = "stride"
            if self.verbose:
                print(
                    f"No binary provided, using system level stride binary: {self._binary}"
                )

        self._ss = dict(
            filename=self.input_file.name,
            one_letter_string="",
            formatted_string="",
            tensor=None,
            tensor_map=None,
            ss_counts=dict(
                n_helix=0,
                n_strand=0,
                n_turn=0,
                n_coil=0,
            ),
            ss_lens=dict(),
        )

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
            filepath.suffix == ".pdb"
        ), f"input_file must be a PDB file: {filepath}"  # test if STRIDE works with cif file
        self._input_file = filepath

    @property
    def ss(self) -> dict[str, Any]:
        return self._ss

    @ss.setter
    def ss(self, ss: dict[str, Any]):
        raise AttributeError("Cannot set ss directly. Use assign_ss() method instead.")

    @property
    def tensor(self):
        return self._ss["tensor"]

    @tensor.setter
    def tensor(self, tensor):
        raise AttributeError(
            "Cannot set tensor directly. Use assign_ss() method instead."
        )

    @property
    def binary(self) -> str:
        return self._binary

    @binary.setter
    def binary(self, bin_path: Path):
        assert isinstance(bin_path, Path), f"binary must be a Path object: {bin_path}"
        assert bin_path.is_file(), f"binary not found: {bin_path.resolve()}"
        self._binary = str(bin_path.resolve())

    def assign_ss(
        self, input_file: Optional[Path] = None, output_file: Optional[Path] = None
    ) -> None:

        if input_file is not None:
            self.input_file = input_file

        if isinstance(output_file, Path) or output_file is None:
            self.output_file = output_file

        else:
            raise TypeError("output_file must be a Path object")

        if self.output_file is None:
            self.output_file = self.input_file.with_suffix(".stride")
        else:
            self.remove_file = False

        cmd = f"{self.binary} {self.input_file} -f{self.output_file}"

        if self.use_cache and self.output_file.is_file():
            if self.verbose:
                print(f"Using cached output file: {self.output_file}")

        else:
            if self.verbose:
                print(f"Running: {cmd}")
            subprocess.call(cmd, shell=True)

        self._ss = dict(
            filename=self.input_file.name,
            one_letter_string=[],
            formatted_string=[],
            tensor=None,
            ss_counts=dict(
                n_helix=0,
                n_strand=0,
                n_turn=0,
                n_coil=0,
            ),
            ss_lens=dict(),
        )

        with open(self.output_file, "r") as f:
            while True:
                line = f.readline()
                if self.verbose:
                    print(line.strip())

                if line == "":
                    break

                line = re.sub("\s\s+", " ", line)
                tokens = line.split(" ")

                if tokens[0] == "REM":
                    continue
                elif tokens[0] == "ASG":
                    self._ss["one_letter_string"].append(tokens[5])

            self._ss["one_letter_string"] = "".join(self._ss["one_letter_string"])

        self._segment_ss()
        self._build_ss_tensor()

        if self.remove_file:
            if self.verbose:
                print(f"Removing: {self.output_file}")

            os.remove(self.output_file)

    def _build_ss_tensor(self) -> None:
        L = len(self._ss["one_letter_string"])
        self._ss["tensor"] = torch.zeros((L, 4))
        self._ss["tensor_map"] = dict()
        for i, ss_type in enumerate(self._ss["one_letter_string"]):
            if ss_type in ["H", "G"]:
                self._ss["tensor"][i, 0] = 1
            elif ss_type in ["E", "B"]:
                self._ss["tensor"][i, 1] = 1
            elif ss_type == "T":
                self._ss["tensor"][i, 2] = 1
            else:
                self._ss["tensor"][i, 3] = 1
            self._ss["tensor_map"][i + 1] = self._ss["tensor"][i, ...]

    def _segment_ss(self) -> None:
        """
        Generate a dictionary of secondary structure segments and their lengths.
        """
        # Group consecutive characters and count their lengths
        self._ss["ss_lens"] = dict()
        self._ss["ss_counts"] = dict()
        self._ss["formatted_string"] = []
        for structure, group in groupby(self._ss["one_letter_string"]):
            segment_length = len(list(group))
            self._ss["formatted_string"] += [f"{structure}{segment_length}"]
            if structure not in self._ss["ss_lens"]:
                self._ss["ss_lens"][structure] = []
            self._ss["ss_lens"][structure].append(segment_length)

        self._ss["formatted_string"] = "-".join(self._ss["formatted_string"])

        self._ss["ss_counts"]["n_helix"] = len(self._ss["ss_lens"].get("H", [])) + len(
            self._ss["ss_lens"].get("G", [])
        )
        self._ss["ss_counts"]["n_strand"] = len(self._ss["ss_lens"].get("E", [])) + len(
            self._ss["ss_lens"].get("B", [])
        )
        self._ss["ss_counts"]["n_turn"] = len(self._ss["ss_lens"].get("T", []))
        self._ss["ss_counts"]["n_coil"] = len(self._ss["ss_lens"].get("C", []))

    @property
    def ss_str(self) -> str:
        return self._ss["one_letter_string"]

    @property
    def formatted_ss_str(self) -> str:
        return self._ss["formatted_string"]

    @property
    def ss_counts(self) -> dict:
        return self._ss["ss_counts"]

    @property
    def ss_lens(self) -> dict:
        return self._ss["ss_lens"]

    @property
    def helix_tensor(self) -> torch.Tensor:
        return self._ss["tensor"][:, 0]

    @property
    def strand_tensor(self) -> torch.Tensor:
        return self._ss["tensor"][:, 1]

    @property
    def turn_tensor(self) -> torch.Tensor:
        return self._ss["tensor"][:, 2]

    @property
    def coil_tensor(self) -> torch.Tensor:
        return self._ss["tensor"][:, 3]

    def residue_ss(self, res_num: int) -> str:
        return self._ss["one_letter_string"][res_num - 1]

    def residue_ss_tensor(self, res_num: int) -> torch.Tensor:
        return self._ss["tensor_map"].get(res_num, torch.zeros(4))
