# Tell2Design Prompt Augmentor

Convert structured Tell2Design dataset prompts into natural, free-form speech using a frozen Qwen3-8B model.

## Features

- **Frozen Qwen3-8B Model**: Uses the model in inference mode without training
- **Automatic Unit Conversion**: Converts square feet to square meters
- **Aspect Ratio Removal**: Automatically removes all aspect ratio information
- **Single Sentence Output**: Produces natural, conversational single sentences
- **Checkpointing**: Saves progress periodically for long datasets
- **4-bit Quantization**: Memory-efficient inference using bitsandbytes

## Installation

```bash
pip install -r requirements.txt
```

For CUDA support with 4-bit quantization:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install bitsandbytes accelerate
```

## Quick Start

### Demo Mode
```bash
python tell2design_simple.py --demo
```

### Process Tell2Design Dataset
```bash
# Download Tell2Design dataset first from:
# https://github.com/LengSicong/Tell2Design

# Then run:
python tell2design_simple.py \
    --input Tell2Design_artificial_all.pkl \
    --output augmented_prompts.json
```

### Full Pipeline (Advanced)
```bash
python tell2design_prompt_augmentor.py \
    --input Tell2Design_artificial_all.pkl \
    --output ./augmented_output \
    --model Qwen/Qwen3-8B \
    --use-4bit \
    --checkpoint-every 100
```

## Input/Output Examples

### Input (Structured)
```
It would be good to have a common room. I would like to place common room 
at the north side of the apartment. The common room should be around 200 sqft 
with the aspect ratio of 3 over 4. The common room should have an en-suite 
bathroom. The common room should be next to the bathroom, kitchen, balcony.
```

### Preprocessed (sqft → sqm, aspect ratio removed)
```
It would be good to have a common room. I would like to place common room 
at the north side of the apartment. The common room should be around 18.6 
square meters. The common room should have an en-suite bathroom. The common 
room should be next to the bathroom, kitchen, balcony.
```

### Output (Natural Speech)
```
I'd like a common room of about 18.6 square meters on the north side of 
the apartment, with an attached bathroom and easy access to the kitchen 
and balcony.
```

## System Prompt Used

```
You are an expert at converting structured architectural descriptions into 
natural, conversational speech. Transform the given text into a free-form 
prompt that sounds like natural human speech.

Rules:
1. Remove ALL aspect ratio information
2. Square meter conversions are already done - just use them
3. Output ONLY a single, flowing sentence that sounds natural
4. Maintain spatial relationships and room information
5. Use casual, natural language
6. Respond with ONLY the converted sentence
```

## Output Files

The full pipeline (`tell2design_prompt_augmentor.py`) generates:

| File | Description |
|------|-------------|
| `augmented_tell2design.json` | Full results with all metadata |
| `augmented_tell2design.pkl` | Pickle format for Python loading |
| `augmented_tell2design.jsonl` | One sample per line |
| `augmented_text_pairs.json` | Original/augmented pairs only |
| `augmented_statistics.json` | Processing statistics |
| `checkpoint.json` | Resume checkpoint (deleted on completion) |

## CLI Arguments

### Simple Script (`tell2design_simple.py`)
| Argument | Default | Description |
|----------|---------|-------------|
| `--input, -i` | - | Input pickle file |
| `--output, -o` | `augmented.json` | Output JSON file |
| `--model, -m` | `Qwen/Qwen3-8B` | Model name |
| `--no-4bit` | False | Disable 4-bit quantization |
| `--demo` | False | Run demo mode |
| `--checkpoint-every` | 50 | Checkpoint frequency |

### Full Pipeline (`tell2design_prompt_augmentor.py`)
| Argument | Default | Description |
|----------|---------|-------------|
| `--input, -i` | `Tell2Design_artificial_all.pkl` | Input file |
| `--output, -o` | `./augmented_output` | Output directory |
| `--model, -m` | `Qwen/Qwen3-8B` | Model name |
| `--batch-size, -b` | 1 | Batch size |
| `--temperature, -t` | 0.7 | Generation temperature |
| `--use-4bit` | (default behavior) | Use 4-bit quantization (enabled by default) |
| `--use-8bit` | False | Use 8-bit quantization |
| `--no-quantize` | False | Disable all quantization |
| `--checkpoint-every` | 100 | Checkpoint frequency |
| `--no-resume` | False | Don't resume from checkpoint |
| `--demo` | False | Run demo mode |
| `--seed` | 42 | Random seed |

## Memory Requirements

| Configuration | VRAM Required |
|--------------|---------------|
| 4-bit quantization | ~6 GB |
| 8-bit quantization | ~10 GB |
| Full precision (fp16) | ~18 GB |
| CPU only | ~32 GB RAM |

## Programmatic Usage

```python
from tell2design_simple import Qwen3Augmentor, preprocess_prompt

# Initialize model
augmentor = Qwen3Augmentor(
    model_name="Qwen/Qwen3-8B",
    use_4bit=True
)

# Process single prompt
original = "The kitchen is around 150 sqft with aspect ratio of 4:3."
preprocessed = preprocess_prompt(original)  # Convert units, remove aspect ratio
augmented = augmentor.augment(preprocessed)

print(f"Natural speech: {augmented}")
```

## Dataset Information

The Tell2Design dataset contains 80k+ floor plan designs with natural language instructions:
- **Artificial instructions**: Structured, complete information
- **Human instructions**: Natural but potentially ambiguous

Dataset source: https://github.com/LengSicong/Tell2Design

Citation:
```bibtex
@inproceedings{leng2023tell2design,
  title={Tell2Design: A Dataset for Language-Guided Floor Plan Generation},
  author={Leng, Sicong and Zhou, Yang and Dupty, Mohammed Haroon and Lee, Wee Sun and Joyce, Sam and Lu, Wei},
  booktitle={Proceedings of ACL},
  year={2023}
}
```

## License

MIT License - see LICENSE file for details.
