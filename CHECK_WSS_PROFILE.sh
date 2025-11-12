#!/bin/bash
# Diagnostic script to check WSS profile configuration

echo "=== Checking WSS Profile Configuration ==="
echo ""

echo "1. Profile Status:"
fs_cli -x "sofia status profile wss" | head -30
echo ""

echo "2. Checking if port 7443 is listening:"
ss -tlnp | grep 7443
echo ""

echo "3. Checking WSS XML file:"
cat /etc/freeswitch/sip_profiles/wss.xml
echo ""

echo "4. Testing TLS connection:"
timeout 3 openssl s_client -connect 136.115.41.45:7443 -brief < /dev/null 2>&1 | head -10
echo ""

echo "5. Checking for WebSocket transport in profile:"
fs_cli -x "sofia status profile wss" | grep -i "transport\|bind"
echo ""

echo "=== Diagnostic Complete ==="

