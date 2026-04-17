import json
from tools.registry import registry

def fire_alarm_query(status: str = "all", task_id: str = None) -> str:
    """Mock implementation for querying fire alarms."""
    alarms = [
        {"id": "A001", "location": "Building 1, Floor 2", "status": "active", "type": "Smoke Detector"},
        {"id": "A002", "location": "Building 3, Basement", "status": "resolved", "type": "Heat Detector"}
    ]
    if status != "all":
        alarms = [a for a in alarms if a["status"] == status]
    return json.dumps({"success": True, "data": alarms})

def cctv_query(location: str, task_id: str = None) -> str:
    """Mock implementation for querying CCTV."""
    return json.dumps({
        "success": True,
        "data": {
            "location": location,
            "status": "online",
            "ai_analysis": "No anomalies detected. Personnel present: 2.",
            "stream_url": f"rtsp://mock-cctv.local/{location.replace(' ', '_')}"
        }
    })

def device_control(device_id: str, command: str, task_id: str = None) -> str:
    """Mock implementation for controlling safety devices (e.g., sprinklers, doors)."""
    return json.dumps({
        "success": True,
        "data": {
            "device_id": device_id,
            "command_executed": command,
            "status": "success"
        }
    })

_FIRE_ALARM_SCHEMA = {
    "name": "fire_alarm_query",
    "description": "查询全区消防报警记录状态 (Query the current fire alarm status across the campus).",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "过滤报警状态 (Filter alarms by status), e.g., 'all', 'active', 'resolved'",
                "enum": ["all", "active", "resolved"]
            }
        },
        "required": []
    }
}

_CCTV_SCHEMA = {
    "name": "cctv_query",
    "description": "查询指定位置的监控摄像头状态与AI分析结果 (Query CCTV status and AI analysis for a specific location).",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "位置名称 (Location name), e.g., 'Building 1, Floor 2'"
            }
        },
        "required": ["location"]
    }
}

_DEVICE_CONTROL_SCHEMA = {
    "name": "device_control",
    "description": "控制安防消防设备，如远程开门、启动喷淋等 (Control safety and fire prevention devices).",
    "parameters": {
        "type": "object",
        "properties": {
            "device_id": {
                "type": "string",
                "description": "设备ID (Device ID)"
            },
            "command": {
                "type": "string",
                "description": "控制指令 (Control command), e.g., 'open', 'close', 'activate'"
            }
        },
        "required": ["device_id", "command"]
    }
}

registry.register(
    name="fire_alarm_query",
    toolset="safety_fire",
    schema=_FIRE_ALARM_SCHEMA,
    handler=lambda args, **kw: fire_alarm_query(status=args.get("status", "all"), task_id=kw.get("task_id")),
    emoji="🔥",
)

registry.register(
    name="cctv_query",
    toolset="safety_fire",
    schema=_CCTV_SCHEMA,
    handler=lambda args, **kw: cctv_query(location=args.get("location", ""), task_id=kw.get("task_id")),
    emoji="📹",
)

registry.register(
    name="device_control",
    toolset="safety_fire",
    schema=_DEVICE_CONTROL_SCHEMA,
    handler=lambda args, **kw: device_control(device_id=args.get("device_id", ""), command=args.get("command", ""), task_id=kw.get("task_id")),
    emoji="⚙️",
)
