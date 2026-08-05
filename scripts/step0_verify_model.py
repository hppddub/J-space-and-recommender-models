# === STEP 0 — Verify Qwen3-4B before switching to it ===
# No GPU needed. Leave the runtime on CPU.
#
# Fixes a bug in the previous version: it looked for `layer_types` and
# `hidden_size` at the top level of the config. Qwen3.5 nests them inside
# `text_config`, so the check reported "no layer_types found" on a model that
# has 24 linear-attention layers. This version searches nested sub-configs.

import torch, json
from huggingface_hub import hf_hub_download
from transformers import AutoConfig

# ---- edit these two lines to check a different model -------------------
HF_MODEL  = "Qwen/Qwen3-4B"
LENS_DIR  = "qwen3-4b/jlens/Salesforce-wikitext"
LENS_FILE = "Qwen3-4B_jacobian_lens.pt"
# ------------------------------------------------------------------------
REPO = "neuronpedia/jacobian-lens"


def find_nested(d, key):
    """Search a config dict and one level of sub-configs for `key`."""
    if key in d:
        return d[key], "top level"
    for k, v in d.items():
        if isinstance(v, dict) and key in v:
            return v[key], f"{k}"
    return None, None


cfg = AutoConfig.from_pretrained(HF_MODEL).to_dict()

print("=" * 70)
print(f"ARCHITECTURE CHECK — {HF_MODEL}")
print("=" * 70)

arch = cfg.get("architectures")
print(f"architectures : {arch}")
is_vlm = bool(arch) and any("ConditionalGeneration" in a or "Vision" in a for a in arch)
print(f"  {'FAIL — this is a vision-language model' if is_vlm else 'OK — plain causal LM'}")
print(f"  vision_config present: {'vision_config' in cfg}"
      f"  {'<-- FAIL' if 'vision_config' in cfg else ''}")

lt, where = find_nested(cfg, "layer_types")
print(f"\nlayer_types   : {'absent' if lt is None else f'found in {where}'}")
if lt:
    from collections import Counter
    counts = dict(Counter(lt))
    print(f"  {len(lt)} layers: {counts}")
    if len(counts) == 1:
        print("  OK — uniform stack")
    else:
        print("  FAIL — mixed layer types. Indices by type:")
        for t in counts:
            print(f"    {t:<20} {[i for i, x in enumerate(lt) if x == t]}")
else:
    print("  OK — no mixed-type declaration")

for k in ("mamba_ssm_dtype", "full_attention_interval", "linear_conv_kernel_dim",
          "mtp_num_hidden_layers"):
    v, w = find_nested(cfg, k)
    if v is not None:
        print(f"  NOTE: {k} = {v}  (in {w}) — hybrid/SSM indicator")

n_layers, w1 = find_nested(cfg, "num_hidden_layers")
d_model,  w2 = find_nested(cfg, "hidden_size")
vocab,    _  = find_nested(cfg, "vocab_size")
print(f"\nn_layers = {n_layers}  (from {w1})")
print(f"d_model  = {d_model}   (from {w2})")
print(f"vocab    = {vocab}")

print("\n" + "=" * 70)
print("LENS CHECK")
print("=" * 70)
try:
    yml = open(hf_hub_download(REPO, filename=f"{LENS_DIR}/config.yaml")).read()
    for line in yml.split("\n"):
        if any(t in line for t in ("hf_model_name", "target_layer", "n_prompts",
                                   "dim_batch", "max_seq_len", "prompts_fitted")):
            print("   ", line.strip())
    match = f'"{HF_MODEL}"' in yml
    print(f"\n  hf_model_name matches {HF_MODEL}: {match}  {'' if match else '<-- FAIL'}")
except Exception as e:
    print(f"  config.yaml unavailable: {type(e).__name__}: {e}")

try:
    ck = torch.load(hf_hub_download(REPO, filename=f"{LENS_DIR}/{LENS_FILE}"),
                    map_location="cpu", weights_only=True)
    src = sorted(ck["source_layers"])
    print(f"\n  lens n_prompts     : {ck['n_prompts']}")
    print(f"  lens d_model       : {ck['d_model']}  "
          f"({'MATCH' if ck['d_model'] == d_model else 'MISMATCH <-- FAIL'})")
    print(f"  lens source_layers : {src[0]}..{src[-1]} ({len(src)} layers)")
    if n_layers and src[-1] == n_layers - 2:
        print("  >>> target was the FINAL layer (code default, not the paper's)")
    elif n_layers and src[-1] <= n_layers - 3:
        print("  >>> consistent with a PENULTIMATE target")
except Exception as e:
    print(f"  lens file unavailable: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("VERDICT — all four must pass (DECISION_model_change.md §7)")
print("=" * 70)
print(f"  1. layer_types absent or uniform      : "
      f"{'PASS' if (lt is None or len(set(lt)) == 1) else 'FAIL'}")
print(f"  2. not a vision-language model        : {'FAIL' if is_vlm else 'PASS'}")
print(f"  3. lens hf_model_name matches         : see above")
print(f"  4. lens d_model matches model config  : see above")
