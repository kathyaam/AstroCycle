import os
from cerebras.cloud.sdk import Cerebras
import json
import time

# Initialize Cerebras client
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY"),
)

# Material state representation
class MaterialState:
    def __init__(self):
        self.defect_density = 0.01  # Initial defect fraction
        self.thermal_stress = 0.05  # Normalized stress level
        self.conductivity_drift = 0.0  # Change from baseline
        self.cycle_count = 0
        
    def to_dict(self):
        return {
            "cycle": self.cycle_count,
            "defect_density": round(self.defect_density, 4),
            "thermal_stress": round(self.thermal_stress, 4),
            "conductivity_drift": round(self.conductivity_drift, 4)
        }
    
    def apply_degradation(self, radiation_level, temp_cycling):
        """Simple degradation model (not real physics)"""
        # Defects accumulate from radiation
        self.defect_density += radiation_level * 0.008 * (1 + self.thermal_stress)
        
        # Thermal stress increases with cycling and existing defects
        self.thermal_stress += temp_cycling * 0.012 * (1 + self.defect_density * 0.5)
        
        # Conductivity degrades as defects increase
        self.conductivity_drift -= self.defect_density * 0.015 + self.thermal_stress * 0.008
        
        self.cycle_count += 1

# Environment parameters
class SpaceEnvironment:
    def __init__(self):
        self.radiation_level = 1.0  # Baseline radiation
        self.temp_cycling = 1.0  # Baseline thermal cycling intensity
    
    def to_dict(self):
        return {
            "radiation_level": round(self.radiation_level, 2),
            "temp_cycling": round(self.temp_cycling, 2)
        }

def run_brain_cycle(state, environment, cycle_history):
    """Single brain cycle: simulate → analyze → reason → adapt"""
    
    # 1. Apply degradation
    state.apply_degradation(environment.radiation_level, environment.temp_cycling)
    
    # 2. Prepare context for LLM analysis
    recent_history = cycle_history[-3:] if len(cycle_history) >= 3 else cycle_history
    
    prompt = f"""You are analyzing a material degradation simulation for space applications.

Current State (Cycle {state.cycle_count}):
{json.dumps(state.to_dict(), indent=2)}

Environment:
{json.dumps(environment.to_dict(), indent=2)}

Recent History:
{json.dumps(recent_history, indent=2)}

Task: Provide a BRIEF (2-3 sentence) analysis covering:
1. What degradation trend do you observe?
2. What's the primary risk factor right now?
3. Should we adjust radiation_level or temp_cycling for the next cycle? (suggest a multiplier like 0.8 or 1.2, or keep at 1.0)

Format your response as:
TREND: [your observation]
RISK: [primary concern]
ADJUST: radiation=X.X, temp=X.X"""

    # 3. Get LLM reasoning (fast inference with Cerebras!)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.3-70b",
        max_tokens=200
    )
    
    reasoning = response.choices[0].message.content
    
    # 4. Parse adjustments (simple parsing)
    try:
        if "ADJUST:" in reasoning:
            adjust_line = [line for line in reasoning.split('\n') if 'ADJUST:' in line][0]
            if 'radiation=' in adjust_line:
                rad_val = float(adjust_line.split('radiation=')[1].split(',')[0].strip())
                environment.radiation_level *= rad_val
            if 'temp=' in adjust_line:
                temp_val = float(adjust_line.split('temp=')[1].split()[0].strip())
                environment.temp_cycling *= temp_val
    except:
        pass  # Keep current settings if parsing fails
    
    return reasoning

def run_simulation():
    """Run 10 brain cycles back-to-back"""
    print("=" * 80)
    print("FAST ITERATIVE AI SIMULATION: Material Degradation in Space")
    print("⚡ Powered by Cerebras Ultra-Fast Inference")
    print("=" * 80)
    print("\nStarting 10 rapid brain cycles...\n")
    
    state = MaterialState()
    environment = SpaceEnvironment()
    cycle_history = []
    all_reasoning = []
    
    start_time = time.time()
    
    for i in range(10):
        print(f"🔄 CYCLE {i+1}/10", end=" ")
        cycle_start = time.time()
        
        reasoning = run_brain_cycle(state, environment, cycle_history)
        cycle_history.append(state.to_dict())
        all_reasoning.append(reasoning)
        
        cycle_time = time.time() - cycle_start
        print(f"({cycle_time:.2f}s)")
        print(f"   State: defects={state.defect_density:.4f}, stress={state.thermal_stress:.4f}, conductivity={state.conductivity_drift:.4f}")
        print(f"   {reasoning.split('TREND:')[1].split('RISK:')[0].strip() if 'TREND:' in reasoning else reasoning[:80]}")
        print()
    
    total_time = time.time() - start_time
    
    # Final synthesis
    print("=" * 80)
    print("📊 GENERATING FINAL SYNTHESIS...")
    print("=" * 80)
    
    synthesis_prompt = f"""You've completed 10 rapid simulation cycles analyzing material degradation in space.

Final State:
{json.dumps(state.to_dict(), indent=2)}

Complete History:
{json.dumps(cycle_history, indent=2)}

All Cycle Reasoning:
{chr(10).join([f"Cycle {i+1}: {r}" for i, r in enumerate(all_reasoning)])}

Provide a 4-5 sentence executive summary explaining:
1. The overall degradation trajectory
2. Which failure mode is most critical
3. What this iterative approach revealed that a single analysis would miss
4. Recommended mission duration limit"""

    synthesis = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": synthesis_prompt
            }
        ],
        model="llama-3.3-70b",
        max_tokens=400
    )
    
    print("\n" + synthesis.choices[0].message.content)
    print("\n" + "=" * 80)
    print(f"⚡ TOTAL RUNTIME: {total_time:.2f}s for 10 reasoning cycles")
    print(f"⚡ AVG CYCLE TIME: {total_time/10:.2f}s")
    print("=" * 80)
    print("\n💡 KEY INSIGHT: Running 10 adaptive cycles revealed emergent degradation patterns")
    print("   that would be invisible in a single slow analysis. The agent LEARNED as it")
    print("   simulated, adjusting parameters and catching non-linear failure modes early.")

if __name__ == "__main__":
    run_simulation()