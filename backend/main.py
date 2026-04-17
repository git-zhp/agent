from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
from pathlib import Path
import yaml

app = FastAPI(title="安消大脑 Control Plane")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HERMES_DIR = Path.home() / ".hermes"
PROFILES_DIR = HERMES_DIR / "profiles"

class EmployeeCreate(BaseModel):
    name: str
    role: str
    description: str

class EmployeeUpdate(BaseModel):
    description: str

class ToolsetUpdate(BaseModel):
    toolsets: list[str]

@app.get("/api/employees")
def list_employees():
    employees = []
    if PROFILES_DIR.exists():
        for p in PROFILES_DIR.iterdir():
            if p.is_dir():
                # Read SOUL.md if exists
                soul_path = p / "SOUL.md"
                soul = soul_path.read_text(encoding="utf-8") if soul_path.exists() else ""
                
                status = "running" if p.name in gateway_processes and gateway_processes[p.name].poll() is None else "idle"
                employees.append({
                    "name": p.name,
                    "soul": soul,
                    "status": status
                })
    return {"employees": employees}

@app.post("/api/employees")
def create_employee(emp: EmployeeCreate):
    # Call hermes to create profile
    cmd = ["uv", "run", "hermes", "profile", "create", emp.name]
    try:
        subprocess.run(cmd, cwd="/workspace/hermes-agent", check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"Failed to create profile: {e.stderr.decode()}")

    # Write SOUL.md
    profile_dir = PROFILES_DIR / emp.name
    profile_dir.mkdir(parents=True, exist_ok=True)
    soul_content = f"# Role: {emp.role}\n\n{emp.description}"
    (profile_dir / "SOUL.md").write_text(soul_content, encoding="utf-8")

    return {"status": "success", "name": emp.name}

@app.delete("/api/employees/{name}")
def delete_employee(name: str):
    cmd = ["uv", "run", "hermes", "profile", "delete", name, "--force"]
    try:
        subprocess.run(cmd, cwd="/workspace/hermes-agent", check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        # Ignore if profile doesn't exist
        pass
    return {"status": "success"}

@app.get("/api/employees/{name}/tools")
def get_employee_tools(name: str):
    config_path = PROFILES_DIR / name / "config.yaml"
    if not config_path.exists():
        return {"toolsets": []}
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    
    toolsets = config.get("enabled_toolsets", [])
    return {"toolsets": toolsets}

@app.post("/api/employees/{name}/tools")
def update_employee_tools(name: str, update: ToolsetUpdate):
    config_path = PROFILES_DIR / name / "config.yaml"
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    
    config["enabled_toolsets"] = update.toolsets
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)
        
    return {"status": "success"}

gateway_processes = {}

@app.post("/api/employees/{name}/gateway/start")
def start_gateway(name: str):
    if name in gateway_processes and gateway_processes[name].poll() is None:
        return {"status": "error", "msg": f"Gateway for {name} is already running."}
    
    # Start the gateway process in the background
    try:
        process = subprocess.Popen(
            ["uv", "run", "hermes", "-p", name, "gateway", "start"],
            cwd="/workspace/hermes-agent",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        gateway_processes[name] = process
        return {"status": "success", "msg": f"Gateway for {name} started."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/employees/{name}/gateway/stop")
def stop_gateway(name: str):
    if name in gateway_processes:
        process = gateway_processes[name]
        if process.poll() is None:
            process.terminate()
            return {"status": "success", "msg": f"Gateway for {name} stopped."}
    return {"status": "error", "msg": f"Gateway for {name} is not running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
