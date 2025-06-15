def evaluate_memory_usage(cms):
    return cms.counters.nbytes


def print_memory_usage(total_size):
    print(f"Total CMS memory usage: {total_size} bytes")
