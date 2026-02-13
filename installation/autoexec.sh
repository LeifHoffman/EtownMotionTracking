#!/bin/bash

# Automation Startup Script for Raspberry Pi 5
# Checks for Python, Git, Apache2, and MySQL, then starts services


# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color


# # Log file location
# LOG_FILE="/var/log/website_startup.log"
# 
# # Function to log messages
# log_message() {
#     echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
# }

# Dummy log function - replace with actual logging if needed
log_message() {
    :  # No-op
}


# Function to check Python installation
check_python() {
    echo -n "Checking for Python... "
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}Found${NC} (Version: $PYTHON_VERSION)"
        log_message "Python $PYTHON_VERSION found"
        return 0
    else
        echo -e "${RED}Not Found${NC}"
        log_message "Python not found"
        return 1
    fi
}


# Function to check Git installation
check_git() {
    echo -n "Checking for Git... "
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | awk '{print $3}')
        echo -e "${GREEN}Found${NC} (Version: $GIT_VERSION)"
        log_message "Git $GIT_VERSION found"
        return 0
    else
        echo -e "${RED}Not Found${NC}"
        log_message "Git not found"
        return 1
    fi
}


# Function to check Apache2 installation
check_apache() {
    echo -n "Checking for Apache2... "
    if command -v apache2 &> /dev/null || systemctl list-unit-files | grep -q apache2.service; then
        APACHE_VERSION=$(apache2 -v 2>/dev/null | head -n1 | awk '{print $3}')
        echo -e "${GREEN}Found${NC} ($APACHE_VERSION)"
        log_message "Apache2 $APACHE_VERSION found"
        return 0
    else
        echo -e "${RED}Not Found${NC}"
        log_message "Apache2 not found"
        return 1
    fi
}


# Function to check MySQL installation
check_mysql() {
    echo -n "Checking for MySQL/MariaDB... "
    if command -v mysql &> /dev/null || systemctl list-unit-files | grep -qE 'mysql|mariadb'; then
        MYSQL_VERSION=$(mysql --version 2>/dev/null | awk '{print $5}' | sed 's/,//')
        echo -e "${GREEN}Found${NC} (Version: $MYSQL_VERSION)"
        log_message "MySQL/MariaDB $MYSQL_VERSION found"
        return 0
    else
        echo -e "${RED}Not Found${NC}"
        log_message "MySQL/MariaDB not found"
        return 1
    fi
}


# Function to start Apache2
start_apache() {
    echo -n "Starting Apache2... "
    if systemctl is-active --quiet apache2; then
        echo -e "${BLUE}Already Running${NC}"
        log_message "Apache2 already running"
        return 0
    else
        sudo systemctl start apache2
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Started${NC}"
            log_message "Apache2 started successfully"
            return 0
        else
            echo -e "${RED}Failed${NC}"
            log_message "Apache2 failed to start"
            return 1
        fi
    fi
}


# Function to start MySQL
start_mysql() {
    echo -n "Starting MySQL/MariaDB... "
    # Try both mysql and mariadb service names
    SERVICE_NAME=""
    if systemctl list-unit-files | grep -q mysql.service; then
        SERVICE_NAME="mysql"
    elif systemctl list-unit-files | grep -q mariadb.service; then
        SERVICE_NAME="mariadb"
    fi
    
    if [ -z "$SERVICE_NAME" ]; then
        echo -e "${RED}Service Not Found${NC}"
        log_message "MySQL/MariaDB service not found"
        return 1
    fi
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${BLUE}Already Running${NC}"
        log_message "$SERVICE_NAME already running"
        return 0
    else
        sudo systemctl start "$SERVICE_NAME"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Started${NC}"
            log_message "$SERVICE_NAME started successfully"
            return 0
        else
            echo -e "${RED}Failed${NC}"
            log_message "$SERVICE_NAME failed to start"
            return 1
        fi
    fi
}


# Main execution
echo "========================================="
echo "  Website Startup Check - Raspberry Pi 5"
echo "========================================="
log_message "=== Startup script initiated ==="
echo ""


PYTHON_INSTALLED=0
GIT_INSTALLED=0
APACHE_INSTALLED=0
MYSQL_INSTALLED=0


check_python && PYTHON_INSTALLED=1
check_git && GIT_INSTALLED=1
check_apache && APACHE_INSTALLED=1
check_mysql && MYSQL_INSTALLED=1


echo ""
echo "========================================="
echo "  Installation Summary"
echo "========================================="


TOTAL_FOUND=$((PYTHON_INSTALLED + GIT_INSTALLED + APACHE_INSTALLED + MYSQL_INSTALLED))
echo "Found: $TOTAL_FOUND/4 components"
echo ""


# Check if critical components are missing
MISSING_COMPONENTS=()
[ $PYTHON_INSTALLED -eq 0 ] && MISSING_COMPONENTS+=("Python")
[ $GIT_INSTALLED -eq 0 ] && MISSING_COMPONENTS+=("Git")
[ $APACHE_INSTALLED -eq 0 ] && MISSING_COMPONENTS+=("Apache2")
[ $MYSQL_INSTALLED -eq 0 ] && MISSING_COMPONENTS+=("MySQL/MariaDB")


if [ ${#MISSING_COMPONENTS[@]} -gt 0 ]; then
    echo -e "${YELLOW}[!] Missing components:${NC}"
    for component in "${MISSING_COMPONENTS[@]}"; do
        echo "    - $component"
    done
    echo ""
    log_message "Missing components: ${MISSING_COMPONENTS[*]}"
    
    # Wait for user input before exiting
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi


echo -e "${GREEN}✓ All components installed${NC}"
echo ""


# Start services
echo "========================================="
echo "  Starting Services"
echo "========================================="


start_apache
start_mysql


echo ""
echo "========================================="
echo "  Service Status"
echo "========================================="


# Display service status
if systemctl is-active --quiet apache2; then
    echo -e "Apache2:      ${GREEN}Running${NC}"
    APACHE_PORT=$(ss -tlnp 2>/dev/null | grep apache2 | grep -oP ':\K\d+' | head -1 || echo "80")
    echo "              Listening on port $APACHE_PORT"
else
    echo -e "Apache2:      ${RED}Not Running${NC}"
fi


SERVICE_NAME=""
[ -f /etc/systemd/system/mysql.service ] || [ -f /lib/systemd/system/mysql.service ] && SERVICE_NAME="mysql"
[ -f /etc/systemd/system/mariadb.service ] || [ -f /lib/systemd/system/mariadb.service ] && SERVICE_NAME="mariadb"


if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo -e "MySQL/MariaDB: ${GREEN}Running${NC}"
else
    echo -e "MySQL/MariaDB: ${RED}Not Running${NC}"
fi


echo ""
log_message "=== Startup script completed successfully ==="

# Keep script running - wait for user input
echo "========================================="
echo -e "${GREEN}Services are running!${NC}"
echo "Press Enter to exit, or Ctrl+C to stop services first..."
read -p ""
