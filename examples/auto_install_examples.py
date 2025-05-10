from devopy.utils.auto_install import ensure_packages

# Example 1: Explicit package list
def test_math():
    import math
    return math.sqrt(16)

def test_numpy():
    import numpy as np
    return np.array([1,2,3]).sum()

@ensure_packages(["numpy"])
def example_with_numpy():
    import numpy as np
    return np.mean([1, 2, 3])

# Example 2: Automatic detection (should install requests if missing)
@ensure_packages()
def example_with_requests():
    import requests
    r = requests.get("https://httpbin.org/get")
    return r.status_code

# Example 3: Multiple imports, automatic detection
@ensure_packages()
def example_with_pandas_and_numpy():
    import pandas as pd
    import numpy as np
    df = pd.DataFrame({"a": [1,2], "b": [3,4]})
    return df.describe(), np.median([1,2,3])

if __name__ == "__main__":
    print("test_math:", test_math())
    print("test_numpy:", test_numpy())
    print("example_with_numpy:", example_with_numpy())
    print("example_with_requests:", example_with_requests())
    print("example_with_pandas_and_numpy:", example_with_pandas_and_numpy())
