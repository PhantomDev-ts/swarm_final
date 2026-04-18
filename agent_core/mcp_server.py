"""
agent_core/mcp_server.py

Servidor MCP (Model Context Protocol) que expõe as tools exclusivas
do Swarm para o OpenClaude usar nativamente:
  - generate_image    (Z-Image-Turbo)
  - generate_video    (LTX-2.3)
  - generate_video_parallel
  - analyse_video     (ffmpeg + visão)
  - web_search
  - memory_save / memory_get

OpenClaude já tem: bash, file edit, grep, glob, web_fetch, agents.
O MCP adiciona as ferramentas únicas do Swarm que ele não tem.

Protocolo: JSON-RPC 2.0 sobre stdio (padrão MCP).
"""

import sys
import json
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def _respond(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if error:
        msg["error"] = {"code": -32000, "message": str(error)}
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def _list_tools():
    return {
        "tools": [
            {
                "name": "generate_image",
                "description": (
                    "Gera uma imagem com Z-Image-Turbo (6B params, 8 steps). "
                    "Excelente para fotorrealismo e texto renderizado. "
                    "Retorna o caminho do arquivo PNG gerado."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt":          {"type": "string", "description": "Descrição da imagem"},
                        "negative_prompt": {"type": "string", "description": "O que evitar"},
                        "width":           {"type": "integer", "default": 1024},
                        "height":          {"type": "integer", "default": 1024},
                        "steps":           {"type": "integer", "default": 8},
                        "seed":            {"type": "integer", "default": -1},
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "generate_video",
                "description": (
                    "Gera um vídeo com LTX-2.3 GGUF (~6GB VRAM). "
                    "Suporta texto-para-vídeo com movimento descrito no prompt. "
                    "num_frames deve ser: 49, 65, 97, 121, 161 (97 ≈ 4s a 24fps). "
                    "Retorna o caminho do arquivo MP4."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt":      {"type": "string"},
                        "num_frames":  {"type": "integer", "default": 97},
                        "fps":         {"type": "integer", "default": 24},
                        "seed":        {"type": "integer", "default": -1},
                        "device_idx":  {"type": "integer", "default": 0, "description": "GPU 0 ou 1"},
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "generate_videos_parallel",
                "description": (
                    "Gera múltiplos vídeos em paralelo usando GPU 0 e GPU 1 simultaneamente. "
                    "Ideal para criar várias cenas de uma vez."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompts":    {"type": "array", "items": {"type": "string"}},
                        "num_frames": {"type": "integer", "default": 97},
                        "fps":        {"type": "integer", "default": 24},
                    },
                    "required": ["prompts"],
                },
            },
            {
                "name": "analyse_video",
                "description": (
                    "Analisa um vídeo frame-a-frame com IA de visão (ffmpeg + Qwen Vision). "
                    "Identifica padrões virais, hooks, ritmo de edição e fórmula replicável. "
                    "Aceita caminho local ou URL."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "video_path": {"type": "string", "description": "Caminho ou URL do vídeo"},
                        "question":   {"type": "string", "description": "O que analisar (opcional)"},
                        "fps_sample": {"type": "number", "default": 1.0},
                    },
                    "required": ["video_path"],
                },
            },
            {
                "name": "web_search",
                "description": "Pesquisa na web via DuckDuckGo.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query":       {"type": "string"},
                        "max_results": {"type": "integer", "default": 6},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "memory_save",
                "description": "Salva uma memória de longo prazo para um agente do swarm.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent": {"type": "string", "description": "Nome do agente"},
                        "key":   {"type": "string"},
                        "value": {"type": "string"},
                    },
                    "required": ["agent", "key", "value"],
                },
            },
            {
                "name": "memory_get",
                "description": "Recupera memórias de um agente do swarm.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent": {"type": "string"},
                        "key":   {"type": "string", "description": "Chave específica (opcional)"},
                    },
                    "required": ["agent"],
                },
            },
            {
                "name": "media_status",
                "description": "Retorna status de VRAM e modelos de geração carregados.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]
    }


def _call_tool(name: str, args: dict) -> str:
    if name == "generate_image":
        from media_engine import generate_image
        path = generate_image(**args)
        return f"Imagem gerada: {path}"

    elif name == "generate_video":
        from media_engine import generate_video
        path = generate_video(**args)
        return f"Vídeo gerado: {path}"

    elif name == "generate_videos_parallel":
        from media_engine import generate_videos_parallel
        prompts = args.pop("prompts")
        paths   = generate_videos_parallel(prompts, **args)
        return "Vídeos gerados:\n" + "\n".join(paths)

    elif name == "analyse_video":
        from skills.general.general_skills import analyse_video
        return analyse_video(
            args["video_path"],
            fps_sample=args.get("fps_sample", 1.0),
            question=args.get("question", ""),
        )

    elif name == "web_search":
        from skills.general.general_skills import web_search
        return web_search(args["query"], args.get("max_results", 6))

    elif name == "memory_save":
        from memory_system import save_memory
        save_memory(args["agent"], args["key"], args["value"])
        return f"Memória salva: [{args['key']}] = {args['value']}"

    elif name == "memory_get":
        from memory_system import get_memory, list_memories
        if "key" in args and args["key"]:
            val = get_memory(args["agent"], args["key"])
            return str(val) if val else "Não encontrada"
        entries = list_memories(args["agent"])
        return "\n".join(f"[{e['key']}] {e['value']}" for e in entries) or "Memória vazia"

    elif name == "media_status":
        from media_engine import system_status
        return system_status()

    else:
        raise ValueError(f"Tool desconhecida: {name}")


# ─── Loop MCP principal ───────────────────────────────────────────────────────
def main():
    sys.stderr.write("🔌 MCP Swarm Server iniciado (stdio)\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = req.get("method", "")
        req_id = req.get("id")
        params = req.get("params", {})

        try:
            if method == "initialize":
                _respond(req_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities":    {"tools": {}},
                    "serverInfo":      {"name": "swarm-mcp", "version": "2.0"},
                })

            elif method == "tools/list":
                _respond(req_id, _list_tools())

            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                result    = _call_tool(tool_name, tool_args)
                _respond(req_id, {
                    "content": [{"type": "text", "text": result}]
                })

            elif method == "notifications/initialized":
                pass  # no-op

            else:
                _respond(req_id, error=f"Método não suportado: {method}")

        except Exception as e:
            _respond(req_id, error=str(e))


if __name__ == "__main__":
    main()
