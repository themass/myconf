#!/usr/bin/env python3
"""从 Xray 服务端配置里读出 VLESS+Reality 入站的客户端链接字段。

输出一行，以 TAB 分隔: uuid, port, serverName, privateKey, shortId
读不出来（文件损坏、不是 VLESS+Reality）时退出码为 1，不输出。
"""
import json
import sys


def main(path):
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return 1

    for inbound in config.get("inbounds") or []:
        if inbound.get("protocol") != "vless":
            continue
        stream = inbound.get("streamSettings") or {}
        if stream.get("security") != "reality":
            continue
        reality = stream.get("realitySettings") or {}
        clients = (inbound.get("settings") or {}).get("clients") or []
        if not clients:
            continue
        uuid = clients[0].get("id")
        port = inbound.get("port")
        server_names = reality.get("serverNames") or []
        server_name = server_names[0] if server_names else ""
        private_key = reality.get("privateKey") or ""
        short_ids = reality.get("shortIds") or []
        short_id = short_ids[0] if short_ids else ""
        if not all([uuid, port, private_key, short_id, server_name]):
            continue
        print("\t".join([uuid, str(port), server_name, private_key, short_id]))
        return 0
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
