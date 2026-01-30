#!/usr/bin/env python3
"""
Automated Drone Simulation Runner
Runs through drone operations with pre-configured settings
"""

import sys
import time
from drone_flight_system import DroneState, UnbreakableAutopilot, ScanAlgorithms
from security_verification import UserVerification, SecurityLevel

def automated_simulation():
    print("=" * 60)
    print("AUTOMATED DRONE FLIGHT SIMULATION")
    print("=" * 60)
    
    # Authenticate
    print("\n🔐 Authenticating with system credentials...")
    verifier = UserVerification()
    
    # Try to use existing session first
    session = verifier.load_session()
    if not session:
        print("No active session found. Logging in as admin...")
        # Authenticate with credentials
        username = "admin"
        password = "admin123"
        success, session = verifier.authenticate(username=username, password=password, interactive=False)
        
        if success:
            print(f"✅ Authenticated as {username}")
        else:
            print("❌ Authentication failed")
            return
    else:
        print(f"✅ Using existing session: {session['username']} (Level {session['level']})")
    
    # Check clearance
    if not verifier.require_level(SecurityLevel.OPERATOR):
        print("❌ Insufficient clearance for drone operations")
        return
    
    print("\n🚁 Initializing Drone System...")
    time.sleep(1)
    
    # Create drone
    drone1 = DroneState(drone_id="ALPHA-1")
    autopilot = UnbreakableAutopilot(drone1)
    
    print("\n" + "=" * 60)
    print("SIMULATION 1: SPIRAL SEARCH PATTERN")
    print("=" * 60)
    print("Generating wide-area spiral search pattern...")
    path1 = ScanAlgorithms.generate_spiral_search(0, 0, 50, spacing=8.0)
    print(f"Generated {len(path1)} waypoints")
    autopilot.execute_pattern("SPIRAL_ALPHA", path1[:15])  # Run first 15 waypoints
    
    time.sleep(2)
    
    # Reset battery for next mission
    drone1.battery = 100.0
    drone1.integrity = 100.0
    
    print("\n" + "=" * 60)
    print("SIMULATION 2: GRID RASTER SCAN")
    print("=" * 60)
    print("Generating detailed grid raster pattern...")
    path2 = ScanAlgorithms.generate_grid_raster(30, 30, altitude=15.0, density=8.0)
    print(f"Generated {len(path2)} waypoints")
    autopilot.execute_pattern("GRID_BETA", path2[:15])  # Run first 15 waypoints
    
    time.sleep(2)
    
    # Final diagnostics
    print("\n" + "=" * 60)
    print("FINAL SYSTEM DIAGNOSTICS")
    print("=" * 60)
    print(f"Drone ID: {drone1.id}")
    print(f"Final Battery: {drone1.battery:.1f}%")
    print(f"Structural Integrity: {drone1.integrity}%")
    print(f"Final Position: X={drone1.position['x']:.1f}, Y={drone1.position['y']:.1f}, Z={drone1.position['z']:.1f}")
    print(f"Status: {drone1.status}")
    
    if autopilot.error_log:
        print(f"\nErrors Encountered: {len(autopilot.error_log)}")
        for i, error in enumerate(autopilot.error_log, 1):
            print(f"  {i}. {error}")
    else:
        print("\n✅ No errors encountered during flight operations")
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    try:
        automated_simulation()
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()
