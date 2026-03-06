# AES-GCM vs ChaCha20-Poly1305 – Latency Comparison

This project evaluates the performance impact of two authenticated encryption algorithms:

- **AES-GCM**
- **ChaCha20-Poly1305**

The study measures **end-to-end latency** in a controlled near real-time TCP communication setup.

---

## Purpose

The objective of this experiment is to compare how AES-GCM and ChaCha20-Poly1305 affect latency in a latency-sensitive environment.

The evaluation focuses on:

- Small messages (~128 bytes)
- Medium messages (~512 bytes)
- Large messages (~2048 bytes)

Latency is measured from:

> Encryption + Transmission + Decryption + ACK verification

---

## Experimental Setup

- Language: Python  
- Transport: TCP (localhost)  
- Measurement unit: microseconds (µs)  
- Statistical method: Welch’s two-sample t-test  
- Warm-up phase before measurements  
- Multiple independent experimental blocks  

Each configuration is repeated multiple times to reduce random variation.

---

## Project Structure

- client/ # Client implementation
- server/ # Server implementation
- crypto/ # AES-GCM and ChaCha20-Poly1305 implementations
- scripts/ # Experiment runner
- results/ # All results, including raw and processed data
- analysis.ipynb # Statistical analysis notebook


---

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows

Install dependencies:
pip install -r requirements.txt

Running the Experiment

Run alternating blocks:
python -m scripts.run_experiment

This will:
- Start the server
- Run the client
- Collect latency data
- Save results in the results/ directory
- Statistical Analysis

Open the Jupyter notebook:
- jupyter notebook analysis.ipynb

The analysis includes:
- Mean latency
- Standard deviation
- 95% confidence intervals
- Welch’s t-test per message size
- Visualization of results

Reproducibility

All raw experimental data and analysis scripts are included to ensure full reproducibility.

- To replicate results:
- Install dependencies
- Run the experiment
- Execute the analysis notebook

Notes
- Results may vary slightly between runs due to OS scheduling and CPU frequency scaling.
- Multiple experimental blocks are used to ensure statistical robustness.
- AES performance may benefit from hardware acceleration (AES-NI).

License
This project is part of an academic thesis project.