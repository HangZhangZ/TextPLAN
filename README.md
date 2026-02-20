# TextPLAN

Work-in-progress research codebase for text-conditioned floorplan generation with diffusion models.

## Project Summary

This repository currently contains two main codebases:

- `TextPLAN/`: core research implementation for:
  - data preprocessing from vector floorplans
  - SDXL-based training and inference
  - composable attention and boundary-aware inpainting modules
  - evaluation and ablation scripts
  - 2D-to-3D reconstruction utilities
  - baseline model wrappers for comparison
- `tell2design_prompt_augmentor/`: utility scripts that convert structured Tell2Design prompts into natural free-form text using a frozen Qwen model.


## Current Status (Important)

This project is under active cleanup/refactoring.

- Code is not fully cleaned up.
- Some scripts/docs are not perfectly aligned yet.
- No automated test suite is included yet.
- The root README now reflects the current repository layout and entry points.

## Repository Layout

```text
.
├── TextPLAN/
│   ├── train.py
│   ├── inference.py
│   ├── preprocessing.py
│   ├── dataset.py
│   ├── textplan.py
│   ├── control_encoder.py
│   ├── composable_attention.py
│   ├── inpainting.py
│   ├── llm_converter.py
│   ├── evaluation.py
│   ├── ablation_study.py
│   ├── reconstruction_3d.py
│   ├── demo.py
│   └── __init__.py   # baseline models
├── tell2design_prompt_augmentor/
│   ├── tell2design_simple.py
│   ├── tell2design_prompt_augmentor.py
│   └── requirements.txt
├── paper.tex
└── README.md
```

## Environment Setup

There is no single root `requirements.txt` yet. Install dependencies from imports used in `TextPLAN/*.py`:

```bash
conda create -n textplan python=3.10 -y
conda activate textplan

# Pick a torch install matching your CUDA setup
pip install torch torchvision torchaudio

pip install \
  diffusers transformers accelerate peft bitsandbytes \
  opencv-python pillow numpy scipy scikit-image shapely tqdm \
  matplotlib seaborn
```

Optional:

- `wandb` for experiment tracking
- extra tokenizer/runtime packages depending on your environment

For Tell2Design augmentation utilities:

```bash
pip install -r tell2design_prompt_augmentor/requirements.txt
```

## Data Preparation (SwissDwellings-style)

`TextPLAN/preprocessing.py` provides `DataPreparationPipeline` for converting vector JSON layouts into training samples.

Expected processed output structure:

```text
<processed_dir>/
├── index.json
└── <sample_id>/
    ├── floorplan.png
    ├── layout_graph.png
    ├── site_condition.png
    └── metadata.json
```

Example usage (Python):

```python
from TextPLAN.config import default_config
from TextPLAN.preprocessing import DataPreparationPipeline

pipeline = DataPreparationPipeline(default_config)
pipeline.process_dataset(input_dir="./raw_json_layouts", output_dir="./data/processed/train")
```

## Main Entry Points

### Train

```bash
accelerate launch TextPLAN/train.py \
  --data_dir ./data/processed/train \
  --output_dir ./outputs/textplan \
  --resolution 512 \
  --train_batch_size 1 \
  --num_train_epochs 100
```

### Inference

```bash
python3 TextPLAN/inference.py \
  --checkpoint_path ./outputs/textplan \
  --site_boundary ./boundary.png \
  --prompt "floorplan with color tags, contains six rooms, north medium bed, center big living" \
  --num_variations 4 \
  --output_dir ./generated
```

Free-speech mode (optional LLM adapter):

```bash
python3 TextPLAN/inference.py \
  --checkpoint_path ./outputs/textplan \
  --free_speech "I need a six-room apartment with a big living room in the center" \
  --llm_path ./outputs/llm_finetuned \
  --output_dir ./generated
```

### Evaluate

```bash
python3 TextPLAN/evaluation.py \
  --generated_dir ./generated \
  --ground_truth_dir ./data/processed/test
```

### Ablation

```bash
python3 TextPLAN/ablation_study.py \
  --checkpoint_dir ./outputs/textplan \
  --data_dir ./data/processed/test \
  --output_dir ./ablation_results \
  --num_samples 1000
```

### 3D Reconstruction

```bash
python3 TextPLAN/reconstruction_3d.py \
  --input ./generated/floorplan_1.png \
  --output ./reconstruction/floorplan_1.json
```

### LLM Fine-tuning (Free-speech -> Structured Prompt)

```bash
python3 TextPLAN/llm_converter.py \
  --base_model Qwen/Qwen2.5-7B-Instruct \
  --train_data ./data/tell2design_train.json \
  --output_dir ./outputs/llm_finetuned
```

## Tell2Design Prompt Augmentation

Simple script:

```bash
python3 tell2design_prompt_augmentor/tell2design_simple.py \
  --input Tell2Design_artificial_all.pkl \
  --output augmented_prompts.json
```

Full pipeline with checkpointing:

```bash
python3 tell2design_prompt_augmentor/tell2design_prompt_augmentor.py \
  --input Tell2Design_artificial_all.pkl \
  --output ./augmented_output \
  --model Qwen/Qwen3-8B \
  --use-4bit
```

## Known Cleanup Items

- Packaging and import-path consistency across scripts.
- Consolidated dependency management at repo root.
- Better CLI ergonomics for preprocessing and end-to-end workflows.
- Test coverage for key modules (training/inference/evaluation).
- Additional docs/examples synced with current code behavior.

## License

MIT. See `LICENSE`.
