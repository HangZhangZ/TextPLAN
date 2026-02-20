# TextPLAN: Text conditioned Irregular Floorplan Generation by Composable Inpainting Diffusion

[![Paper](https://img.shields.io/badge/Paper-PDF-red)](https://arxiv.org/abs/XXXX.XXXXX)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**TextPLAN** is the first generative model capable of translating unconstrained natural language descriptions of spatial features into feasible floorplans, including those with irregular shapes.

> Zhang, Savov, Dillenburger (2025). "TextPLAN: Text conditioned Irregular Floorplan Generation by Composable Inpainting Diffusion"

## 🌟 Key Features

- **Irregular Shape Generation**: Supports non-orthogonal geometries common in real-world architectural designs
- **Natural Language Input**: Accepts free-form text descriptions of spatial requirements
- **Composable Diffusion Modules**: Precise alignment between structured prompts and layout semantics
- **Inpainting Mechanism**: Enables flexible region-specific generation and arbitrary site conditioning
- **Iterative Customization**: Supports design refinement from rough ideas to precise specifications
- **3D Reconstruction**: Automated pipeline for converting 2D floorplans to 3D models

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Training](#training)
  - [Inference](#inference)
  - [Evaluation](#evaluation)
  - [3D Reconstruction](#3d-reconstruction)
- [Architecture](#architecture)
- [Dataset](#dataset)
- [Results](#results)
- [Citation](#citation)

## 🔧 Installation

### Requirements

- Python 3.8+
- PyTorch 2.0+
- CUDA 11.8+ (for GPU acceleration)

### Setup

```bash
# Clone repository
git clone https://github.com/yourrepo/textplan.git
cd textplan

# Create conda environment
conda create -n textplan python=3.10
conda activate textplan

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Dependencies

```
torch>=2.0.0
diffusers>=0.27.0
transformers>=4.36.0
accelerate>=0.25.0
peft>=0.7.0
bitsandbytes>=0.41.0
opencv-python>=4.8.0
scikit-image>=0.21.0
scipy>=1.11.0
Pillow>=10.0.0
numpy>=1.24.0
tqdm>=4.66.0
wandb>=0.16.0  # optional, for experiment tracking
```

## 🚀 Quick Start

### Generate a floorplan from text

```python
from textplan.inference import TextPLANInference, InferenceInput
from PIL import Image

# Initialize model
inference = TextPLANInference(
    model_path="./checkpoints/textplan",
    llm_path="./checkpoints/llm",  # optional
    device="cuda"
)

# Load site condition
site = Image.open("site_boundary.png")

# Generate
result = inference.generate(
    InferenceInput(
        free_speech="I want a 6 room apartment with a big living room on the south side",
        site_condition=site,
        num_variations=4,
    )
)

# Save results
for i, floorplan in enumerate(result.floorplans):
    floorplan.save(f"output_{i}.png")
```

### Command Line Interface

```bash
# Generate floorplan
python -m textplan generate \
    --prompt "Design a 7 room apartment with 3 bedrooms and a balcony" \
    --site_condition ./boundary.png \
    --model_path ./checkpoints/textplan \
    --output ./result.png \
    --num_variations 4

# 3D Reconstruction
python -m textplan reconstruct \
    --input ./floorplan.png \
    --output ./model.json
```

## 📖 Usage

### Training

#### 1. Prepare Dataset

TextPLAN uses the [SwissDwellings](https://zenodo.org/record/7070952) dataset. Download and preprocess:

```bash
# Download SwissDwellings
wget https://zenodo.org/record/7070952/files/swissdwellings.zip
unzip swissdwellings.zip -d ./data/

# Preprocess data
python scripts/preprocess_data.py \
    --input_dir ./data/swissdwellings \
    --output_dir ./data/processed \
    --resolution 512 \
    --max_boundary_size 20  # meters
```

#### 2. Train Main Model

```bash
# Single GPU
python -m textplan train \
    --data_dir ./data/processed \
    --output_dir ./outputs/textplan \
    --resolution 512 \
    --batch_size 4 \
    --epochs 100 \
    --lr 1e-5

# Multi-GPU with Accelerate
accelerate launch --multi_gpu training/train.py \
    --data_dir ./data/processed \
    --output_dir ./outputs/textplan \
    --train_batch_size 4 \
    --gradient_accumulation_steps 4 \
    --learning_rate 1e-5 \
    --num_train_epochs 100 \
    --mixed_precision fp16
```

#### 3. Fine-tune LLM (Optional)

For free-speech to structured prompt conversion:

```bash
python -m textplan finetune_llm \
    --dataset ./data/tell2design \
    --output ./outputs/llm \
    --base_model Qwen/Qwen2.5-7B-Instruct \
    --epochs 50 \
    --lora_r 64 \
    --lora_alpha 128
```

### Inference

#### Python API

```python
from textplan.inference import TextPLANInference, InferenceInput
from PIL import Image

# Initialize
inference = TextPLANInference(
    model_path="./checkpoints/textplan",
    llm_path="./checkpoints/llm",
    device="cuda",
)

# Basic generation with text
result = inference.generate(
    InferenceInput(
        free_speech="A modern apartment with 5 rooms",
        site_condition=Image.open("site.png"),
    )
)

# Generation with user sketch (inpainting)
result = inference.generate(
    InferenceInput(
        free_speech="Add a kitchen in the southeast",
        site_condition=Image.open("site.png"),
        user_sketch=Image.open("sketch.png"),
    ),
    num_inference_steps=50,
    guidance_scale=7.5,
)

# Iterative refinement
for iteration in range(4):
    result = inference.generate(
        InferenceInput(
            free_speech=user_feedback[iteration],
            site_condition=result.floorplans[user_choice],
        )
    )
```

#### Structured Prompt Format

TextPLAN uses structured prompts internally:

```
floorplan with color tags, contains [num] rooms, [location] [size] [type], ...
```

Example:
```
floorplan with color tags, contains eight rooms, southwest big living, 
north medium bedroom, northwest small balcony, middle tiny bath, ...
```

Vocabularies:
- **Location**: southwest, southeast, south, west, east, center, northwest, northeast, north
- **Size**: tiny, small, medium, big, large
- **Type**: living, bath, closet, bed, kitchen, dining, balcony, corridor

### Evaluation

```bash
# Run evaluation
python -m textplan evaluate \
    --results_dir ./outputs/generated \
    --gt_dir ./data/test \
    --output ./evaluation_results.json

# Run ablation study
python -m textplan ablation \
    --model_dir ./checkpoints \
    --data_dir ./data/test \
    --output_dir ./ablation_results \
    --variants full no_compose no_inpaint no_both
```

Metrics:
- **FID^img**: Fréchet Inception Distance for visual quality
- **KL^vec_T/S/A**: KL divergence for room types, sizes, and adjacencies
- **Nov^vec**: Novelty/diversity of generated layouts
- **Acc^vec**: Accuracy of constraint satisfaction

### 3D Reconstruction

Convert generated floorplans to 3D models for Rhino Grasshopper:

```python
from textplan.reconstruction import Reconstruction3D

reconstructor = Reconstruction3D(
    pixels_per_meter=25.6,  # 512px = 20m
    wall_height=2.8,
)

# Process single image
result = reconstructor.process(
    "floorplan.png",
    "output.json"
)

print(f"Detected {len(result.rooms)} rooms")
print(f"Generated {len(result.walls)} wall segments")
```

The JSON output can be imported directly into Rhino Grasshopper for 3D visualization.

## 🏗️ Architecture

### Overview

TextPLAN extends Stable Diffusion XL (SDXL) with three key innovations:

```
User Free Speech → [LLM QLoRA] → Structured Prompt
                                      ↓
Site Condition → [Control Encoder] → TextPLAN → Generated Floorplan
                                      ↑
              [Composable Diffusion + Inpainting]
```

### Components

1. **QLoRA Fine-tuned LLM** (Section 4.1)
   - Base: Qwen2.5-7B-Instruct
   - 4-bit NF4 quantization with double-Q
   - LoRA adapters (r=64, α=128)
   - Converts free-speech to structured prompts

2. **Control Encoder** (Section 4.3)
   - Processes partial layout graph G^img_partial
   - Multi-scale feature injection via zero convolutions
   - Temporal encoding for diffusion coherence

3. **Composable Diffusion Module** (Section 4.5)
   - Extracts segment embeddings from structured prompts
   - Custom attention masks for spatial alignment
   - Cross-attention between text and visual features

4. **Inpainting Mechanism** (Section 4.4)
   - Boundary-aware noise scheduling (Eq. 17-19)
   - Mask consistency validation (Eq. 20-22)
   - Enables site conditioning and user sketches

### Loss Function (Eq. 27)

```
L_total = L_denoise + λ₁L_inpaint + λ₂L_com + λ₃L_perceptual
```

Where:
- λ₁ = 0.1 (inpainting loss weight)
- λ₂ = 0.05 (composable loss weight)
- λ₃ = 0.01 (perceptual loss weight)

## 📊 Dataset

### SwissDwellings

- **Source**: [Zenodo](https://zenodo.org/record/7070952)
- **Size**: 50k+ apartment layouts
- **Format**: Vectorized floorplans
- **Filtered**: 21k single-family layouts (boundary < 20m, prompt < 77 tokens)

### Data Format

```
data/
├── train/
│   ├── floorplan/     # RGB floorplan images (512×512)
│   ├── layout_graph/  # Layout graph images
│   ├── site/          # Site condition images
│   └── prompts.json   # Structured prompts
├── val/
└── test/
```

### Room Colors (RGB)

| Room Type | Color | RGB |
|-----------|-------|-----|
| Living Room | Red | (255, 0, 0) |
| Bathroom | Cyan | (0, 255, 255) |
| Closet | Yellow | (255, 255, 0) |
| Bedroom | Magenta | (255, 0, 255) |
| Kitchen | Green | (0, 255, 0) |
| Dining Room | Orange | (255, 165, 0) |
| Balcony | Blue | (0, 0, 255) |
| Corridor | Gray | (128, 128, 128) |

## 📈 Results

### Quantitative Comparison

| Model | FID↓ | KL_T↓ | KL_S↓ | KL_A↓ | Nov↑ | Acc↑ |
|-------|------|-------|-------|-------|------|------|
| SD 2.1* | 68.49 | - | - | - | - | - |
| SDXL* | 52.41 | - | - | - | - | - |
| MSD-MHD | 18.76 | 0.074 | 0.341 | 0.269 | 0.774 | 0.26 |
| MSD-UN | 14.55 | - | - | - | - | - |
| **Ours Full** | **5.84** | **0.025** | **0.086** | **0.052** | 0.513 | **0.87** |

*Models marked with * are not fine-tuned for this task.

### Ablation Study

| Variant | FID↓ | KL_T↓ | KL_S↓ | Acc↑ |
|---------|------|-------|-------|------|
| w/o Both | 19.73 | 0.268 | 0.425 | 0.31 |
| w/o Inpaint | 15.07 | 0.213 | 0.378 | 0.58 |
| w/o Composable | 8.15 | 0.104 | 0.124 | 0.79 |
| **Full Model** | **5.84** | **0.025** | **0.086** | **0.87** |

### LLM Fine-tuning

| Model | EMA↑ | SSA↑ |
|-------|------|------|
| Qwen3-8B (original) | 0.463 | 0.841 |
| **QLoRA fine-tuned** | **0.806** | **0.972** |

## 📂 Project Structure

```
textplan/
├── configs/
│   └── config.py           # Configuration dataclasses
├── data/
│   ├── preprocessing.py    # Data preprocessing utilities
│   └── dataset.py          # PyTorch Dataset classes
├── models/
│   ├── textplan.py         # Main TextPLAN model
│   ├── control_encoder.py  # ControlNet encoder
│   ├── composable_attention.py  # Composable diffusion module
│   ├── inpainting.py       # Inpainting mechanism
│   └── llm_converter.py    # QLoRA LLM fine-tuning
├── training/
│   └── train.py            # Training script
├── inference/
│   └── inference.py        # Inference pipeline
├── evaluation/
│   └── evaluation.py       # Evaluation metrics
├── reconstruction/
│   └── reconstruction_3d.py  # 3D reconstruction pipeline
├── scripts/
│   └── ablation_study.py   # Ablation experiments
├── utils/                  # Utility functions
├── __main__.py            # CLI entry point
└── README.md
```

## 🙏 Acknowledgments

- This research is funded by the Swiss National Science Foundation project 7DayHouse.
- Built on [Stable Diffusion XL](https://github.com/Stability-AI/generative-models), [diffusers](https://github.com/huggingface/diffusers), and [transformers](https://github.com/huggingface/transformers).
- Dataset from [SwissDwellings](https://zenodo.org/record/7070952).

## 📄 Citation

```bibtex
@article{zhang2025textplan,
  title={TextPLAN: Text conditioned Irregular Floorplan Generation by Composable Inpainting Diffusion},
  author={Zhang, Hang and Savov, Anton and Dillenburger, Benjamin},
  journal={Automation in Construction},
  year={2025},
  publisher={Elsevier}
}
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
