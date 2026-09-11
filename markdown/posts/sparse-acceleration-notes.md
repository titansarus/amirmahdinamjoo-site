Sparse linear algebra shows up everywhere, including graph analytics, scientific
computing, and increasingly machine learning. Yet it is stubbornly hard to
accelerate. Here is the short version of why.

## Density is the enemy of locality

Dense matrix multiply is a hardware designer's dream: predictable access
patterns, high reuse, and easy tiling. Sparsity breaks all of that. When most
entries are zero, you spend your time chasing indices and moving small,
irregular chunks of data rather than doing useful arithmetic.

## It's a memory problem

For many sparse kernels the bottleneck is not compute but **memory bandwidth and
irregular access**. Roughly, the useful work scales with the number of nonzeros,

$$\text{FLOPs} \approx 2 \cdot \text{nnz},$$

while the data movement can be far larger once you account for index arrays and
poor reuse. High-bandwidth memory helps, but only if you can actually keep its
channels busy, which is where careful data placement and migration matter.

These notes are informal; the details live in the papers on my
[publications](/publications/) page.
