def check_compliance(config: dict) -> str:
    # Validate host: lowercase string
    host = config.get("host")
    if not isinstance(host, str) or not host.islower():
        return "FAIL"
    
    # Validate port: integer between 1 and 65535 inclusive
    port = config.get("port")
    if not isinstance(port, int) or isinstance(port, bool) or not (1 <= port <= 65535):
        return "FAIL"
    
    # Validate retries: integer between 1 and 5 inclusive
    retries = config.get("retries")
    if not isinstance(retries, int) or isinstance(retries, bool) or not (1 <= retries <= 5):
        return "FAIL"
    
    # Validate mode: allowed enum values "http" or "grpc"
    mode = config.get("mode")
    if mode not in ("http", "grpc"):
        return "FAIL"
    
    # Validate tls object: contains boolean enabled and lowercase string cert
    tls = config.get("tls")
    if not isinstance(tls, dict):
        return "FAIL"
    enabled = tls.get("enabled")
    if not isinstance(enabled, bool):
        return "FAIL"
    cert = tls.get("cert")
    if not isinstance(cert, str) or not cert.islower():
        return "FAIL"
    
    return "PASS"

import json
config = json.loads('{"host": "db01", "port": 99999, "retries": 3, "mode": "http", "tls": {"enabled": true, "cert": "server-pem"}}')
result = check_compliance(config)
print(result)
