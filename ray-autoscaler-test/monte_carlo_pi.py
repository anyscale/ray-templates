# Based off of @edoakes example https://medium.com/distributed-computing-with-ray/how-to-scale-python-multiprocessing-to-a-cluster-with-one-line-of-code-d19f242f60ff

import argparse
import time
import random
import math

parser = argparse.ArgumentParser(description="Approximate digits of Pi using Monte Carlo simulation.")
parser.add_argument("--num-samples", type=int, default=20000000)
parser.add_argument("--max-time", type=int, default=15)

SAMPLE_BATCH_SIZE = 100000

def sample(num_samples):
    num_inside = 0
    for _ in range(num_samples):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if math.hypot(x, y) <= 1:
            num_inside += 1

    return num_inside

def approximate_pi_distributed(num_samples, max_time):
    from ray.util.multiprocessing import Pool
    pool = Pool()

    start = time.time()
    num_inside = 0
    for result in pool.map(sample, [SAMPLE_BATCH_SIZE for _ in range(num_samples//SAMPLE_BATCH_SIZE)]):
        num_inside += result

    elapsed_time = time.time() - start

    assert elapsed_time < max_time

if __name__ == "__main__":
    args = parser.parse_args()
    approximate_pi_distributed(args.num_samples, args.max_time)
