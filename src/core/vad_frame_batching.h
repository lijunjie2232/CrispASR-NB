#pragma once
// core/vad_frame_batching.h — split a frame axis into compute blocks that
// reproduce the whole-axis result exactly.
//
// FireRedVAD and MarbleNet already push the whole file through one graph, so a
// `batch_size` cap is not about launch overhead (there is only one launch) —
// it bounds peak activation memory on long audio (an hour is ~360k frames).
// That only makes sense if the cap cannot change the answer, so each block
// carries the model's receptive field of context on both sides and the outputs
// that depend on the block edges are dropped.
//
// Both models are stacks of same-padding convolutions, so they are
// translation-equivariant for shifts that are multiples of the total stride.
// `in_begin` is aligned down to such a multiple, which is what makes
// `out_offset = in_begin / stride` exact rather than approximate.
//
// Header-only, no dependencies.

#include <algorithm>
#include <cstdint>
#include <vector>

namespace core_vad_batching {

struct block {
    int in_begin, in_end;     // frame range to feed the model
    int out_offset;           // whole-axis index of this block's output 0
    int keep_begin, keep_end; // which of this block's outputs are valid
};

// n_in / n_out — whole-axis input and output lengths.
// stride        — input frames consumed per output frame (>= 1).
// half_ctx      — receptive-field half-width, in INPUT frames.
// batch         — output frames per block; <= 0 (or >= n_out) = one block over
//                 everything, i.e. no context and no dropping: bit-identical to
//                 the pre-batching path.
inline std::vector<block> plan(int n_in, int n_out, int stride, int half_ctx, int batch) {
    std::vector<block> blocks;
    if (n_in <= 0 || n_out <= 0)
        return blocks;
    stride = std::max(1, stride);
    half_ctx = std::max(0, half_ctx);

    if (batch <= 0 || batch >= n_out) {
        blocks.push_back({0, n_in, 0, 0, n_out});
        return blocks;
    }

    // + stride: in_begin is aligned down by up to stride-1 frames, so the
    // context has to cover that too or the first kept output still sees an edge.
    const int ctx = half_ctx + stride;

    for (int o0 = 0; o0 < n_out; o0 += batch) {
        const int o1 = std::min(n_out, o0 + batch);

        int64_t m0 = (int64_t)o0 * stride - ctx;
        int64_t m1 = (int64_t)o1 * stride + ctx;
        if (m0 < 0)
            m0 = 0;
        m0 -= m0 % stride; // align down
        if (m1 > n_in)
            m1 = n_in;

        block b;
        b.in_begin = (int)m0;
        b.in_end = (int)m1;
        b.out_offset = (int)(m0 / stride);
        b.keep_begin = o0 - b.out_offset;
        b.keep_end = o1 - b.out_offset;
        blocks.push_back(b);
    }
    return blocks;
}

} // namespace core_vad_batching
