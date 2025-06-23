#!/usr/bin/env bash
###############################################################################
#  ERPNext v15  +  repair_portal   –   Codex container bootstrap (Ubuntu 24.04)
###############################################################################
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# ───────── config ─────────
WORKSPACE="/workspace"
BENCH_DIR="${WORKSPACE}/frappe-bench"

SITE_NAME="erp.artisanclarinets.com"
ADMIN_PASS="admin"
MYSQL_ROOT_PASS="root"

FRAPPE_BRANCH="version-15"
ERP_BRANCH="version-15"
REPAIR_PORTAL_GIT="https://github.com/ArtisanClarinets/repair_portal.git"

NODE_VER=18
YARN_VER=1.22.19
# ─────────────────────────

[[ $EUID -ne 0 ]] && { echo "Run this script as root (or with sudo)"; exit 1; }

###############################################################################
# 1. Base packages
###############################################################################
echo -e "\n── Installing system packages ───────────────────────────────"
apt-get update -qq
apt-get install -yqq apt-utils
apt-get install -yqq \
    git curl wget ca-certificates software-properties-common \
    mariadb-server redis-server supervisor nginx cron \
    build-essential libffi-dev libssl-dev \
    python3 python3-dev python3-venv python3-pip pipx \
    wkhtmltopdf >/dev/null

service supervisor   start >/dev/null
service redis-server start  >/dev/null     # avoids redis WARN spam later

###############################################################################
# 2. Node 18  +  classic Yarn 1
###############################################################################
echo -e "\n── Node ${NODE_VER} + classic Yarn ${YARN_VER} ───────────────"
curl -fsSL "https://deb.nodesource.com/setup_${NODE_VER}.x" | bash - >/dev/null
apt-get install -yqq nodejs >/dev/null
corepack disable >/dev/null 2>&1 || true
npm config set prefix /usr/local
npm install -g "yarn@${YARN_VER}" --unsafe-perm --force >/dev/null

# --- Codex sandbox fix: use npmjs registry + generous timeout -------------
yarn config set registry        "https://registry.npmjs.org"  -g
yarn config set network-timeout 300000                        -g
# -------------------------------------------------------------------------

echo "   • yarn $(yarn --version) at $(command -v yarn)"

###############################################################################
# 3. MariaDB – quick dev hardening
###############################################################################
echo -e "\n── Securing MariaDB ──────────────────────────────────────────"
service mariadb start
mysql -u root <<SQL
CREATE OR REPLACE USER 'admin'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASS}';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SQL

###############################################################################
# 4. Unix account  *frappe*
###############################################################################
echo -e "\n── Creating UNIX user *frappe* ───────────────────────────────"
id -u frappe &>/dev/null || adduser --disabled-password --gecos "" --home "$WORKSPACE" frappe
usermod -aG sudo frappe
echo "frappe ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/frappe
chmod 0440 /etc/sudoers.d/frappe
chown -R frappe:frappe "$WORKSPACE"

###############################################################################
# 5. Bench CLI via pipx
###############################################################################
echo -e "\n── Installing Bench CLI (pipx) ───────────────────────────────"
sudo -H -u frappe pipx install --include-deps frappe-bench >/dev/null

###############################################################################
# 6. Initialise bench & apps  (runs as *frappe*)
###############################################################################
export PATH="/usr/local/bin:$PATH"
export SITE_NAME ADMIN_PASS MYSQL_ROOT_PASS BENCH_DIR \
       FRAPPE_BRANCH ERP_BRANCH REPAIR_PORTAL_GIT WORKSPACE

sudo -E -H -u frappe bash <<'EOF'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

echo "   › yarn  -> \$(yarn --version)"
echo "   › bench -> \$(command -v bench)"

rm -rf "\$BENCH_DIR"

bench init --frappe-branch "\$FRAPPE_BRANCH" "\$BENCH_DIR" --skip-assets
cd "\$BENCH_DIR"

# fetch applications
bench get-app erpnext       --branch "\$ERP_BRANCH"
bench get-app repair_portal "\$REPAIR_PORTAL_GIT"

# create site
bench new-site "\$SITE_NAME" \
      --db-root-username admin \
      --db-root-password "\$MYSQL_ROOT_PASS" \
      --admin-password   "\$ADMIN_PASS"

# install apps
bench --site "\$SITE_NAME" install-app erpnext
bench --site "\$SITE_NAME" install-app repair_portal

# python & node deps
bench setup requirements

# ───── bench build can exit ≠ 0 for benign reasons – don't kill bootstrap
if ! bench build; then
    echo "bench build returned non-zero status – continuing anyway"
fi
EOF

echo -e "\n✅  Bootstrap complete – ERPNext + repair_portal ready"
exit 0
