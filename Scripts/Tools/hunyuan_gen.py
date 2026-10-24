"""
Image -> 3D mesh with a local Hunyuan3D-2 (shape only; colours come later in Blender).

Runs with the Hunyuan3D virtual environment, not the project Python:

    D:\\AI\\Hunyuan3D-2\\.venv\\Scripts\\python.exe Scripts/Tools/hunyuan_gen.py <image> <out.glb> [--crop x0 y0 x1 y1]
        [--faces 40000] [--steps 50] [--octree 384] [--seed 1234]

--crop cuts a region of the concept (pixels of the original image) before generation, so one object
can be taken from a sheet with several views. The background is removed automatically.
"""

import argparse
import os
import time

os.environ.setdefault("HF_HOME", r"D:\AI\hf-cache")
# hy3dgen keeps its weights here (downloaded once, ~5 GB for the shape model).
os.environ.setdefault("HY3DGEN_MODELS", r"D:\AI\hy3dgen-models")

import torch  # noqa: E402
from PIL import Image  # noqa: E402

from hy3dgen.rembg import BackgroundRemover  # noqa: E402
from hy3dgen.shapegen import DegenerateFaceRemover, FaceReducer, FloaterRemover, Hunyuan3DDiTFlowMatchingPipeline  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("output")
    parser.add_argument("--crop", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    parser.add_argument("--faces", type=int, default=40000, help="Target triangle count after reduction")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--octree", type=int, default=384, help="Surface extraction resolution")
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGB")
    if args.crop:
        image = image.crop(tuple(args.crop))
    image = BackgroundRemover()(image)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    preview = os.path.splitext(args.output)[0] + "_input.png"
    image.save(preview)

    started = time.time()
    pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")
    mesh = pipeline(
        image=image,
        num_inference_steps=args.steps,
        octree_resolution=args.octree,
        generator=torch.manual_seed(args.seed),
    )[0]
    mesh = FloaterRemover()(mesh)
    mesh = DegenerateFaceRemover()(mesh)
    mesh = FaceReducer()(mesh, max_facenum=args.faces)

    mesh.export(args.output)
    print("saved %s (%d faces) in %.0f s, input preview %s" % (args.output, len(mesh.faces), time.time() - started, preview))


if __name__ == "__main__":
    main()
