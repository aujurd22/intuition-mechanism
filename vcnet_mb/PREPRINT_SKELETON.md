# Mushroom-Body Microcircuit Sparsification Provides Adversarial Robustness at Zero Accuracy Cost Inside a Cortical Macro-Architecture

**JUNRONG DU**

Independent researcher. Email: dududu9738@gmail.com

## Abstract

Neuro-inspired architecture design operates at two disconnected scales:
macro-structure work borrows cortical organization (hierarchy, dual
streams, predictive feedback) while microcircuit work borrows local
canonical circuits (winner-take-all, lateral inhibition). No prior work
tests whether the two compose. We take VCNet — a recent cortical
macro-architecture that achieves state-of-the-art accuracy on the
Spots-10 texture benchmark — and insert a Drosophila mushroom-body
microcircuit into its streams: per-position channel winner-take-all
sparsification (top-10% of channels at each spatial location), the
algorithmic analogue of APL-neuron gating of Kenyon-cell responses. In
a three-arm comparison at matched parameter count (224,587) on the full
Spots-10 benchmark (40k train / 10k test), the sparsified macro-network
matches the accuracy of its ReLU counterpart (0.8828 vs 0.8900, within
noise) while delivering **+71% relative robustness under FGSM attack
and 1.6× under PGD-20** (0.2903 vs 0.1697 and 0.0248 vs 0.0152), and
**+187% / 13.1×** over a plain CNN of the same family. The robustness
advantage is stable across three seeds, three data fractions (10/50/100%
— k-WTA additionally leads clean accuracy at the 10% tier), and both
attack strengths, indicating a structural rather than gradient-masking
effect. We identify a critical implementation pitfall — channel-wise
versus position-wise k-WTA semantics — that silently reverses the
result, and release all code. To our knowledge this is the first
controlled evidence that mushroom-body microcircuit principles compose
productively with cortical macro-architectures.

## 1. Introduction

[Context: two disconnected scales of neuro-inspired design; VCNet as
the macro exemplar (cite 2508.02995); k-WTA/MB literature (cite
flypoet-adjacent literature, Krotov & Hopfield WTA layer, Papadimitriou
& Widing MB model); the composition gap.]

## 2. Related Work

### 2.1 Cortical macro-architecture
VCNet; predictive-coding networks; two-stream hypotheses.

### 2.2 Winner-take-all and sparsification
Krotov & Hopfield (WTA dense layer); k-WTA autoencoders; MB
-connectome models; sparse coding (Olshausen).

### 2.3 Adversarial robustness via representation structure
Robust feature space literature; why gradient masking is distrusted
and how we rule it out (PGD-20 + attack-strength consistency).

## 3. Method

### 3.1 The VCNet macro-skeleton (reimplemented)
Hierarchy, dual streams (ventral fine / dorsal coarse), fusion, and a
top-down predictive gate — described in the source paper; not
open-sourced, so we reimplement from the macro description (224,587
parameters).

### 3.2 The MB microcircuit: per-position channel k-WTA
At each spatial location, keep the top-10% channels by activation;
zero the rest. Forward-only mask with a 5% linear bypass in backward
(dead-unit gradient stream). This is the algorithmic analogue of APL
gating Kenyon cells.

### 3.3 The critical implementation pitfall
A channel-wise whole-map variant (keep top-10% CHANNELS across the
whole map, zero entire feature maps) collapses learning to 0.23
accuracy — the sparse semantics must be per-position. We document this
because it silently reverses experimental conclusions.

### 3.4 Three arms, matched parameters
plain (242,250) / VCNet-ReLU / VCNet-kWTA (both 224,587). Same data
(Spots-10 40k/10k), augmentation (none beyond scaling), optimizer
(AdamW, cosine), epochs (15), seeds (0,1,2).

## 4. Results

### 4.1 Accuracy: parity across arms
### 4.2 FGSM robustness: +71% / +187%
### 4.3 PGD-20: ordering preserved (1.6× / 13.1×)
### 4.4 Sample efficiency: advantage stable at 10/50/100% data; clean
accuracy edge at the 10% tier
### 4.5 Gradient-masking control: attack-strength consistency

## 5. Discussion

[Macro+micro composition; connection to MB computation (only the
strongest hypothesis survives); why truncating weak-channel
accumulation paths blunts adversarial perturbations; limitations
(single small dataset, no certified robustness, PGD-only family).]

## 6. Reproducibility

All code, seeds, logs, and results: `vcnet_mb/` at
github.com/aujurd22/intuition-mechanism (commit 514eb89+). Full-run
matrix executed on one RTX 4070 SUPER in under one hour.
