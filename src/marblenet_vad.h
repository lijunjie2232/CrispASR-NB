#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

struct marblenet_vad_context;

struct marblenet_vad_segment {
    float start_sec;
    float end_sec;
};

struct marblenet_vad_context* marblenet_vad_init(const char* model_path);

// Extended init.
//   use_gpu    != 0 -> place the weights and run the graph on the GPU backend
//               (CUDA); falls back to the CPU backend when none is registered.
//   batch_size -> output frames per graph compute, 0 = the whole file. Blocks
//               carry the model's receptive field of context and drop the
//               outputs that depend on the block edges, so the slices are the
//               same as one whole-file pass.
struct marblenet_vad_context* marblenet_vad_init_ex(const char* model_path, int use_gpu, int batch_size);

int marblenet_vad_detect(struct marblenet_vad_context* ctx, const float* samples, int n_samples,
                         struct marblenet_vad_segment** segments, int* n_segments, float threshold,
                         float min_speech_sec, float min_silence_sec);

void marblenet_vad_free(struct marblenet_vad_context* ctx);

#ifdef __cplusplus
}
#endif
