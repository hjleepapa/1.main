# Check Database Commands for FusionPBX

Run these commands on your FusionPBX server to find the database:

```bash
# Check for MariaDB
which mariadb
which mysql
/usr/bin/mariadb --version
/usr/bin/mysql --version

# Check for PostgreSQL
which psql
/usr/bin/psql --version

# Check for SQLite
which sqlite3
/usr/bin/sqlite3 --version

# Check running database processes
ps aux | grep -i "mysql\|postgres\|sqlite"

# Check installed database packages
dpkg -l | grep -i "mysql\|postgres\|sqlite\|mariadb"

# Check if FusionPBX is using ODBC
cat /etc/freeswitch/autoload_configs/odbc.conf.xml

# Check FusionPBX config for database connection
find /etc/fusionpbx -name "*.php" -o -name "*.xml" | xargs grep -i "database\|db_host\|db_name" | head -20
```

