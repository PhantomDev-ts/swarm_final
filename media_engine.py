"""
media_engine.py — Z-Image-Turbo + LTX-2.3 GGUF, otimizados para T4 × 2

Mapa de VRAM (32GB total):
  GPU 0: LTX-2.3 GGUF Q4  ~6GB  +  Z-Image-Turbo BF16 ~10GB  = ~16GB
  GPU 1: LTX-2.3 GGUF Q4  ~6GB                                 =  ~6GB
  Sobra: ~10GB para buffer/codecs

Com isso você roda 2 LTX em paralelo + Z-Image simultaneamente.
"""

import os, sys, torch, datetime, concurrent.futures, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    HUGGINGFACE_TOKEN, LTXV_MODEL_ID, ZIMAGE_MODEL_ID,
    LTXV_RESOLUTION, LTXV_NUM_FRAMES, ZIMAGE_RESOLUTION, MEDIA_DIR,
)

MEDIA_DIR.mkdir(parents=True, exist_ok=True)

_zimage_pipe  = None
_ltxv_pipes   = {}          # {0: pipe_gpu0, 1: pipe_gpu1}
_executor     = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# GGUF Q4_K_M — ~6GB VRAM, qualidade quase indistinguível do BF16
LTXV_GGUF_REPO = "city-96/ltx-video-2b-v0.9-gguf"
LTXV_GGUF_FILE = "ltx-video-2b-v0.9-Q4_K_M.gguf"


def _ts() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def _has_gpu(idx: int = 0) -> bool:
    return torch.cuda.is_available() and torch.cuda.device_count() > idx


def vram_free(idx: int = 0) -> float:
    if not _has_gpu(idx):
        return 0.0
    props = torch.cuda.get_device_properties(idx)
    return (props.total_memory - torch.cuda.memory_allocated(idx)) / 1e9


def system_status() -> str:
    lines = ["🖥️  **Status de mídia**"]
    if not torch.cuda.is_available():
        return "⚠️ Sem GPU"
    for i in range(torch.cuda.device_count()):
        p   = torch.cuda.get_device_properties(i)
        use = torch.cuda.memory_allocated(i) / 1e9
        tot = p.total_memory / 1e9
        lines.append(f"  GPU{i} {p.name}: {use:.1f}/{tot:.1f}GB")
    loaded = (
        (["Z-Image-Turbo"] if _zimage_pipe else [])
        + [f"LTX-2.3 GPU{k}" for k in _ltxv_pipes]
    )
    lines.append(f"  Carregados: {', '.join(loaded) or 'nenhum'}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
#  Z-IMAGE-TURBO
# ──────────────────────────────────────────────────────────────────────────────

def _load_zimage():
    global _zimage_pipe
    if _zimage_pipe is not None:
        return _zimage_pipe
    print("📦 Carregando Z-Image-Turbo (BF16)...")
    from diffusers import ZImagePipeline  # type: ignore
    dev = "cuda:0" if _has_gpu(0) else "cpu"
    _zimage_pipe = ZImagePipeline.from_pretrained(
        ZIMAGE_MODEL_ID,
        torch_dtype=torch.bfloat16,
        token=HUGGINGFACE_TOKEN or None,
    ).to(dev)
    _zimage_pipe.enable_model_cpu_offload()
    print(f"✅ Z-Image-Turbo | VRAM livre GPU0: {vram_free(0):.1f}GB")
    return _zimage_pipe


def generate_image(
    prompt: str,
    negative_prompt: str = (
        "blurry, low quality, watermark, text overlay, ugly, AI slop, "
        "generic stock photo, overexposed, noise"
    ),
    width:  int   = ZIMAGE_RESOLUTION[0],
    height: int   = ZIMAGE_RESOLUTION[1],
    steps:  int   = 8,
    guidance_scale: float = 4.5,
    seed:   int   = -1,
) -> str:
    pipe = _load_zimage()
    gen  = None
    if seed >= 0:
        dev = "cuda:0" if _has_gpu(0) else "cpu"
        gen = torch.Generator(device=dev).manual_seed(seed)
    res      = pipe(prompt=prompt, negative_prompt=negative_prompt,
                    width=width, height=height,
                    num_inference_steps=steps,
                    guidance_scale=guidance_scale, generator=gen)
    out      = MEDIA_DIR / "zimage" / f"img_{_ts()}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    res.images[0].save(str(out))
    return str(out)


def generate_images_batch(prompts: list[str], **kw) -> list[str]:
    """Gera N imagens em sequência."""
    return [generate_image(p, **kw) for p in prompts]


# ──────────────────────────────────────────────────────────────────────────────
#  LTX-2.3 — GGUF Q4 (~6GB VRAM por instância)
# ──────────────────────────────────────────────────────────────────────────────

def _ensure_gguf_deps():
    subprocess.run(
        ["pip", "install", "-q", "gguf", "diffusers[torch]"],
        capture_output=True,
    )


def _load_ltxv(device_idx: int = 0):
    if device_idx in _ltxv_pipes:
        return _ltxv_pipes[device_idx]

    print(f"📦 Carregando LTX-2.3 GGUF → GPU{device_idx}...")
    _ensure_gguf_deps()

    dev = f"cuda:{device_idx}" if _has_gpu(device_idx) else "cpu"

    try:
        # Tenta GGUF Q4 — precisa do SingleFileQuantizedPipeline do diffusers ≥0.33
        from diffusers import LTXPipeline  # type: ignore
        from huggingface_hub import hf_hub_download  # type: ignore

        gguf_path = hf_hub_download(
            repo_id=LTXV_GGUF_REPO,
            filename=LTXV_GGUF_FILE,
            token=HUGGINGFACE_TOKEN or None,
        )
        pipe = LTXPipeline.from_single_file(
            gguf_path,
            torch_dtype=torch.bfloat16,
        ).to(dev)
        print(f"  ↳ GGUF Q4 carregado ({vram_free(device_idx):.1f}GB livres)")

    except Exception as e:
        print(f"  ↳ GGUF falhou ({e}), usando BF16 padrão...")
        from diffusers import LTXPipeline  # type: ignore
        pipe = LTXPipeline.from_pretrained(
            LTXV_MODEL_ID,
            torch_dtype=torch.bfloat16,
            token=HUGGINGFACE_TOKEN or None,
        ).to(dev)

    pipe.enable_model_cpu_offload()
    _ltxv_pipes[device_idx] = pipe
    print(f"✅ LTX-2.3 GPU{device_idx} pronto | VRAM livre: {vram_free(device_idx):.1f}GB")
    return pipe


def _valid_frames(n: int) -> int:
    """num_frames deve ser (N×8)+1."""
    valid = [49, 65, 97, 121, 161, 193, 257]
    return min(valid, key=lambda x: abs(x - n))


def generate_video(
    prompt: str,
    negative_prompt: str = (
        "worst quality, inconsistent motion, blurry, jittery, "
        "distorted, AI slop, watermark, text overlay, generic"
    ),
    width:      int   = LTXV_RESOLUTION[0],
    height:     int   = LTXV_RESOLUTION[1],
    num_frames: int   = LTXV_NUM_FRAMES,
    fps:        int   = 24,
    steps:      int   = 40,
    guidance_scale: float = 3.5,
    seed:       int   = -1,
    device_idx: int   = 0,
) -> str:
    """Gera vídeo com LTX-2.3. Retorna caminho do .mp4."""
    num_frames = _valid_frames(num_frames)
    pipe       = _load_ltxv(device_idx)
    dev        = f"cuda:{device_idx}" if _has_gpu(device_idx) else "cpu"

    gen = None
    if seed >= 0:
        gen = torch.Generator(device=dev).manual_seed(seed)

    res = pipe(
        prompt=prompt, negative_prompt=negative_prompt,
        width=width, height=height, num_frames=num_frames,
        num_inference_steps=steps, guidance_scale=guidance_scale,
        generator=gen,
    )
    out = MEDIA_DIR / "ltxv" / f"vid_{_ts()}_gpu{device_idx}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    from diffusers.utils import export_to_video  # type: ignore
    export_to_video(res.frames[0], str(out), fps=fps)
    print(f"🎬 Salvo: {out}")
    return str(out)


def generate_videos_parallel(prompts: list[str], **kw) -> list[str]:
    """
    Gera múltiplos vídeos usando as duas GPUs T4 em paralelo.
    GPU 0 recebe prompts[0, 2, 4…] e GPU 1 recebe prompts[1, 3, 5…]

    Exemplo:
        cenas = ["praia ao pôr do sol", "cidade neon à noite", "floresta com névoa"]
        paths = generate_videos_parallel(cenas, num_frames=97)
    """
    if not prompts:
        return []
    if len(prompts) == 1 or not _has_gpu(1):
        return [generate_video(prompts[0], **kw)]

    futures = [
        _executor.submit(generate_video, p, **{**kw, "device_idx": i % 2})
        for i, p in enumerate(prompts)
    ]
    return [f.result() for f in futures]


# ──────────────────────────────────────────────────────────────────────────────
#  PROMPT BUILDER (helper para conteúdo viral)
# ──────────────────────────────────────────────────────────────────────────────

def build_viral_video_prompt(
    scene:     str,
    camera:    str = "close-up dinâmico com leve dolly in",
    lighting:  str = "iluminação natural contrastada, golden hour",
    motion:    str = "movimento fluido, câmera lenta no clímax",
    aesthetic: str = "cinematográfico, cores saturadas, sem texto ou watermark",
) -> str:
    return (
        f"{scene}. Cinematografia: {camera}. "
        f"Iluminação: {lighting}. Movimento: {motion}. Estética: {aesthetic}."
    )
