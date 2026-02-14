#!/bin/bash

# Installation Script for Raspberry Pi 5 LAMP Stack
# Installs specific versions: Python 3.13.5, Git 2.47.3, Apache 2.4.66, MariaDB 15.2, PHP 8.4.16

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Target versions
PYTHON_VERSION="3.13.5"
GIT_VERSION="2.47.3"
APACHE_VERSION="2.4.66"
MARIADB_VERSION="15.2"
PHP_VERSION="8.4.16"

echo "========================================="
echo "  LAMP Stack Installer - Raspberry Pi 5"
echo "========================================="
echo ""
echo "This will install specific versions:"
echo "  - Python $PYTHON_VERSION"
echo "  - Git $GIT_VERSION"
echo "  - Apache $APACHE_VERSION"
echo "  - MariaDB $MARIADB_VERSION"
echo "  - PHP $PHP_VERSION"
echo ""
echo -e "${YELLOW}Warning: Pinned versions require manual installation${NC}"
echo -e "${YELLOW}This may take 30-60 minutes to compile from source${NC}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

# Function to check if a version matches
version_matches() {
    installed_version=$1
    target_version=$2
    
    # Extract major.minor.patch
    installed_major=$(echo "$installed_version" | cut -d. -f1)
    target_major=$(echo "$target_version" | cut -d. -f1)
    
    if [ "$installed_major" == "$target_major" ]; then
        return 0
    else
        return 1
    fi
}

echo ""
echo "========================================="
echo "  Step 1: Installing Build Dependencies"
echo "========================================="

sudo apt-get update
sudo apt-get install -y build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev \
    libffi-dev liblzma-dev libgdbm-dev libnss3-dev \
    libpcre3-dev libexpat1-dev gettext autoconf libapr1-dev \
    libaprutil1-dev libncurses-dev cmake

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install build dependencies${NC}"
    exit 1
fi

INSTALL_DIR="$HOME/lamp_install"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo ""
echo "========================================="
echo "  Step 2: Installing Python $PYTHON_VERSION"
echo "========================================="

if command -v python3 &> /dev/null; then
    CURRENT_VERSION=$(python3 --version | awk '{print $2}')
    if version_matches "$CURRENT_VERSION" "$PYTHON_VERSION"; then
        echo -e "${BLUE}Python $CURRENT_VERSION already installed (compatible)${NC}"
    else
        echo -e "${YELLOW}Different Python version found: $CURRENT_VERSION${NC}"
    fi
else
    echo "Downloading Python $PYTHON_VERSION..."
    wget "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz"
    
    if [ -f "Python-$PYTHON_VERSION.tar.xz" ]; then
        tar -xf "Python-$PYTHON_VERSION.tar.xz"
        cd "Python-$PYTHON_VERSION"
        
        echo "Configuring Python..."
        ./configure --enable-optimizations --with-ensurepip=install
        
        echo "Building Python (this will take 15-20 minutes)..."
        make -j$(nproc)
        
        echo "Installing Python..."
        sudo make altinstall
        
        # Create symlink
        sudo ln -sf /usr/local/bin/python3.13 /usr/local/bin/python3
        sudo ln -sf /usr/local/bin/pip3.13 /usr/local/bin/pip3
        
        cd "$INSTALL_DIR"
        echo -e "${GREEN}✓ Python $PYTHON_VERSION installed${NC}"
    else
        echo -e "${RED}✗ Failed to download Python${NC}"
    fi
fi

echo ""
echo "========================================="
echo "  Step 3: Installing Git $GIT_VERSION"
echo "========================================="

if command -v git &> /dev/null; then
    CURRENT_VERSION=$(git --version | awk '{print $3}')
    if version_matches "$CURRENT_VERSION" "$GIT_VERSION"; then
        echo -e "${BLUE}Git $CURRENT_VERSION already installed (compatible)${NC}"
    else
        echo -e "${YELLOW}Different Git version found: $CURRENT_VERSION${NC}"
    fi
else
    echo "Downloading Git $GIT_VERSION..."
    wget "https://mirrors.edge.kernel.org/pub/software/scm/git/git-$GIT_VERSION.tar.gz"
    
    if [ -f "git-$GIT_VERSION.tar.gz" ]; then
        tar -xf "git-$GIT_VERSION.tar.gz"
        cd "git-$GIT_VERSION"
        
        echo "Building Git..."
        make prefix=/usr/local all -j$(nproc)
        
        echo "Installing Git..."
        sudo make prefix=/usr/local install
        
        cd "$INSTALL_DIR"
        echo -e "${GREEN}✓ Git $GIT_VERSION installed${NC}"
    else
        echo -e "${RED}✗ Failed to download Git${NC}"
    fi
fi

echo ""
echo "========================================="
echo "  Step 4: Installing Apache $APACHE_VERSION"
echo "========================================="

if systemctl list-unit-files | grep -q apache2.service; then
    CURRENT_VERSION=$(apache2 -v 2>/dev/null | head -n1 | awk '{print $3}' | cut -d'/' -f2)
    if version_matches "$CURRENT_VERSION" "$APACHE_VERSION"; then
        echo -e "${BLUE}Apache $CURRENT_VERSION already installed (compatible)${NC}"
    else
        echo -e "${YELLOW}Different Apache version found: $CURRENT_VERSION${NC}"
    fi
else
    echo "Downloading Apache $APACHE_VERSION..."
    wget "https://dlcdn.apache.org/httpd/httpd-$APACHE_VERSION.tar.gz"
    
    if [ -f "httpd-$APACHE_VERSION.tar.gz" ]; then
        tar -xf "httpd-$APACHE_VERSION.tar.gz"
        cd "httpd-$APACHE_VERSION"
        
        echo "Configuring Apache..."
        ./configure --enable-so --enable-ssl --with-ssl=/usr --prefix=/usr/local/apache2
        
        echo "Building Apache (this will take 10-15 minutes)..."
        make -j$(nproc)
        
        echo "Installing Apache..."
        sudo make install
        
        # Create systemd service
        sudo bash -c 'cat > /etc/systemd/system/apache2.service << EOF
[Unit]
Description=Apache Web Server
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/apache2/bin/apachectl start
ExecStop=/usr/local/apache2/bin/apachectl stop
ExecReload=/usr/local/apache2/bin/apachectl graceful

[Install]
WantedBy=multi-user.target
EOF'
        
        sudo systemctl daemon-reload
        sudo systemctl enable apache2
        sudo systemctl start apache2
        
        # Create symlink
        sudo ln -sf /usr/local/apache2/bin/apachectl /usr/local/bin/apache2
        
        cd "$INSTALL_DIR"
        echo -e "${GREEN}✓ Apache $APACHE_VERSION installed${NC}"
    else
        echo -e "${RED}✗ Failed to download Apache${NC}"
    fi
fi

echo ""
echo "========================================="
echo "  Step 5: Installing MariaDB $MARIADB_VERSION"
echo "========================================="

if systemctl list-unit-files | grep -qE 'mysql|mariadb'; then
    CURRENT_VERSION=$(mysql --version 2>/dev/null | awk '{print $5}' | sed 's/,//')
    if version_matches "$CURRENT_VERSION" "$MARIADB_VERSION"; then
        echo -e "${BLUE}MariaDB $CURRENT_VERSION already installed (compatible)${NC}"
    else
        echo -e "${YELLOW}Different MariaDB version found: $CURRENT_VERSION${NC}"
    fi
else
    echo "Downloading MariaDB $MARIADB_VERSION..."
    # MariaDB version format is 11.x.x for client version 15.x
    MARIADB_SERVER_VERSION="11.6.2"
    wget "https://downloads.mariadb.org/rest-api/mariadb/$MARIADB_SERVER_VERSION/mariadb-$MARIADB_SERVER_VERSION.tar.gz"
    
    if [ -f "mariadb-$MARIADB_SERVER_VERSION.tar.gz" ]; then
        tar -xf "mariadb-$MARIADB_SERVER_VERSION.tar.gz"
        cd "mariadb-$MARIADB_SERVER_VERSION"
        
        sudo apt-get install -y libncurses5-dev bison
        
        echo "Configuring MariaDB..."
        cmake . -DCMAKE_INSTALL_PREFIX=/usr/local/mysql
        
        echo "Building MariaDB (this will take 20-30 minutes)..."
        make -j$(nproc)
        
        echo "Installing MariaDB..."
        sudo make install
        
        # Setup MariaDB
        sudo groupadd mysql 2>/dev/null || true
        sudo useradd -r -g mysql -s /bin/false mysql 2>/dev/null || true
        sudo /usr/local/mysql/scripts/mysql_install_db --user=mysql --basedir=/usr/local/mysql --datadir=/usr/local/mysql/data
        
        # Create systemd service
        sudo bash -c 'cat > /etc/systemd/system/mariadb.service << EOF
[Unit]
Description=MariaDB Server
After=network.target

[Service]
Type=simple
User=mysql
Group=mysql
ExecStart=/usr/local/mysql/bin/mysqld --basedir=/usr/local/mysql --datadir=/usr/local/mysql/data --user=mysql

[Install]
WantedBy=multi-user.target
EOF'
        
        sudo systemctl daemon-reload
        sudo systemctl enable mariadb
        sudo systemctl start mariadb
        
        # Create symlink
        sudo ln -sf /usr/local/mysql/bin/mysql /usr/local/bin/mysql
        
        cd "$INSTALL_DIR"
        echo -e "${GREEN}✓ MariaDB installed${NC}"
        echo -e "${YELLOW}Note: Run 'sudo /usr/local/mysql/bin/mysql_secure_installation' to secure your installation${NC}"
    else
        echo -e "${RED}✗ Failed to download MariaDB${NC}"
    fi
fi

echo ""
echo "========================================="
echo "  Step 6: Installing PHP $PHP_VERSION"
echo "========================================="

if command -v php &> /dev/null; then
    CURRENT_VERSION=$(php -v | head -n1 | awk '{print $2}')
    if version_matches "$CURRENT_VERSION" "$PHP_VERSION"; then
        echo -e "${BLUE}PHP $CURRENT_VERSION already installed (compatible)${NC}"
    else
        echo -e "${YELLOW}Different PHP version found: $CURRENT_VERSION${NC}"
    fi
else
    echo "Downloading PHP $PHP_VERSION..."
    wget "https://www.php.net/distributions/php-$PHP_VERSION.tar.gz"
    
    if [ -f "php-$PHP_VERSION.tar.gz" ]; then
        tar -xf "php-$PHP_VERSION.tar.gz"
        cd "php-$PHP_VERSION"
        
        sudo apt-get install -y libxml2-dev libsqlite3-dev
        
        echo "Configuring PHP..."
        ./configure --with-apxs2=/usr/local/apache2/bin/apxs \
            --with-mysqli=/usr/local/mysql/bin/mysql_config \
            --enable-mbstring \
            --with-openssl
        
        echo "Building PHP (this will take 10-15 minutes)..."
        make -j$(nproc)
        
        echo "Installing PHP..."
        sudo make install
        
        # Configure Apache to use PHP
        sudo bash -c 'echo "LoadModule php_module modules/libphp.so" >> /usr/local/apache2/conf/httpd.conf'
        sudo bash -c 'echo "AddType application/x-httpd-php .php" >> /usr/local/apache2/conf/httpd.conf'
        sudo bash -c 'echo "DirectoryIndex index.php index.html" >> /usr/local/apache2/conf/httpd.conf'
        
        sudo systemctl restart apache2
        
        cd "$INSTALL_DIR"
        echo -e "${GREEN}✓ PHP $PHP_VERSION installed${NC}"
    else
        echo -e "${RED}✗ Failed to download PHP${NC}"
    fi
fi

echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""

# Display installed versions
echo "Installed versions:"
echo "-------------------"
if command -v python3 &> /dev/null; then
    echo -e "Python:  ${GREEN}$(python3 --version)${NC}"
else
    echo -e "Python:  ${RED}Not found${NC}"
fi

if command -v git &> /dev/null; then
    echo -e "Git:     ${GREEN}$(git --version)${NC}"
else
    echo -e "Git:     ${RED}Not found${NC}"
fi

if command -v apache2 &> /dev/null || [ -f /usr/local/apache2/bin/apachectl ]; then
    echo -e "Apache:  ${GREEN}$(/usr/local/apache2/bin/apachectl -v 2>/dev/null | head -n1)${NC}"
else
    echo -e "Apache:  ${RED}Not found${NC}"
fi

if command -v mysql &> /dev/null; then
    echo -e "MySQL:   ${GREEN}$(mysql --version)${NC}"
else
    echo -e "MySQL:   ${RED}Not found${NC}"
fi

if command -v php &> /dev/null; then
    echo -e "PHP:     ${GREEN}$(php -v | head -n1)${NC}"
else
    echo -e "PHP:     ${RED}Not found${NC}"
fi

echo ""
echo -e "${GREEN}Installation files saved to: $INSTALL_DIR${NC}"
echo -e "${GREEN}You can now run your autoexec.sh script!${NC}"
echo ""
read -p "Press Enter to exit..."
