import argparse
import glob
import sys
import os

from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Helix import Helix


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Compress hcut.",
        epilog="Example: %(prog)s data/HL-31_H1.yaml data/*.yaml",
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        help='Path(s) to input YAML file(s); glob patterns (e.g. "data/*.yaml") are supported',
    )
    parser.add_argument("--ratio", help="Compress ratio", type=float, default=0.9)

    args = parser.parse_args()

    cwd = os.getcwd()

    # Import after parsing so `--help` does not trigger package init logging.
    import python_magnetgeo as pmg

    # Expand glob patterns and collect all matching files
    files = []
    for pattern in args.input_files:
        matched = glob.glob(pattern)
        if matched:
            files.extend(matched)
        else:
            print(f"Warning: no files matched: {pattern}", file=sys.stderr)

    if not files:
        print("Error: no input files found.", file=sys.stderr)
        sys.exit(1)

    pmg.verify_class_registration()

    errors = 0
    for input_file in files:
        # basename =
        # dirname =
        obj = pmg.load(input_file)
        print(f"\nLoad {input_file}", flush=True)

        # test if obj is an Helix
        # if not quit

        hcut = obj.getModelAxi()
        turns, pitch = hcut.compact()
        print(f"Original hcut: {len(hcut.pitch)}", flush=True)
        print(f"Compacted hcut: {len(pitch)}", flush=True)
        nhcut = ModelAxi(name="compacted", h=hcut.h, turns=turns, pitch=pitch)
        assert hcut.get_Nturns() == nhcut.get_Nturns()

        print(f"Compact hcut: {len(nhcut.pitch)}", flush=True)

        nhelix = Helix(
            f"{obj.name}-compressed",
            obj.r,
            obj.z,
            obj.cutwidth,
            obj.odd,
            obj.dble,
            nhcut,
            obj.model3d,
            obj.shape,
            obj.chamfers,
            obj.grooves,
        )
        print(f"Create new helix with compacted hcut")

        # save as yaml

        new_pitch = [args.ratio * p for p in nhcut.pitch]

        # create new heliw with compressed hcut
        new_modelaxi = ModelAxi(
            name="compressed",
            h=args.ratio * obj.modelaxi.h,
            turns=nhcut.turns,
            pitch=new_pitch,
        )
        new_helix = Helix(
            f"{obj.name}-compressed",
            obj.r,
            obj.z,
            obj.cutwidth,
            obj.odd,
            obj.dble,
            new_modelaxi,
            obj.model3d,
            obj.shape,
            obj.chamfers,
            obj.grooves,
        )

        # save as yaml
        new_helix.write_to_yaml(directory=cwd)

        # create hcut without shape
        # create hcut with shape for Salome, Catia and CAD
        for format in ["lncmi", "salome", "catia"]:
            new_helix.generate_cut(format=format)


if __name__ == "__main__":
    main()
