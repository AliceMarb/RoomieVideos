import modal

MINUTES = 60
MODEL_ID = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
MODEL_DIR = "/models"
OUTPUT_DIR = "/outputs"

app = modal.App("wan-video")

model_volume = modal.Volume.from_name("wan-model-cache", create_if_missing=True)
output_volume = modal.Volume.from_name("wan-video-outputs", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install(
        "torch>=2.4.0",
        "torchvision>=0.19.0",
        "diffusers>=0.31.0",
        "transformers>=4.49.0,<=4.51.3",
        "accelerate>=1.1.1",
        "imageio[ffmpeg]",
        "imageio-ffmpeg",
        "sentencepiece",
        "ftfy",
        "Pillow",
        "numpy<2",
    )
    .env({"HF_HUB_CACHE": MODEL_DIR})
)


@app.cls(
    image=image,
    gpu="A100",
    timeout=15 * MINUTES,
    scaledown_window=10 * MINUTES,
    volumes={MODEL_DIR: model_volume, OUTPUT_DIR: output_volume},
)
class WanVideo:
    @modal.enter()
    def load_model(self):
        import torch
        from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
        from diffusers.utils import export_to_video

        self.export_to_video = export_to_video

        vae = AutoencoderKLWan.from_pretrained(
            MODEL_ID, subfolder="vae", torch_dtype=torch.float32
        )
        self.pipe = WanImageToVideoPipeline.from_pretrained(
            MODEL_ID, vae=vae, torch_dtype=torch.bfloat16
        )
        self.pipe.to("cuda")
        print("Model loaded.")

    @modal.method()
    def generate(
        self,
        image_bytes: bytes,
        prompt: str,
        num_frames: int = 81,
        guidance_scale: float = 5.0,
        num_inference_steps: int = 30,
        seed: int = 42,
    ) -> bytes:
        import io
        import torch
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        max_area = 480 * 832
        aspect = image.width / image.height
        height = int((max_area / aspect) ** 0.5)
        width = int(height * aspect)
        height = (height // 16) * 16
        width = (width // 16) * 16
        image = image.resize((width, height))

        output = self.pipe(
            image=image,
            prompt=prompt,
            height=height,
            width=width,
            num_frames=num_frames,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=torch.Generator("cuda").manual_seed(seed),
        )

        video_path = f"{OUTPUT_DIR}/output.mp4"
        self.export_to_video(output.frames[0], video_path, fps=16)
        output_volume.commit()

        with open(video_path, "rb") as f:
            return f.read()

    @modal.fastapi_endpoint(method="POST", docs=True)
    async def web(self, request: dict):
        import base64

        image_bytes = base64.b64decode(request["image_b64"])
        prompt = request.get("prompt", "")
        num_frames = request.get("num_frames", 81)
        seed = request.get("seed", 42)

        video_bytes = self.generate.local(
            image_bytes, prompt, num_frames=num_frames, seed=seed,
        )

        return {
            "video_b64": base64.b64encode(video_bytes).decode(),
            "status": "ok",
        }


@app.local_entrypoint()
def main(
    image_path: str = "test.png",
    prompt: str = "Animate this image with natural motion",
    output_path: str = "output/wan_output.mp4",
):
    from pathlib import Path

    img = Path(image_path)
    if not img.exists():
        print(f"Error: {img} not found")
        return

    print(f"Sending {img} to Wan2.2...")
    video_bytes = WanVideo().generate.remote(
        img.read_bytes(), prompt,
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(video_bytes)
    print(f"Done: {out} ({len(video_bytes) / 1024 / 1024:.1f} MB)")
