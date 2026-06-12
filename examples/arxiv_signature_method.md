# A Primer on the Signature Method in Machine Learning
<!-- author: Chevyrev & Kormilitzin (2016, rev. 2025) -->
<!-- theme: academic -->

### Presentation outline
<!-- agenda -->
1. The sequential data problem
2. What is the signature method
3. Mathematical properties
4. Practical ML pipeline
5. Results and advantages

## 1. The Problem

### Sequential data is ubiquitous but standard ML cannot handle it efficiently
**Situation:** Time-ordered data appears across every domain — finance, healthcare, handwriting, text, networks — and each domain needs effective feature extraction from variable-length sequences
**Complication:** Existing approaches either lose information through aggressive dimensionality reduction, require prohibitive memory, or rely on parametric assumptions that do not hold for complex sequential data
**Resolution:** The signature method transforms any path into a compact, fixed-dimensional, non-parametric feature vector via iterated integrals — theoretically grounded in rough path theory and competitive with deep learning at a fraction of the computation
> Source: Chevyrev & Kormilitzin 2016/2025; arXiv:1603.03788

### Dimensional efficiency: signature features scale far better than raw sequences
**2D path, level 3 truncation:** 15 features
**vs raw sequence features:** thousands
**Dimensionality formula:** (d^(k+1) - 1) / (d - 1)
> Source: arXiv:1603.03788, Section 2

## 2. The Signature Method

### The signature captures a path's geometry through all iterated integrals
> "The signature is a sequence of numbers associated with a path that captures many of its important analytic and geometric properties."
> — Chevyrev & Kormilitzin, arXiv:1603.03788

### Iterated integrals encode path geometry at increasing levels of complexity
![Figure: Signature levels for a 2D path](Level 1 captures coordinate increments (2 terms); Level 2 captures pairwise interaction integrals (4 terms); Level 3 nests further (8 terms); total 14 features — fixed regardless of sequence length)
> Source: arXiv:1603.03788, Section 2.1

## 3. Mathematical Properties

### Four algebraic properties make the signature theoretically principled
| Property | What it means | Why it matters |
|---|---|---|
| Time-reparametrisation invariance | Unchanged under speed rescaling | Works when measurement intervals vary |
| Chen's identity | S(X)^{a,b} tensor S(X)^{b,c} = S(X)^{a,c} | Enables modular path analysis |
| Shuffle product | Algebraic constraint on signature components | Guarantees uniqueness and efficiency |
| Universality | Highly descriptive across domains | One method, any sequential data type |
> Source: arXiv:1603.03788, Sections 3–4

### Log-signature reduces dimensionality while preserving essential information
- Log-signature computed from signature components via Campbell-Baker-Hausdorff formula
- Strictly lower-dimensional than full signature at same truncation level
- Preferred in practice for high-dimensional or long sequences
- Captures same geometric information as signature under mild conditions
> Source: arXiv:1603.03788, Section 4.3

## 4. Practical ML Pipeline

### Three-step pipeline converts any sequential data into ML-ready features
1. **Path embedding:** Convert discrete observations into continuous path via interpolation (e.g. linear, rectilinear, lead-lag)
2. **Signature computation:** Calculate iterated integrals up to truncation level N (typically 2–4 for practical use)
3. **Classification:** Feed fixed-dimensional signature features into any standard classifier — SVM, logistic regression, random forest
> Source: arXiv:1603.03788, Section 5

### Signature method compared to deep learning approaches
#### Signature Method
- Non-parametric — no distributional assumptions
- Fixed feature dim regardless of sequence length
- Theoretically grounded via rough path theory
- Fast at inference; no training required
#### Deep Learning (RNN/LSTM)
- Parametric — requires architecture choices
- Memory scales with sequence length
- Empirically motivated, less interpretable
- Slower inference; expensive training
> Source: arXiv:1603.03788, Section 6

## 5. Results

### Signature features achieve competitive accuracy on handwritten digit classification
![Figure: Handwritten digit classification pipeline](MNIST digit trajectories embedded as 2D paths; signature features at level 3 (15 features) fed to SVM classifier; competitive accuracy vs deep learning baselines with substantially lower compute)
> Source: arXiv:1603.03788, Section 6 (case study)

### Signature method is theoretically sound but has practical limits
#### Advantages
- Universality: works across finance, healthcare, NLP, vision
- Interpretability: each component has geometric meaning
- Efficiency: fixed dimensionality, no training loop
- Rigour: full theoretical backing from rough path theory
#### Limitations
- Truncation: infinite series must be cut; level selection needs tuning
- Computational cost: exponential in level for high-dimensional paths
- Embedding quality: results depend on interpolation choice
- Sparse benchmarks: limited direct comparison vs deep learning in this primer

### Thank You — arXiv:1603.03788
<!-- closing -->
https://arxiv.org/abs/1603.03788
