import pandas as pd
import pulp
import time
import os
import sys

# Force UTF-8 output on Windows to avoid encoding errors
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 1. LOAD DATASET DIRECTLY FROM EXCEL
file_path = "Supply-chain-logistics-problem.xlsx"

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found in the folder.")
    print("Detected files:", os.listdir())
    exit()

try:
    print("Reading Excel sheets... this may take a moment.")
    # Load each sheet as a dataframe
    order_list = pd.read_excel(file_path, sheet_name="OrderList")
    freight_rates = pd.read_excel(file_path, sheet_name="FreightRates")
    wh_capacities = pd.read_excel(file_path, sheet_name="WhCapacities")
    plant_ports = pd.read_excel(file_path, sheet_name="PlantPorts")
    print("Sheets loaded successfully.")
except Exception as e:
    print(f"Error reading Excel: {e}")
    exit()

# ============================================================
# 2. PREPROCESSING - Step-by-Step with Formulas & Results
# ============================================================

print("\n" + "=" * 60)
print("  STEP-BY-STEP PREPROCESSING")
print("=" * 60)

# -- STEP 1: Aggregate Demand by Destination -----------------
print("\n+---------------------------------------------------------+")
print("|  STEP 1: Aggregate Demand by Destination Port          |")
print("+---------------------------------------------------------+")
print("\n  Formula:")
print("    D_j = SUM(Unit quantity_k)  for all orders k -> destination j")
print("         where j in {Destination Ports}")
print()

# Show raw data sample
print("  Raw OrderList sample (first 5 rows):")
print(order_list[['Order ID', 'Destination Port', 'Unit quantity']].head().to_string(index=False))
print()

# Perform aggregation
demand_series = order_list.groupby('Destination Port')['Unit quantity'].sum()
demand = demand_series.to_dict()

print(f"  Result: {len(demand)} unique destinations identified.")
print(f"  Total demand across all destinations: {sum(demand.values()):,.0f} units")
print()
print("  Aggregated Demand (D_j):")
demand_df = pd.DataFrame({'Destination Port': demand.keys(), 'Total Demand (units)': demand.values()})
demand_df = demand_df.sort_values('Total Demand (units)', ascending=False).reset_index(drop=True)
print(demand_df.to_string(index=False))
print()
print("  [OK] Step 1 Complete - Demand dictionary built.")

# -- STEP 2: Map Plants to Origin Ports ----------------------
print("\n+---------------------------------------------------------+")
print("|  STEP 2: Map Plant Codes to Origin Ports               |")
print("+---------------------------------------------------------+")
print("\n  Formula:")
print("    OriginPort(i) = Port  where PlantCode = i")
print("    This creates a lookup:  Plant -> Port  for freight rate matching.")
print()

# Show raw mapping data
print("  PlantPorts table:")
print(plant_ports[['Plant Code', 'Port']].to_string(index=False))
print()

# Perform mapping
plant_to_port = dict(zip(plant_ports['Plant Code'], plant_ports['Port']))

print(f"  Result: {len(plant_to_port)} plant-to-port mappings created.")
print()
print("  Mapping (Plant -> Origin Port):")
for plant, port in plant_to_port.items():
    print(f"    {plant}  -->  {port}")
print()
print("  [OK] Step 2 Complete - Plant-to-port lookup built.")

# -- STEP 3: Compute Average Freight Rates per Route ---------
print("\n+---------------------------------------------------------+")
print("|  STEP 3: Average Freight Rates per Route               |")
print("+---------------------------------------------------------+")
print("\n  Formula:")
print("    C_ij = (1/N) * SUM(rate_k)  for all records k with")
print("           orig_port_cd = OriginPort(i) and dest_port_cd = j")
print("    where N = number of rate records for that route")
print()

# Show raw freight rates sample
print("  Raw FreightRates sample (first 5 rows):")
print(freight_rates[['orig_port_cd', 'dest_port_cd', 'rate']].head().to_string(index=False))
print()

# Perform averaging
avg_rates_series = freight_rates.groupby(['orig_port_cd', 'dest_port_cd'])['rate'].mean()
avg_rates = avg_rates_series.to_dict()

print(f"  Result: {len(avg_rates)} unique routes with averaged costs.")
print()
print("  Average Cost per Route (C_ij) - sample of first 10:")
rate_df = pd.DataFrame([
    {'Origin Port': k[0], 'Destination Port': k[1], 'Avg Rate ($)': f"{v:,.2f}"}
    for k, v in list(avg_rates.items())[:10]
])
print(rate_df.to_string(index=False))
if len(avg_rates) > 10:
    print(f"    ... and {len(avg_rates) - 10} more routes")
print()
print("  [OK] Step 3 Complete - Average freight rate matrix built.")

# -- STEP 4: Load Plant / Warehouse Capacities ---------------
print("\n+---------------------------------------------------------+")
print("|  STEP 4: Load Plant / Warehouse Capacities             |")
print("+---------------------------------------------------------+")
print("\n  Formula:")
print("    S_i = Daily Capacity of plant i")
print("    Supply constraint:  SUM_j(x_ij) <= S_i   for each plant i")
print()

# Perform loading
capacities = dict(zip(wh_capacities['Plant ID'], wh_capacities['Daily Capacity ']))

print("  Plant Capacities (S_i):")
cap_df = pd.DataFrame({'Plant ID': capacities.keys(), 'Daily Capacity (units)': capacities.values()})
cap_df = cap_df.sort_values('Daily Capacity (units)', ascending=False).reset_index(drop=True)
print(cap_df.to_string(index=False))
print()
print(f"  Total supply capacity: {sum(capacities.values()):,.0f} units")
print(f"  Total demand:          {sum(demand.values()):,.0f} units")
diff = sum(capacities.values()) - sum(demand.values())
if diff >= 0:
    print(f"  Surplus:               {diff:,.0f} units  [OK] (feasible)")
else:
    print(f"  Deficit:              {abs(diff):,.0f} units  [!!] (may be infeasible!)")
print()
print("  [OK] Step 4 Complete - Capacity constraints ready.")

# -- STEP 5: Build Decision Variable Index Sets --------------
print("\n+---------------------------------------------------------+")
print("|  STEP 5: Build Decision Variable Index Sets            |")
print("+---------------------------------------------------------+")
print("\n  Formula:")
print("    Decision variables:  x_ij >= 0")
print("    where i in Plants = {set of plant IDs}")
print("          j in Destinations = {set of destination ports}")
print()

plants = list(capacities.keys())
destinations = list(demand.keys())

print(f"  Plants (i):       {len(plants)} plants  ->  {plants}")
print(f"  Destinations (j): {len(destinations)} ports  ->  {destinations}")
print(f"  Total routes:     {len(plants)} x {len(destinations)} = {len(plants) * len(destinations)} decision variables")
print()
print("  [OK] Step 5 Complete - Index sets ready.")

# -- Preprocessing Summary -----------------------------------
print("\n" + "=" * 60)
print("  PREPROCESSING COMPLETE - Summary")
print("=" * 60)
print(f"  * Demand points (j):       {len(destinations)}")
print(f"  * Supply plants (i):       {len(plants)}")
print(f"  * Known freight routes:    {len(avg_rates)}")
print(f"  * Decision variables:      {len(plants) * len(destinations)}")
print(f"  * Total demand:            {sum(demand.values()):,.0f} units")
print(f"  * Total capacity:          {sum(capacities.values()):,.0f} units")
print("=" * 60)
print("\n  Proceeding to optimization...\n")

# ============================================================
# 3. DATA SPLITTING - 80% Training / 20% Testing
# ============================================================

import random

print("\n" + "=" * 60)
print("  DATA SPLITTING  (80% Training / 20% Testing)")
print("=" * 60)

print("\n+---------------------------------------------------------+")
print("|  STEP 6: Split OrderList into Train & Test Sets        |")
print("+---------------------------------------------------------+")
print("\n  Formula:")
print("    Total orders N -> Train: 0.80 * N  |  Test: 0.20 * N")
print("    Rows are shuffled with a fixed seed then sliced 80/20.")
print()

total_orders = len(order_list)
print(f"  Total orders in dataset:  {total_orders}")

# Shuffle indices with fixed seed for reproducibility, then split 80/20
random.seed(42)
shuffled_idx = order_list.index.tolist()
random.shuffle(shuffled_idx)

split_point = int(0.80 * total_orders)
train_idx   = shuffled_idx[:split_point]
test_idx    = shuffled_idx[split_point:]

train_orders = order_list.loc[train_idx]
test_orders  = order_list.loc[test_idx]
print("  [Random shuffle split used (seed=42)]")

train_size = len(train_orders)
test_size  = len(test_orders)

print()
print(f"  {'Set':<12} {'Orders':>8} {'% of Total':>12}")
print(f"  {'-'*34}")
print(f"  {'Training':<12} {train_size:>8,} {train_size/total_orders*100:>11.1f}%")
print(f"  {'Testing':<12} {test_size:>8,} {test_size/total_orders*100:>11.1f}%")
print(f"  {'TOTAL':<12} {total_orders:>8,} {'100.0%':>12}")
print()

# Rebuild demand from TRAINING set only
demand_train_series = train_orders.groupby('Destination Port')['Unit quantity'].sum()
demand_train = demand_train_series.to_dict()

# Keep test demand for evaluation reference
demand_test_series = test_orders.groupby('Destination Port')['Unit quantity'].sum()
demand_test = demand_test_series.to_dict()

print("  Demand comparison - Full vs Train vs Test (by destination):")
print()
print(f"  {'Destination Port':<30} {'Full Demand':>12} {'Train Demand':>13} {'Test Demand':>12}")
print(f"  {'-'*70}")
for dest in sorted(demand.keys()):
    full_d  = demand.get(dest, 0)
    train_d = demand_train.get(dest, 0)
    test_d  = demand_test.get(dest, 0)
    print(f"  {dest:<30} {full_d:>12,.0f} {train_d:>13,.0f} {test_d:>12,.0f}")
print()

print(f"  Total Train Demand : {sum(demand_train.values()):>12,.0f} units")
print(f"  Total Test Demand  : {sum(demand_test.values()):>12,.0f} units")
print(f"  Total Full Demand  : {sum(demand.values()):>12,.0f} units")
print()
print("  [OK] Step 6 Complete - Data split ready.")
print()

# Replace demand with training demand for optimization
demand = demand_train
destinations = list(demand.keys())

print("=" * 60)
print("  DATA SPLIT COMPLETE - Summary")
print("=" * 60)
print(f"  * Training orders:         {train_size:,}  ({train_size/total_orders*100:.1f}%)")
print(f"  * Testing  orders:         {test_size:,}  ({test_size/total_orders*100:.1f}%)")
print(f"  * Train demand (used):     {sum(demand_train.values()):,.0f} units")
print(f"  * Test  demand (held out): {sum(demand_test.values()):,.0f} units")
print(f"  * Optimization will use TRAINING data only.")
print("=" * 60)
print("\n  Proceeding to optimization...\n")

def run_model(is_integer=False):
    model_type = 'Integer' if is_integer else 'Linear'
    cat = 'Integer' if is_integer else 'Continuous'
    
    prob = pulp.LpProblem(f"Minimize_Cost_{model_type}", pulp.LpMinimize)
    routes = [(i, j) for i in plants for j in destinations]
    x = pulp.LpVariable.dicts("Ship", routes, lowBound=0, cat=cat)
    
    # Objective
    objective_terms = []
    for i, j in routes:
        orig_port = plant_to_port.get(i)
        rate = avg_rates.get((orig_port, j))
        if rate is not None:
            objective_terms.append(x[i, j] * rate)
    prob += pulp.lpSum(objective_terms)
    
    # Constraints
    for i in plants:
        prob += pulp.lpSum([x[i, j] for j in destinations]) <= capacities[i]
    for j in destinations:
        prob += pulp.lpSum([x[i, j] for i in plants]) >= demand[j]
        
    start_time = time.time()
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return pulp.value(prob.objective), time.time() - start_time

# 3. EXECUTE COMPARISON
lp_cost, lp_time = run_model(is_integer=False)
ip_cost, ip_time = run_model(is_integer=True)

print(f"\n--- COMPARISON RESULTS ---")
print(f"Linear Programming Cost: ${lp_cost:,.2f} | Time: {lp_time:.4f}s")
print(f"Integer Programming Cost: ${ip_cost:,.2f} | Time: {ip_time:.4f}s")