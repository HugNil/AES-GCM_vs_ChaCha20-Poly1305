import subprocess
import time
import os
from dotenv import load_dotenv
import pandas as pd
import glob

load_dotenv()

BLOCKS = int(os.getenv("BLOCKS", "10"))
ALGORITHMS = ["AES-GCM", "ChaCha20-Poly1305"]

for block in range(BLOCKS):
    algo = ALGORITHMS[block % 2] 

    print(f"\n=== Starting block {block + 1} with {algo.upper()} ===")

    env = os.environ.copy()
    env["ALGO"] = algo # Set the algorithm for this block
    env["BLOCK_ID"] = str(block + 1)  # For unique CSV filenames

    server_process = subprocess.Popen(
        [os.sys.executable, "-m", "server.server"], # Start the server process
        env=env
    )

    time.sleep(1)

    subprocess.run(
        [os.sys.executable, "-m", "client.client"], # Run the client process which will perform the experiment
        env=env
    )

    server_process.terminate() # Ensure the server process is terminated after the client finishes
    server_process.wait() # Wait for the server process to exit

    print(f"=== Finished block {block + 1} ===")


files = glob.glob("results/*.csv") # Get all CSV files in the results directory

dfs = []

# Merge all individual block CSVs into one DataFrame
for file in files:
    if file.endswith("summary_table.csv") or file.endswith("all_results.csv"):
        continue
    df = pd.read_csv(file)
    df["source_file"] = os.path.basename(file)
    dfs.append(df)

all_results = pd.concat(dfs, ignore_index=True) # Combine all block results into one DataFrame

all_results["latency_us"] = all_results["latency_ns"] / 1000 # Convert latency to microseconds for easier analysis

all_results.to_csv("results/all_results.csv", index=False) # Save the merged results to a single CSV file

print("Merged file saved as results/all_results.csv")

print("\nAll experiment blocks completed.")