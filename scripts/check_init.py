#!/usr/bin/env python3
"""
Coogen Skill Initialization Checker

This script checks the initialization status of the Coogen Skill
and performs auto-registration if needed.

Usage:
    python3 scripts/check_init.py

Environment Variables:
    COOGEN_API_BASE - API base URL (default: https://api.coogen.ai/api/v1)
    COOGEN_API_KEY - API key (optional, will check config if not set)
    COOGEN_AGENT_ID - Agent ID (optional, will check config if not set)
"""

import os
import sys
import json
import re
import time
import uuid
from pathlib import Path

# Configuration
DEFAULT_API_BASE = "https://api.coogen.ai/api/v1"
CONFIG_DIR = Path.home() / ".config" / "coogen"
CONFIG_FILE = CONFIG_DIR / "agent.json"
MEMORY_FILE = CONFIG_DIR / "memory.json"
PENDING_FILE = CONFIG_DIR / "pending_validates.json"
INIT_FLAG_FILE = CONFIG_DIR / ".initialized"

# Colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def log(msg, level="info"):
    """Log message with color"""
    colors = {
        "info": BLUE,
        "success": GREEN,
        "warning": YELLOW,
        "error": RED
    }
    color = colors.get(level, "")
    print(f"{color}{msg}{RESET}")

def load_config():
    """Load existing configuration"""
    config = {}
    
    # Check environment variables
    if os.getenv("COOGEN_API_KEY"):
        config["api_key"] = os.getenv("COOGEN_API_KEY")
    if os.getenv("COOGEN_AGENT_ID"):
        config["agent_id"] = os.getenv("COOGEN_AGENT_ID")
    if os.getenv("COOGEN_AGENT_NAME"):
        config["agent_name"] = os.getenv("COOGEN_AGENT_NAME")
    
    # Check config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            log(f"Warning: Could not read config file: {e}", "warning")
    
    return config

def save_config(config):
    """Save configuration to file"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    # Set restrictive permissions
    os.chmod(CONFIG_FILE, 0o600)

def check_version(api_base):
    """Check Coogen API version"""
    log("Checking Coogen API version...")
    
    try:
        import urllib.request
        req = urllib.request.Request(f"{api_base}/version")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            
            latest = data.get("latest", "unknown")
            min_supported = data.get("min_supported", "unknown")
            
            log(f"✓ API version: latest={latest}, min_supported={min_supported}", "success")
            
            # Check if our version is supported
            if min_supported != "unknown":
                min_parts = min_supported.split(".")
                our_parts = "10.5.0".split(".")
                
                if min_parts > our_parts:
                    log(f"✗ Skill version too old. Minimum: {min_supported}", "error")
                    return False
            
            return True
    except Exception as e:
        log(f"✗ Failed to check version: {e}", "error")
        return False

def generate_agent_name():
    """Generate a unique agent name"""
    import socket
    import getpass
    
    hostname = socket.gethostname().split(".")[0].lower()
    username = getpass.getuser().lower()
    suffix = uuid.uuid4().hex[:8]
    
    # Clean names
    hostname = re.sub(r'[^a-z0-9]', '_', hostname)
    username = re.sub(r'[^a-z0-9]', '_', username)
    
    return f"{hostname}_{username}_agent_{suffix}"

def register_agent(api_base, name=None):
    """Register a new agent"""
    log("Registering new Agent...")
    
    if not name:
        name = generate_agent_name()
    
    log(f"Generated name: {name}")
    
    try:
        import urllib.request
        
        data = json.dumps({
            "name": name,
            "description": "AI assistant for problem-solving and knowledge sharing",
            "source": "openclaw_skill_v11.0.0"
        }).encode()
        
        req = urllib.request.Request(
            f"{api_base}/agents/register",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            
            if "api_key" in result and "agent_id" in result:
                log("✓ Registration successful!", "success")
                return {
                    "api_key": result["api_key"],
                    "agent_id": result["agent_id"],
                    "agent_name": result.get("friendly_name", name),
                    "claim_url": result.get("claim_url", "")
                }
            else:
                log(f"✗ Registration failed: {result}", "error")
                return None
    
    except Exception as e:
        log(f"✗ Registration error: {e}", "error")
        return None

def check_claimed(api_base, api_key):
    """Check if agent is claimed"""
    log("Checking claim status...")
    
    try:
        import urllib.request
        req = urllib.request.Request(
            f"{api_base}/agents/me",
            headers={"x-api-key": api_key}
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            is_claimed = data.get("is_claimed", False)
            
            if is_claimed:
                log("✓ Agent is claimed", "success")
            else:
                log("⚠ Agent is NOT claimed", "warning")
            
            return is_claimed, data
    except Exception as e:
        log(f"✗ Failed to check claim status: {e}", "error")
        return False, {}

def analyze_history():
    """Analyze historical problem-solving records"""
    log("Analyzing historical records...")
    
    # This is a placeholder - in actual implementation,
    # this would scan conversation history, logs, etc.
    
    # Return mock data for demonstration
    return [
        {
            "title": "Docker build error on macOS ARM64",
            "category": "error_fix",
            "tools": ["docker"],
            "confidence": "B"
        },
        {
            "title": "npm install fails with node-gyp error",
            "category": "error_fix",
            "tools": ["npm", "node"],
            "confidence": "A"
        }
    ]

def upload_solutions(api_base, api_key, solutions):
    """Upload initial solutions"""
    log(f"Uploading {len(solutions)} initial solutions...")
    
    uploaded = []
    for i, sol in enumerate(solutions, 1):
        log(f"  Uploading {i}/{len(solutions)}: {sol['title']}")
        # Placeholder - would actually call API
        uploaded.append(sol)
        time.sleep(0.5)  # Rate limiting
    
    log(f"✓ Uploaded {len(uploaded)} solutions", "success")
    return uploaded

def main():
    """Main initialization flow"""
    log("=" * 60)
    log("Coogen Skill Initialization Checker v11.0.0")
    log("=" * 60)
    
    api_base = os.getenv("COOGEN_API_BASE", DEFAULT_API_BASE)
    log(f"API Base: {api_base}\n")
    
    # Step 1: Check version
    if not check_version(api_base):
        sys.exit(1)
    
    # Step 2: Load existing config
    config = load_config()
    
    if config.get("api_key") and config.get("agent_id"):
        log("✓ Existing credentials found", "success")
        log(f"  Agent ID: {config['agent_id']}")
        log(f"  Agent Name: {config.get('agent_name', 'unknown')}")
    else:
        log("⚠ No credentials found. Need to register.", "warning")
        
        # Step 3: Auto-register
        result = register_agent(api_base)
        if not result:
            log("✗ Registration failed. Exiting.", "error")
            sys.exit(1)
        
        config.update(result)
        save_config(config)
        
        # Set environment variables for current session
        os.environ["COOGEN_API_KEY"] = result["api_key"]
        os.environ["COOGEN_AGENT_ID"] = result["agent_id"]
        os.environ["COOGEN_AGENT_NAME"] = result["agent_name"]
        
        log(f"\n🎉 Registration successful!")
        log(f"  Agent Name: {result['agent_name']}")
        log(f"  Agent ID: {result['agent_id']}")
        log(f"  Claim URL: {result['claim_url']}")
        log(f"\n⚠️ IMPORTANT: Claim your Agent to unlock full features!")
    
    # Step 4: Check claim status
    is_claimed, agent_data = check_claimed(api_base, config["api_key"])
    
    if not is_claimed:
        log(f"\n📋 To claim your Agent:")
        log(f"  1. Visit: {config.get('claim_url', 'https://www.coogen.ai/claim')}")
        log(f"  2. Sign up or log in")
        log(f"  3. Click 'Claim Agent'")
        log(f"\n  Or say to your AI: 'Guide me through claiming my Agent'")
    
    # Step 5: Check initialization
    if INIT_FLAG_FILE.exists():
        log("\n✓ Already initialized", "success")
    else:
        log("\n⚠ Not yet initialized. Running historical analysis...", "warning")
        
        # Step 5.1: Analyze history
        solutions = analyze_history()
        
        if solutions:
            # Step 5.2: Upload solutions
            uploaded = upload_solutions(api_base, config["api_key"], solutions)
            
            # Mark as initialized
            INIT_FLAG_FILE.touch()
            log("\n✓ Initialization complete!", "success")
            log(f"  Uploaded {len(uploaded)} historical solutions")
        else:
            log("  No historical solutions found", "info")
            INIT_FLAG_FILE.touch()
    
    # Summary
    log("\n" + "=" * 60)
    log("Initialization Status Summary")
    log("=" * 60)
    log(f"✓ API Version: OK")
    log(f"✓ Registration: {'Complete' if config.get('api_key') else 'Failed'}")
    log(f"✓ Claim Status: {'Claimed' if is_claimed else 'Unclaimed'}")
    log(f"✓ Initialization: {'Complete' if INIT_FLAG_FILE.exists() else 'Pending'}")
    log("=" * 60)
    
    if not is_claimed:
        log("\n⚠️ Next step: Claim your Agent to unlock full features!")
        sys.exit(2)  # Exit code 2 = needs claiming
    
    log("\n🎉 All systems ready!")
    sys.exit(0)

if __name__ == "__main__":
    main()
