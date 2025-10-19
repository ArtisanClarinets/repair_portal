#!/usr/bin/env bash
set -euo pipefail

trap 'echo "[ERROR] Installation failed at line $LINENO" >&2' ERR

# Utility logger
log() {
    echo -e "\033[1;32m==>\033[0m $1"
}

restart_service() {
    local service_name="$1"
    if command -v systemctl >/dev/null 2>&1; then
        systemctl restart "$service_name"
    elif command -v service >/dev/null 2>&1; then
        service "$service_name" restart
    else
        return 1
    fi
}

reload_service() {
    local service_name="$1"
    if command -v systemctl >/dev/null 2>&1; then
        systemctl reload "$service_name"
    elif command -v service >/dev/null 2>&1; then
        service "$service_name" reload || service "$service_name" restart
    else
        return 1
    fi
}

# -----------------------------
# Configuration (override with env vars)
# -----------------------------
BENCH_USER=${BENCH_USER:-frappe}
BENCH_NAME=${BENCH_NAME:-frappe-bench}
SITE_NAME=${SITE_NAME:-erpnext.local}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-root}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin}
ADMIN_EMAIL=${ADMIN_EMAIL:-administrator@example.com}
ADMIN_FIRST_NAME=${ADMIN_FIRST_NAME:-Site}
ADMIN_LAST_NAME=${ADMIN_LAST_NAME:-Administrator}
COMPANY_NAME=${COMPANY_NAME:-Example Corp}
COMPANY_ABBR=${COMPANY_ABBR:-EX}
COMPANY_TAGLINE=${COMPANY_TAGLINE:-Example Tagline}
COMPANY_DOMAIN=${COMPANY_DOMAIN:-Manufacturing}
COMPANY_COUNTRY=${COMPANY_COUNTRY:-United States}
COMPANY_TIMEZONE=${COMPANY_TIMEZONE:-Etc/UTC}
COMPANY_CURRENCY=${COMPANY_CURRENCY:-USD}
FISCAL_YEAR_START=${FISCAL_YEAR_START:-2024-01-01}
FISCAL_YEAR_END=${FISCAL_YEAR_END:-2024-12-31}
FRAPPE_BRANCH=${FRAPPE_BRANCH:-version-15}
ERPNEXT_BRANCH=${ERPNEXT_BRANCH:-version-15}
PAYMENTS_BRANCH=${PAYMENTS_BRANCH:-version-15}
NODE_MAJOR=${NODE_MAJOR:-18}
PYTHON_BIN=${PYTHON_BIN:-/usr/bin/python3.11}

if [[ $(id -u) -ne 0 ]]; then
    echo "This script must be run as root." >&2
    exit 1
fi

if ! command -v lsb_release >/dev/null 2>&1; then
    apt update
    apt install -y lsb-release
fi

DISTRO=$(lsb_release -is)
RELEASE=$(lsb_release -rs)

if [[ "$DISTRO" != "Ubuntu" ]]; then
    echo "Unsupported distribution: $DISTRO. Only Ubuntu 22.04/24.04 are supported." >&2
    exit 1
fi

case "$RELEASE" in
    22.04|24.04) ;;
    *)
        echo "Ubuntu $RELEASE is not in the supported list (22.04, 24.04)." >&2
        exit 1
        ;;
esac

if ! id "$BENCH_USER" >/dev/null 2>&1; then
    useradd -m -s /bin/bash "$BENCH_USER"
fi

BENCH_HOME=$(eval echo "~$BENCH_USER")

ensure_python() {
    log "Ensuring Python 3.11 is available"
    if [[ ! -x "$PYTHON_BIN" ]]; then
        add-apt-repository -y ppa:deadsnakes/ppa
        apt update
        apt install -y python3.11 python3.11-dev python3.11-venv python3.11-distutils
    fi
}

install_packages() {
    log "Installing system dependencies"
    export DEBIAN_FRONTEND=noninteractive
    apt update
    apt install -y software-properties-common curl git build-essential libffi-dev \
        python3-pip redis-server xvfb libfontconfig1 libxrender1 libfreetype6 libx11-6 \
        libjpeg-turbo8 libpng16-16 liblcms2-2 libjpeg-dev zlib1g-dev libmysqlclient-dev \
        mariadb-server mariadb-client xfonts-75dpi xfonts-base nginx supervisor
    ensure_python
}

install_node() {
    log "Installing Node.js and Yarn"
    if ! command -v node >/dev/null 2>&1 || [[ $(node -v | cut -d'.' -f1 | tr -d 'v') -lt $NODE_MAJOR ]]; then
        curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash -
        apt install -y nodejs
    fi
    npm install -g yarn
}

install_wkhtmltopdf() {
    log "Installing wkhtmltopdf"
    local arch pkg
    case $(dpkg --print-architecture) in
        amd64) arch="amd64" ;;
        arm64) arch="arm64" ;;
        *)
            echo "Unsupported architecture for wkhtmltopdf" >&2
            exit 1
            ;;
    esac

    pkg="wkhtmltox_0.12.6.1-2.jammy_${arch}.deb"
    if [[ ! -f /usr/local/bin/wkhtmltopdf ]]; then
        curl -fsSL -o "$pkg" "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/${pkg}"
        apt install -y ./"$pkg" || true
        cp /usr/local/bin/wkhtmlto* /usr/bin/
        chmod a+x /usr/bin/wkhtmlto*
        rm -f "$pkg"
        apt -f install -y
    fi
}

configure_mariadb() {
    log "Configuring MariaDB"
    cat <<MYSQLCONF >/etc/mysql/conf.d/frappe.cnf
[mysql]
default-character-set = utf8mb4

[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
innodb-file-format = Barracuda
innodb-file-per-table = 1
innodb-large-prefix = 1
MYSQLCONF

    if ! restart_service mariadb >/dev/null 2>&1; then
        restart_service mysql >/dev/null 2>&1 || true
    fi

    mysql --protocol=socket -uroot <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';
FLUSH PRIVILEGES;
SQL
}

install_bench_cli() {
    log "Installing Bench CLI"
    python3 -m pip install -U pip
    python3 -m pip install -U frappe-bench
}

run_as_bench() {
    local cmd="$1"
    runuser -u "$BENCH_USER" -- bash -lc "export PATH=\"\$HOME/.local/bin:\$PATH\"; $cmd"
}

site_has_app() {
    local app="$1"
    run_as_bench "cd $BENCH_HOME/$BENCH_NAME && bench --site $SITE_NAME list-apps || true" | grep -qx "$app"
}

setup_bench() {
    log "Initialising bench: $BENCH_NAME"
    if [[ ! -d "$BENCH_HOME/$BENCH_NAME" ]]; then
        run_as_bench "bench init $BENCH_NAME --frappe-branch $FRAPPE_BRANCH --python $PYTHON_BIN --skip-assets"
    else
        log "Bench $BENCH_NAME already exists, skipping init"
    fi
}

install_apps() {
    if [[ ! -d "$BENCH_HOME/$BENCH_NAME/apps/erpnext" ]]; then
        log "Fetching ERPNext ($ERPNEXT_BRANCH)"
        local bench_cmd="cd $BENCH_HOME/$BENCH_NAME && bench get-app --branch $ERPNEXT_BRANCH erpnext https://github.com/frappe/erpnext"
        run_as_bench "$bench_cmd"
    else
        log "ERPNext already fetched, skipping"
    fi

    if [[ ! -d "$BENCH_HOME/$BENCH_NAME/apps/payments" ]]; then
        log "Fetching Payments ($PAYMENTS_BRANCH)"
        local bench_cmd="cd $BENCH_HOME/$BENCH_NAME && bench get-app --branch $PAYMENTS_BRANCH payments https://github.com/frappe/payments"
        run_as_bench "$bench_cmd"
    else
        log "Payments already fetched, skipping"
    fi
}

create_site() {
    if [[ ! -f "$BENCH_HOME/$BENCH_NAME/sites/$SITE_NAME/site_config.json" ]]; then
        log "Creating site $SITE_NAME"
        local bench_cmd="cd $BENCH_HOME/$BENCH_NAME && bench new-site $SITE_NAME --mariadb-root-password $MYSQL_ROOT_PASSWORD --admin-password $ADMIN_PASSWORD --db-name ${SITE_NAME//./_}"
        run_as_bench "$bench_cmd"
    else
        log "Site $SITE_NAME already exists, skipping creation"
    fi

    if ! site_has_app erpnext; then
        log "Installing ERPNext on $SITE_NAME"
        local bench_cmd="cd $BENCH_HOME/$BENCH_NAME && bench --site $SITE_NAME install-app erpnext"
        run_as_bench "$bench_cmd"
    else
        log "ERPNext already installed on $SITE_NAME"
    fi

    if ! site_has_app payments; then
        log "Installing Payments on $SITE_NAME"
        local bench_cmd="cd $BENCH_HOME/$BENCH_NAME && bench --site $SITE_NAME install-app payments"
        run_as_bench "$bench_cmd"
    else
        log "Payments already installed on $SITE_NAME"
    fi
}

complete_setup_wizard() {
    if grep -q 'setup_wizard_completed' "$BENCH_HOME/$BENCH_NAME/sites/$SITE_NAME/site_config.json" 2>/dev/null; then
        log "Setup wizard already completed for $SITE_NAME"
        return
    fi

    log "Completing ERPNext setup wizard"
    local payload
    payload=$(cat <<EOF
{'language': 'en', 'country': '${COMPANY_COUNTRY}', 'timezone': '${COMPANY_TIMEZONE}', 'currency': '${COMPANY_CURRENCY}',
'company_name': '${COMPANY_NAME}', 'company_abbr': '${COMPANY_ABBR}', 'company_tagline': '${COMPANY_TAGLINE}',
'domain': '${COMPANY_DOMAIN}', 'fy_start_date': '${FISCAL_YEAR_START}', 'fy_end_date': '${FISCAL_YEAR_END}',
'email': '${ADMIN_EMAIL}', 'first_name': '${ADMIN_FIRST_NAME}', 'last_name': '${ADMIN_LAST_NAME}', 'password': '${ADMIN_PASSWORD}'}
EOF
)

    local bench_cmd="cd $BENCH_HOME/$BENCH_NAME && bench --site $SITE_NAME execute erpnext.setup.install.setup_complete --args \"$payload\""
    run_as_bench "$bench_cmd"

    bench_cmd="cd $BENCH_HOME/$BENCH_NAME && bench --site $SITE_NAME enable-scheduler"
    run_as_bench "$bench_cmd"
}

setup_production() {
    log "Configuring production services"
    cd "$BENCH_HOME/$BENCH_NAME"
    HOME="$BENCH_HOME" bench setup production "$BENCH_USER" --yes
    reload_service nginx >/dev/null 2>&1 || true
}

add_hosts_entry() {
    log "Adding hosts entry for $SITE_NAME"
    if ! grep -q "$SITE_NAME" /etc/hosts; then
        echo "127.0.0.1 $SITE_NAME" >> /etc/hosts
    fi
}

install_packages
install_node
install_wkhtmltopdf
configure_mariadb
install_bench_cli
setup_bench
install_apps
create_site
complete_setup_wizard
setup_production
add_hosts_entry

echo "Installation complete!"
echo "Bench path : $BENCH_HOME/$BENCH_NAME"
echo "Site URL  : http://$SITE_NAME"
echo "Admin user: Administrator"
echo "Admin pass: $ADMIN_PASSWORD"
