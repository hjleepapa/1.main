# Check FusionPBX Configuration

The database has the correct values, but FreeSWITCH isn't reading them. FusionPBX might be caching or regenerating the config from elsewhere.

## Step 1: Find where the variables are defined

```bash
# Check FusionPBX config directory
ls -la /etc/fusionpbx/config.php
cat /etc/fusionpbx/config.php | grep -i "external.*ip"

# Check FreeSWITCH vars.xml
cat /etc/freeswitch/vars.xml | grep -i "external"
cat /etc/freeswitch/vars.xml | grep -i "ip"

# Check for FusionPBX specific config
find /etc/fusionpbx -name "*.xml" -o -name "*.conf" | xargs grep -i "external.*ip" 2>/dev/null

# Check autoload_configs
grep -r "external_sip_ip\|external_rtp_ip" /etc/freeswitch/autoload_configs/

# Check actual XML files being used
find /var/lib/freeswitch -name "*.xml" 2>/dev/null | grep sip
```

## Step 2: Check if FusionPBX regenerates XML

FusionPBX might be regenerating the XML on every reload. Look for where the SIP profile XML is actually generated:

```bash
# Watch the XML file while reloading
tail -f /etc/freeswitch/sip_profiles/external.xml &
TAIL_PID=$!

fs_cli -x "reloadxml"

kill $TAIL_PID

# Check if the file was modified
stat /etc/freeswitch/sip_profiles/external.xml
```

## Step 3: Force reload from database

FusionPBX might need to be told to rewrite the XML from the database:

```bash
# Check if there's a FusionPBX CLI command
fwconsole reload

# Or via web API (if you have credentials)
curl -u admin:PASSWORD https://136.113.215.142/app/xml_cdr/xml_cdr_sql.php

# Or check PHP scripts that generate config
find /var/www/fusionpbx -name "*.php" | xargs grep -l "sofia.*xml\|sip_profiles" | head -5
```

## Step 4: Check actual variable values in FreeSWITCH

```bash
# Check what FreeSWITCH actually sees for these variables
fs_cli -x "eval \${external_sip_ip}"
fs_cli -x "eval \${external_rtp_ip}"
fs_cli -x "eval \${local_ip_v4}"

# Check all environment variables
fs_cli -x "eval \${sofia_contact_external/internal}"
```

## Step 5: Find the actual XML being used

FreeSWITCH might be loading from a different location:

```bash
# Check where actual profile is loaded from
fs_cli -x "sofia status profile external"

# Check what XML FreeSWITCH parsed
fs_cli -x "sofia profile external xmlstatus"

# Find the actual file being read
strace -p $(pgrep freeswitch) 2>&1 | grep external.xml
```

## Step 6: Nuclear Option - Manual XML Override

If FusionPBX keeps overwriting, create a custom include:

```bash
# Create a custom settings file that loads AFTER FusionPBX rewrites
cat > /etc/freeswitch/sip_profiles/external-override.xml << 'EOF'
<profile name="external">
  <settings>
    <param name="ext-sip-ip" value="136.113.215.142"/>
    <param name="ext-rtp-ip" value="136.113.215.142"/>
  </settings>
</profile>
EOF

# Edit sofia.conf.xml to include your override AFTER default includes
# Make sure your include comes last so it overrides
```

## Step 7: Use FusionPBX GUI (Most Reliable)

Sometimes the GUI is the ONLY way that works:

1. Login: `https://136.113.215.142`
2. Advanced → SIP Profiles → external
3. Click "Edit Settings" for the external profile
4. Find "External SIP IP" and "External RTP IP" fields
5. Set both to: `136.113.215.142`
6. Save
7. Status → SIP Status → Reload XML → Restart

The GUI update might trigger FusionPBX to properly regenerate the XML.

