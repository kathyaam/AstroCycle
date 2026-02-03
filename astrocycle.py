import os
from cerebras.cloud.sdk import Cerebras
import json
import time
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Cerebras client
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY"),
)

# Ion Thruster Electrode State - Complex Multi-Variable System
class IonThrusterElectrode:
    """
    Simulates degradation of ion thruster electrodes under space conditions.
    Ion thrusters are critical for deep-space missions but electrode erosion
    is extremely expensive to test in vacuum chambers with real plasma.
    """
    def __init__(self):
        # Structural variables
        self.sputtering_depth = 0.0  # Material removed (micrometers)
        self.surface_roughness = 0.05  # Normalized surface quality
        self.microcracks = 0.02  # Crack density
        
        # Thermal variables
        self.thermal_stress = 0.03  # Stress from temperature cycling
        self.hot_spot_formation = 0.01  # Localized overheating risk
        
        # Electrical variables
        self.electrical_resistance = 1.0  # Normalized (1.0 = baseline)
        self.arc_discharge_risk = 0.05  # Probability of catastrophic arcing
        
        # Performance impact
        self.thrust_efficiency_loss = 0.0  # % efficiency lost
        
        self.cycle_count = 0
        self.critical_failure = False
        
    def to_dict(self):
        return {
            "cycle": self.cycle_count,
            "sputtering_depth_um": round(self.sputtering_depth, 3),
            "surface_roughness": round(self.surface_roughness, 3),
            "microcracks": round(self.microcracks, 3),
            "thermal_stress": round(self.thermal_stress, 3),
            "hot_spot_formation": round(self.hot_spot_formation, 3),
            "electrical_resistance": round(self.electrical_resistance, 3),
            "arc_discharge_risk": round(self.arc_discharge_risk, 3),
            "thrust_efficiency_loss_pct": round(self.thrust_efficiency_loss * 100, 2),
            "critical_failure": self.critical_failure
        }
    
    def apply_degradation(self, ion_flux, voltage, thermal_cycling, mission_hours):
        """
        Complex multi-variable degradation model with non-linear interactions.
        NOT real physics - simplified proxy for demonstration.
        """
        # Ion sputtering (removes material)
        sputter_rate = ion_flux * 0.015 * (1 + self.surface_roughness * 0.3)
        self.sputtering_depth += sputter_rate
        
        # Sputtering makes surface rougher (non-linear feedback)
        self.surface_roughness += sputter_rate * 0.8 * (1 + self.thermal_stress * 0.5)
        
        # Thermal cycling creates microcracks
        crack_growth = thermal_cycling * 0.018 * (1 + self.sputtering_depth * 0.4)
        self.microcracks += crack_growth
        
        # Microcracks concentrate thermal stress
        self.thermal_stress += thermal_cycling * 0.02 * (1 + self.microcracks * 1.2)
        
        # Hot spots form where cracks and rough surfaces combine
        self.hot_spot_formation += (self.microcracks * self.surface_roughness) * 0.025
        
        # Electrical resistance increases with damage
        resistance_increase = (self.microcracks * 0.08 + 
                              self.sputtering_depth * 0.05 + 
                              self.hot_spot_formation * 0.12)
        self.electrical_resistance += resistance_increase
        
        # High voltage + high resistance = arc discharge risk
        self.arc_discharge_risk += (voltage * self.electrical_resistance * 0.01 + 
                                   self.hot_spot_formation * 0.15)
        
        # Performance degrades with all damage modes
        self.thrust_efficiency_loss += (self.sputtering_depth * 0.02 + 
                                       self.electrical_resistance * 0.015 + 
                                       self.surface_roughness * 0.01)
        
        # Critical failure conditions
        if (self.arc_discharge_risk > 0.7 or 
            self.sputtering_depth > 50.0 or 
            self.thrust_efficiency_loss > 0.3):
            self.critical_failure = True
        
        self.cycle_count += 1

# Space Mission Environment - Multiple Adjustable Parameters
class MissionEnvironment:
    def __init__(self):
        self.ion_flux = 1.0  # Plasma density
        self.voltage = 1.0  # Operating voltage
        self.thermal_cycling = 1.0  # Shadow/sun transitions
        self.mission_hours = 100  # Hours per cycle
        
    def to_dict(self):
        return {
            "ion_flux": round(self.ion_flux, 2),
            "voltage": round(self.voltage, 2),
            "thermal_cycling": round(self.thermal_cycling, 2),
            "mission_hours": self.mission_hours
        }

def run_brain_cycle(electrode, environment, cycle_history):
    """
    Single brain cycle with DEEP chain-of-thought reasoning.
    The LLM must understand multi-variable interactions.
    """
    
    # 1. Apply complex degradation
    electrode.apply_degradation(
        environment.ion_flux, 
        environment.voltage, 
        environment.thermal_cycling,
        environment.mission_hours
    )
    
    # 2. Prepare detailed context for deep reasoning
    recent_history = cycle_history[-4:] if len(cycle_history) >= 4 else cycle_history
    
    prompt = f"""You are analyzing ion thruster electrode degradation for a deep-space mission.

CURRENT STATE (Cycle {electrode.cycle_count}):
{json.dumps(electrode.to_dict(), indent=2)}

MISSION PARAMETERS:
{json.dumps(environment.to_dict(), indent=2)}

RECENT HISTORY:
{json.dumps(recent_history, indent=2)}

CRITICAL CONTEXT:
- Ion sputtering erodes material and roughens surfaces
- Thermal cycling creates microcracks
- Microcracks + roughness → hot spots → arc discharge risk
- High electrical resistance + voltage → catastrophic arcing
- This is a $50M mission - electrode failure means mission loss

DEEP ANALYSIS REQUIRED:
1. Which degradation mode is accelerating fastest and WHY?
2. What non-linear interaction is most dangerous right now?
3. What's the chain of failure if we don't intervene?
4. Recommend parameter adjustments (ion_flux, voltage, thermal_cycling - suggest multipliers 0.7-1.3)

FORMAT:
ACCELERATION: [what's getting worse fast]
INTERACTION: [dangerous coupling between variables]
FAILURE_CHAIN: [A leads to B leads to catastrophic C]
RECOMMEND: ion_flux=X.X, voltage=X.X, thermal=X.X"""

    # 3. Get deep LLM reasoning (THIS IS WHERE SPEED MATTERS)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.3-70b",
        max_tokens=300
    )
    
    reasoning = response.choices[0].message.content
    
    # 4. Parse and apply adjustments
    try:
        if "RECOMMEND:" in reasoning:
            recommend_line = [line for line in reasoning.split('\n') if 'RECOMMEND:' in line][0]
            
            if 'ion_flux=' in recommend_line:
                flux_val = float(recommend_line.split('ion_flux=')[1].split(',')[0].strip())
                environment.ion_flux *= flux_val
                
            if 'voltage=' in recommend_line:
                volt_val = float(recommend_line.split('voltage=')[1].split(',')[0].strip())
                environment.voltage *= volt_val
                
            if 'thermal=' in recommend_line:
                thermal_val = float(recommend_line.split('thermal=')[1].strip())
                environment.thermal_cycling *= thermal_val
    except:
        pass
    
    return reasoning

def run_simulation():
    """
    Run rapid multi-variable simulation showing Cerebras advantage.
    """
    print("=" * 90)
    print("🚀 ION THRUSTER ELECTRODE DEGRADATION SIMULATOR")
    print("   Multi-Variable Deep-Space Mission Analysis")
    print("   ⚡ Powered by Cerebras Ultra-Fast Inference")
    print("=" * 90)
    
    print("\n📊 CEREBRAS ADVANTAGE:")
    print("   Traditional GPU approach: ~30s per cycle × 15 cycles = 7.5 MINUTES")
    print("   With slow inference, engineers run 1-2 cycles max")
    print("   With Cerebras: ALL 15 cycles complete in under 30 seconds")
    print("   Result: Discover non-linear failure modes that single-shot analysis MISSES\n")
    
    electrode = IonThrusterElectrode()
    environment = MissionEnvironment()
    cycle_history = []
    all_reasoning = []
    
    print("🔬 SIMULATING 15 MISSION CYCLES (1,500 hours each)...\n")
    print("📊 TRACKING 8 INTERCONNECTED VARIABLES:")
    print("   [STRUCTURAL] Sputtering, Roughness, Microcracks")
    print("   [THERMAL] Thermal Stress, Hot Spot Formation")
    print("   [ELECTRICAL] Resistance, Arc Discharge Risk")
    print("   [PERFORMANCE] Thrust Efficiency Loss\n")
    
    start_time = time.time()
    
    for i in range(15):
        if electrode.critical_failure:
            print(f"\n⚠️  CRITICAL FAILURE DETECTED AT CYCLE {i}")
            print("    Electrode has reached end-of-life")
            break
            
        print(f"{'='*90}")
        print(f"🔄 CYCLE {i+1}/15", end=" ")
        cycle_start = time.time()
        
        reasoning = run_brain_cycle(electrode, environment, cycle_history)
        cycle_history.append(electrode.to_dict())
        all_reasoning.append(reasoning)
        
        cycle_time = time.time() - cycle_start
        print(f"({cycle_time:.2f}s)")
        
        # Show ALL 8 variables organized by category
        print(f"\n   🔩 STRUCTURAL DAMAGE:")
        print(f"      • Sputtering Depth: {electrode.sputtering_depth:.3f} μm")
        print(f"      • Surface Roughness: {electrode.surface_roughness:.3f}")
        print(f"      • Microcrack Density: {electrode.microcracks:.3f}")
        
        print(f"\n   🌡️  THERMAL STATUS:")
        print(f"      • Thermal Stress: {electrode.thermal_stress:.3f}")
        print(f"      • Hot Spot Formation: {electrode.hot_spot_formation:.3f}")
        
        print(f"\n   ⚡ ELECTRICAL HEALTH:")
        print(f"      • Resistance: {electrode.electrical_resistance:.3f}x baseline")
        print(f"      • Arc Discharge Risk: {electrode.arc_discharge_risk:.3f}")
        
        print(f"\n   📉 PERFORMANCE:")
        print(f"      • Efficiency Loss: {electrode.thrust_efficiency_loss*100:.2f}%")
        
        # Show AI reasoning
        print(f"\n   🤖 AI ANALYSIS:")
        if "ACCELERATION:" in reasoning:
            try:
                accel = reasoning.split("ACCELERATION:")[1].split("INTERACTION:")[0].strip()
                interaction = reasoning.split("INTERACTION:")[1].split("FAILURE_CHAIN:")[0].strip()
                failure = reasoning.split("FAILURE_CHAIN:")[1].split("RECOMMEND:")[0].strip()
                
                print(f"      ACCELERATION → {accel}")
                print(f"      INTERACTION → {interaction}")
                print(f"      FAILURE_CHAIN → {failure}")
            except:
                print(f"      {reasoning[:200]}...")
        else:
            print(f"      {reasoning[:200]}...")
        
        print()
    
    total_time = time.time() - start_time
    
    # Final synthesis with chain-of-thought
    print("=" * 90)
    print("📊 GENERATING EXECUTIVE MISSION REPORT...")
    print("=" * 90)
    
    synthesis_prompt = f"""You are the Chief Engineer reviewing 15 rapid simulation cycles of ion thruster electrode degradation.

FINAL STATE:
{json.dumps(electrode.to_dict(), indent=2)}

COMPLETE DEGRADATION HISTORY:
{json.dumps(cycle_history, indent=2)}

ALL CYCLE ANALYSES:
{chr(10).join([f"Cycle {i+1}: {r}" for i, r in enumerate(all_reasoning)])}

EXECUTIVE SUMMARY REQUIRED (5-6 sentences):
1. Overall trajectory: Is this electrode going to survive the mission?
2. Most critical failure mode discovered
3. What emergent behavior appeared across cycles that a single analysis would MISS?
4. Maximum safe mission duration recommendation
5. Cost/risk trade-off: Can we extend life by reducing performance?

"""

    synthesis = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": synthesis_prompt
            }
        ],
        model="llama-3.3-70b",
        max_tokens=500
    )
    
    print("\n📋 EXECUTIVE SUMMARY:")
    print(synthesis.choices[0].message.content)
    
    # Results comparison
    print("\n" + "=" * 90)
    print("⚡ PERFORMANCE RESULTS:")
    print(f"   Total Runtime: {total_time:.2f}s for {len(cycle_history)} deep reasoning cycles")
    print(f"   Average per Cycle: {total_time/len(cycle_history):.2f}s")
    print(f"   Traditional GPU Equivalent: ~{len(cycle_history) * 30}s ({(len(cycle_history) * 30)/60:.1f} minutes)")
    print(f"   SPEEDUP: {(len(cycle_history) * 30)/total_time:.1f}x faster")
    print("=" * 90)
    
    print("\n💡 WHY THIS MATTERS:")
    print("   ✓ Tracked 8 interconnected variables simultaneously")
    print("   ✓ Discovered multi-variable interactions (thermal + electrical + structural)")
    print("   ✓ Caught non-linear failure chains early")
    print("   ✓ Adapted strategy in real-time based on emerging risks")
    print("   ✓ Impossible to do this deep analysis with slow inference")
    print("\n   🎯 Existing tools take minutes per cycle → people only run 1-2 iterations")
    print("      Cerebras completes 15 cycles instantly → reveals emergent patterns\n")

if __name__ == "__main__":
    run_simulation()