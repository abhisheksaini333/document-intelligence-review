import time, statistics, math


def measure(operation, repeats=5):
    if not 1 <= repeats <= 100:
        raise ValueError("Invalid repeat count")
    operation()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        operation()
        samples.append((time.perf_counter() - start) * 1000)
    ordered = sorted(samples)
    return {
        "samples": repeats,
        "median_ms": statistics.median(samples),
        "p95_ms": ordered[math.ceil(0.95 * repeats) - 1],
        "min_ms": ordered[0],
        "max_ms": ordered[-1],
    }
