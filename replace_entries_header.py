#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import re
from pathlib import Path
import sys
import tempfile
import shutil

def replace_header(src_path: Path, header: str, inplace: bool, suffix: str, encoding: str) -> Path:
    # 出力先の決定
    if inplace:
        dst_path = src_path  # 後で一時ファイルへ書いてから置換
    else:
        dst_path = src_path.with_name(src_path.stem + suffix + src_path.suffix)

    pattern = re.compile(r"^ITEM: ENTRIES ")

    # inplace の場合は tmp→置換
    if inplace:
        with src_path.open("r", encoding=encoding, errors="replace") as fin, \
             tempfile.NamedTemporaryFile("w", delete=False, encoding=encoding) as tmp:
            for line in fin:
                if pattern.match(line):
                    tmp.write(header + "\n")
                else:
                    tmp.write(line)
        shutil.move(tmp.name, src_path)
        return src_path

    # 通常（別ファイル）
    with src_path.open("r", encoding=encoding, errors="replace") as fin, \
         dst_path.open("w", encoding=encoding) as fout:
        for line in fin:
            if pattern.match(line):
                fout.write(header + "\n")
            else:
                fout.write(line)
    return dst_path

def main():
    parser = argparse.ArgumentParser(
        description="Replace the 'ITEM: ENTRIES ...' header line in LIGGGHTS dump files."
    )
    parser.add_argument(
        "-H", "--header", required=True,
        help="Replacement header line (e.g., 'ITEM: ENTRIES x1 y1 ... area')."
    )
    parser.add_argument(
        "inputs", nargs="+",
        help="Input files or glob patterns (e.g., post/forcechain-*.dmp)."
    )
    parser.add_argument(
        "--inplace", action="store_true",
        help="Overwrite files in place (default: write *-renamed files)."
    )
    parser.add_argument(
        "--suffix", default="-renamed",
        help="Suffix for output filenames when not using --inplace (default: -renamed)."
    )
    parser.add_argument(
        "--encoding", default="utf-8",
        help="Text encoding for reading/writing (default: utf-8)."
    )

    args = parser.parse_args()

    # 対象ファイルを展開
    matched = []
    for pat in args.inputs:
        # glob で展開（シェル未展開のケースにも対応）
        expanded = glob.glob(pat)
        if expanded:
            matched.extend(expanded)
        else:
            # パターンがそのままファイル名かも
            p = Path(pat)
            if p.exists():
                matched.append(str(p))
            else:
                print(f"No match: {pat}", file=sys.stderr)

    if not matched:
        print("No input files found.", file=sys.stderr)
        sys.exit(1)

    # 置換処理
    for f in sorted(set(matched)):
        src = Path(f)
        try:
            outp = replace_header(src, args.header, args.inplace, args.suffix, args.encoding)
            print(f"OK: {src} -> {outp}")
        except Exception as e:
            print(f"NG: Error processing {src}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
