# 📦 Linear Programming vs. Integer Programming
### Evaluating Model Effectiveness in Supply Chain Cost Minimization

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/PuLP-Optimization-FF6B6B?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/CBC-Solver-4FC3F7?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/HTML%20%2F%20CSS%20%2F%20JS-Website%20GUI-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
</p>

<p align="center">
  A comparative study of <strong>Linear Programming (LP)</strong> and <strong>Integer Programming (IP)</strong>
  applied to a real-world supply chain logistics dataset to minimize total transportation cost.
</p>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Research Objectives](#research-objectives)
- [Dataset](#dataset)
- [Methodology](#methodology)
- [Mathematical Formulation](#mathematical-formulation)
- [Results](#results)
- [Project Structure](#project-structure)
- [Setup & Usage](#setup--usage)
- [Website GUI](#website-gui)
- [Technologies Used](#technologies-used)
- [Key Findings](#key-findings)
- [Future Work](#future-work)

---

## 🔍 Overview

This study investigates the performance of **Linear Programming (LP)** and **Integer Programming (IP)** in minimizing total transportation cost across a multi-plant, multi-destination supply chain network.

Using a real logistics dataset — containing order lists, freight rates, warehouse capacities, and plant-to-port mappings — we:
1. Preprocess raw data through a 6-step pipeline
2. Apply an **80/20 train–test split** for model training and evaluation
3. Formulate both LP and IP transportation models
4. Solve both using the **CBC open-source MILP solver** via **PuLP**
5. Compare optimal costs and solution times

> **Central Question:** Does integer-constrained optimization yield meaningfully different costs and performance characteristics compared to its relaxed continuous counterpart in a supply chain context?

---

## 🎯 Research Objectives

- [x] Preprocess and aggregate real supply chain order data by destination demand and plant capacity
- [x] Map plant codes to origin ports and compute average freight rates per route
- [x] Apply a reproducible 80/20 random train–test split (seed = 42)
- [x] Formulate a Transportation Problem as both a Continuous LP and an Integer LP (ILP)
- [x] Solve both models using the CBC solver via the PuLP library
- [x] Compare solution cost, solve time, and optimality between LP and IP models
- [x] Identify practical trade-offs between solution quality and computational efficiency

---

## 📊 Dataset

**File:** `Supply-chain-logistics-problem.xlsx`

| Sheet | Description |
|---|---|
| `OrderList` | Individual shipment orders with destination port and unit quantities |
| `FreightRates` | Freight cost records per origin–destination port pair |
| `WhCapacities` | Daily capacity of each plant/warehouse |
| `PlantPorts` | Mapping of plant codes to their corresponding origin ports |

---

## ⚙️ Methodology

### 6-Step Preprocessing Pipeline

```
Step 1 → Aggregate Demand by Destination Port
           D_j = Σ(unit_qty_k)  for all orders k → destination j

Step 2 → Map Plant Codes to Origin Ports
           OriginPort(i) = Port  where PlantCode = i

Step 3 → Compute Average Freight Rates per Route
           C_ij = (1/N) · Σ rate_k  for orig=OriginPort(i), dest=j

Step 4 → Load Plant / Warehouse Capacities
           S_i = Daily Capacity of plant i

Step 5 → Build Decision Variable Index Sets
           x_ij ≥ 0  (LP)  |  x_ij ∈ ℤ⁺  (IP)
           i ∈ Plants,  j ∈ Destinations

Step 6 → 80/20 Train–Test Split
           Train: 0.80 × N orders  (seed=42)
           Test:  0.20 × N orders  (held out)
```

---

## 🧮 Mathematical Formulation

### Objective Function — Minimize Total Freight Cost

$$\min Z = \sum_{i \in I} \sum_{j \in J} C_{ij} \cdot x_{ij}$$

### Subject To

**Supply Constraints** (each plant cannot exceed its capacity):
$$\sum_{j \in J} x_{ij} \leq S_i \quad \forall i \in I$$

**Demand Constraints** (each destination must receive enough units):
$$\sum_{i \in I} x_{ij} \geq D_j \quad \forall j \in J$$

**Non-negativity / Integrality:**
$$x_{ij} \geq 0 \quad \text{(LP — continuous)}$$
$$x_{ij} \in \mathbb{Z}^+ \quad \text{(IP — integer)}$$

### Variable Definitions

| Symbol | Description |
|---|---|
| `x_ij` | Units shipped from plant `i` to destination `j` |
| `C_ij` | Average freight cost per unit on route `(i → j)` |
| `S_i` | Daily capacity of plant `i` |
| `D_j` | Aggregated demand at destination port `j` |
| `I` | Set of all supply plants |
| `J` | Set of all destination ports |
| `Z` | Total transportation cost (objective value) |

---

## 📈 Results

| Metric | Linear Programming (LP) | Integer Programming (IP) |
|---|---|---|
| **Variable Type** | Continuous (ℝ⁺) | Integer (ℤ⁺) |
| **Solver Method** | Simplex / Interior Point | Branch & Bound (CBC) |
| **Optimal Cost** | Lower bound | ≥ LP cost |
| **Solve Time** | ⚡ Very fast | 🐢 Slower |
| **Fractional Routes?** | Possible | Never |
| **Status** | Optimal | Optimal |

> **Note:** Run `SC_Cost_Minimizer_LP_vs_IP_finalfinal.py` against the Excel dataset to obtain the exact cost and time values for your specific data instance.

---

## 📁 Project Structure

```
LP-vs-IP-SCM/
│
├── 📄 README.md                              ← This file
├── 🐍 SC_Cost_Minimizer_LP_vs_IP_finalfinal.py  ← Main optimization script
├── 🌐 index.html                             ← Interactive website GUI
├── 🖼️  hero_bg.png                            ← Website background image
└── 📊 Supply-chain-logistics-problem.xlsx    ← Real logistics dataset
```

---

## 🚀 Setup & Usage

### Prerequisites

```bash
pip install pulp pandas openpyxl
```

### Running the Optimization Script

1. Make sure `Supply-chain-logistics-problem.xlsx` is in the **same folder** as the script.
2. Run:

```bash
python SC_Cost_Minimizer_LP_vs_IP_finalfinal.py
```

3. The script will:
   - Load and preprocess the Excel dataset
   - Display step-by-step preprocessing with formulas and results
   - Apply the 80/20 train–test split
   - Solve both LP and IP models
   - Print a side-by-side cost and time comparison

### Expected Output (abbreviated)

```
Reading Excel sheets... this may take a moment.
============================================================
  STEP-BY-STEP PREPROCESSING
============================================================

  STEP 1: Aggregate Demand by Destination Port
  ...
  STEP 6: Split OrderList into Train & Test Sets
  ...

--- COMPARISON RESULTS ---
Linear Programming Cost:  $XX,XXX,XXX.XX | Time: X.XXXXs
Integer Programming Cost: $XX,XXX,XXX.XX | Time: X.XXXXs
```

---

## 🌐 Website GUI

An interactive research website (`index.html`) is included. Open it directly in any browser — **no server required**.

**Sections:**
- 🏠 **Hero** — Animated overview with live stat counters
- 📋 **Abstract** — Research background and objectives
- ⚙️ **Pipeline** — All 6 preprocessing steps with formulas
- 📊 **LP vs IP Comparison** — Side-by-side model properties
- 🧮 **Formulation** — Full mathematical model with code
- 📉 **Data Split** — Animated 80/20 bar visualization
- 📈 **Results** — Metric cards and animated bar chart
- 🎛️ **Simulator** — Interactive sliders to simulate LP vs IP behavior
- 🔭 **Conclusion** — Key findings, verdict, and future work

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.x** | Core programming language |
| **PuLP** | LP/IP model formulation |
| **CBC (via PuLP)** | Open-source MILP solver (Branch & Bound) |
| **pandas** | Data loading, preprocessing, aggregation |
| **openpyxl** | Excel `.xlsx` file reading |
| **HTML / CSS / JS** | Interactive research website |
| **Google Fonts** | Typography (Outfit, Inter, JetBrains Mono) |

---

## 🏆 Key Findings

1. **LP provides a tight lower bound** — The LP relaxation gives the minimum achievable cost assuming fractional shipments are allowed.

2. **IP costs are near-equal to LP** — For transportation problems with integer supply/demand, the LP constraint matrix is *totally unimodular*, meaning the LP optimal solution is often already integral.

3. **Solve time difference is significant** — LP solves in milliseconds via the simplex method; IP requires Branch & Bound and can be orders of magnitude slower at large scale.

4. **IP is operationally necessary** — When real shipments must be whole units, IP is the only practically feasible model, even if cost differences are negligible.

5. **80/20 split ensures generalizability** — Training the model on 80% of orders and holding 20% out tests whether the optimal routes generalize to unseen demand patterns.

---

## 🔭 Future Work

- [ ] Multi-objective optimization (cost + delivery time + CO₂ emissions)
- [ ] Stochastic demand with robust LP/IP formulations
- [ ] Metaheuristics (Genetic Algorithm, Simulated Annealing) for large-scale IP
- [ ] Dynamic routing with time-window constraints
- [ ] Network flow vs. transportation simplex method comparison
- [ ] Real-time dashboard integration with live logistics data

---

<p align="center">
  Made with ❤️ &nbsp;|&nbsp; Operations Research &nbsp;|&nbsp; Supply Chain Optimization
</p>
