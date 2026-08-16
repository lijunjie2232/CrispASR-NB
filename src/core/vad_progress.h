#pragma once
// core/vad_progress.h — progress reporting for the VADs ("memory counter + async thread").
//
// A VAD over a long file is a multi-second blocking call with no output, so the
// caller cannot tell whether it is grinding or wedged. Printing from the hot
// loop is not an option: one line per window/frame costs more than the window
// itself (the models are small enough that stderr would dominate).
//
// So: the model bumps an atomic counter (a few ns, no lock, no I/O) and a
// background thread samples it and prints one line every
// CRISPASR_VAD_PROGRESS_MS. The counter is unit-agnostic — windows for Silero,
// frames for FireRed/MarbleNet — and the label says which.
//
//   CRISPASR_VAD_PROGRESS=0     silence (any value starting with '0')
//   CRISPASR_VAD_PROGRESS_MS=N  report interval, default 1000
//
// One instance per detect() call. Each model holds its cache mutex for the
// whole detect (see the dispatcher), so two counters never overlap on one
// model; the counter itself is thread-safe regardless.
//
// Header-only, no dependencies beyond the stdlib.

#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <thread>

namespace core_vad_progress {

inline bool enabled() {
    static const bool v = [] {
        const char* e = std::getenv("CRISPASR_VAD_PROGRESS");
        return !(e && e[0] == '0');
    }();
    return v;
}

inline int interval_ms() {
    static const int v = [] {
        const char* e = std::getenv("CRISPASR_VAD_PROGRESS_MS");
        const int ms = e ? std::atoi(e) : 0;
        return ms > 0 ? ms : 1000;
    }();
    return v;
}

class counter {
public:
    counter(const char* label, long long total) : label_(label), total_(total) {
        if (enabled() && total_ > 0)
            worker_ = std::thread(&counter::run, this);
    }

    ~counter() { finish(); }

    counter(const counter&) = delete;
    counter& operator=(const counter&) = delete;

    // Hot path: one relaxed atomic add. Call once per window/frame (or once per
    // batch with n = the batch width).
    void add(long long n = 1) { done_.fetch_add(n, std::memory_order_relaxed); }

    // Idempotent: stops the thread and prints the closing line.
    void finish() {
        if (worker_.joinable()) {
            stop_.store(true, std::memory_order_relaxed);
            worker_.join();
        }
        if (!enabled() || finished_ || total_ <= 0)
            return;
        finished_ = true;
        std::fprintf(stderr, "crispasr[vad]: %s %lld/%lld (100%%)\n", label_,
                     done_.load(std::memory_order_relaxed), total_);
    }

private:
    void run() {
        const int ms = interval_ms();
        const auto t0 = std::chrono::steady_clock::now();
        while (!stop_.load(std::memory_order_relaxed)) {
            // Sleep in slices so the destructor's join() does not have to wait
            // out a whole interval (default 1 s) on a short file.
            for (int waited = 0; waited < ms && !stop_.load(std::memory_order_relaxed); waited += 50)
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
            if (stop_.load(std::memory_order_relaxed))
                break;
            const long long done = done_.load(std::memory_order_relaxed);
            const double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            const double pct = total_ > 0 ? 100.0 * (double)done / (double)total_ : 0.0;
            std::fprintf(stderr, "crispasr[vad]: %s %lld/%lld (%.0f%%) %.1fs\n", label_, done, total_, pct, secs);
        }
    }

    const char* label_;
    long long total_;
    std::atomic<long long> done_{0};
    std::atomic<bool> stop_{false};
    std::thread worker_;
    bool finished_ = false;
};

} // namespace core_vad_progress
