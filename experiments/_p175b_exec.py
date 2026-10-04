def check_compliance(config: dict) -> str:
    # host must be a lowercase string
    host = config.get("host")
    if not isinstance(host, str) or host != host.lower():
        return "FAIL"

    # port must be an integer from 1 to 65535
    port = config.get("port")
    if not isinstance(port, int) or isinstance(port, bool) or not (1 <= port <= 65535):
        return "FAIL"

    # retries must be an integer from 1 to 5
    retries = config.get("retries")
    if not isinstance(retries, int) or isinstance(retries, bool) or not (1 <= retries <= 5):
        return "FAIL"

    # mode must be either "http" or "grpc"
    mode = config.get("mode")
    if mode not in ("http", "grpc"):
        return "FAIL"

    # tls must be an object whose enabled is a boolean and cert is a lowercase string
    tls = config.get("tls")
    if not isinstance(tls, dict):
        return "FAIL"

    enabled = tls.get("enabled")
    if not isinstance(enabled, bool):
        return "FAIL"

    cert = tls.get("cert")
    if not isinstance(cert, str) or cert != cert.lower():
        return "FAIL"

    return "PASS"

import json
config = json.loads('{"host": "db01", "port": 99999, "retries": 3, "mode": "http", "tls": {"enabled": true, "cert": "server-pem"}}')
result = check_compliance(config)
print(result)
