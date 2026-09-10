"""
Gemini CLI Interface

Provides a natural language command interface to the NetworkBuster AI Pipeline.
Simulates an LLM agent to interpret user queries about system status, logs, and models.
"""

import sys
import os
import json
import argparse
import random
from datetime import datetime

class GeminiAgent:
    def __init__(self):
        self.state_file = "evolution_state.json"
        
    def respond(self, query: str):
        query = query.lower()
        
        if "status" in query or "state" in query:
            return self.get_system_status()
        elif "model" in query or "registry" in query:
            return self.list_models()
        elif "log" in query or "history" in query:
            return self.get_latest_logs()
        elif "help" in query:
            return self.print_help()
        else:
            return "Gemini: I am listening. You can ask me about 'system status', 'available models', or 'recent logs'."

    def get_system_status(self):
        if not os.path.exists(self.state_file):
            return "Gemini: System state not found. The continuous learning engine may not have run yet."
            
        with open(self.state_file, 'r') as f:
            state = json.load(f)
            
        return f"""
Gemini System Report
--------------------
Generation: {state.get('generation', 0)}
Last Update: {state.get('last_update', 'Never')}
Samples Processed: {state.get('total_samples_processed', 0)}
Active Models: {len(state.get('models', {}))}
Status: ONLINE and EVOLVING
"""

    def list_models(self):
        checkpoint_dir = "checkpoints"
        if not os.path.exists(checkpoint_dir):
            return "Gemini: No checkpoints found."
            
        models = [f for f in os.listdir(checkpoint_dir) if f.endswith('.joblib')]
        if not models:
            return "Gemini: Registry is empty."
            
        return "Gemini: Found the following active models in registry:\n" + "\n".join([f" - {m}" for m in models])

    def get_latest_logs(self):
        # Simulated log retrieval - in production read from log files
        return f"Gemini: Retrieved latest system logs...\n[{datetime.utcnow().isoformat()}] INGESTION: System active.\n[{datetime.utcnow().isoformat()}] SECURITY: Integrity checks passed."

    def print_help(self):
        return """
Gemini CLI Help
---------------
Try asking:
- "What is the current system status?"
- "Show me available models"
- "Check recent logs"
- "How many generations have evolved?"
"""

def main():
    parser = argparse.ArgumentParser(description="Gemini Interface for NetworkBuster AI")
    parser.add_argument("query", nargs="*", help="Natural language query")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive session")
    args = parser.parse_args()
    
    agent = GeminiAgent()
    
    if args.interactive:
        print("Gemini AI Interface Online. (Type 'exit' to quit)")
        while True:
            try:
                user_input = input("User> ")
                if user_input.lower() in ('exit', 'quit'):
                    break
                print(agent.respond(user_input))
            except KeyboardInterrupt:
                break
    else:
        if not args.query:
            print(agent.respond("help"))
        else:
            query = " ".join(args.query)
            print(agent.respond(query))

if __name__ == "__main__":
    main()
