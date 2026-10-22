"""MCP Stdio Server for Consistent Hash Ring Router.
100% Python Standard Library.
"""
import sys
import json
from client import ConsistentHashRingRouter

router = ConsistentHashRingRouter()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-consistent-hash-ring-router-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "add_nodes",
                "description": "Add physical server or cache shard nodes into consistent hash ring",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nodes": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["nodes"]
                }
            },
            {
                "name": "remove_node",
                "description": "Safely remove a node from consistent ring with minimal key migration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "node": {"type": "string"}
                    },
                    "required": ["node"]
                }
            },
            {
                "name": "get_node_for_key",
                "description": "Determine target shard/node for a given cache key or prompt hash",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"}
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "get_distribution_stats",
                "description": "Calculate key balance and load spread standard deviation across nodes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sample_keys": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["sample_keys"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "add_nodes":
            out = router.add_nodes(args.get("nodes", []))
        elif name == "remove_node":
            out = router.remove_node(args.get("node", ""))
        elif name == "get_node_for_key":
            out = {"key": args.get("key"), "assigned_node": router.get_node_for_key(args.get("key", ""))}
        elif name == "get_distribution_stats":
            out = router.get_distribution_stats(args.get("sample_keys", []))
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
