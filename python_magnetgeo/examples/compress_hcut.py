import argparse
import glob
import os
import sys

from ..Helix import Helix
from ..ModelAxi import ModelAxi
from ..Shape import Shape
from ..Profile import Profile


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
    parser.add_argument("--ratio", help="Compress ratio", type=float, default=1.0)

    args = parser.parse_args()

    cwd = os.getcwd()

    # Import after parsing so `--help` does not trigger package init logging.
    from .. import load, verify_class_registration

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

    verify_class_registration()

    for input_file in files:
        # basename =
        # dirname =
        obj = load(input_file)
        print(f"\nLoad {input_file}", flush=True)

        # test if obj is an Helix
        # if not quit

        hcut = obj.getModelAxi()
        turns, pitch = hcut.compact()
        print(f"Original hcut: {len(hcut.pitch)}", flush=True)
        print(f"Compacted hcut: {len(pitch)}", flush=True)
        nhcut = ModelAxi(name="compacted", h=hcut.h, turns=turns, pitch=pitch)
        assert (
            abs(1 - hcut.get_Nturns() / nhcut.get_Nturns()) < 1e-6
        ), f"Nturns mismatch after compaction: original={hcut.get_Nturns()}, compacted={nhcut.get_Nturns()}"

        print(f"Compact hcut: {len(nhcut.pitch)}", flush=True)

        Helix(
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
        print("Create new helix with compacted hcut")

        # compress hcut
        new_pitch = [args.ratio * p for p in nhcut.pitch]

        # compress shape
        print(f"Shape: {obj.shape}")
        new_shape = None
        if obj.shape is not None:
            profile = obj.shape.profile
            print(f"Profile: {profile}")
            new_points = [[point[0], point[1] * args.ratio] for point in profile.points]
            new_profile = Profile(
                cad=f"{profile.cad}-compressed", points=new_points, labels=profile.labels
            )

            new_shape = Shape(
                name=f"{obj.shape.name}-compressed",
                profile=new_profile,
                length=obj.shape.length,
                angle=obj.shape.angle,
                onturns=obj.shape.onturns,
                position=obj.shape.position,
            )

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
            obj.shape if new_shape is None else new_shape,
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
