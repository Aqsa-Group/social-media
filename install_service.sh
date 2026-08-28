#!/bin/bash

echo "=========================================="
echo "Installing Systemd Service"
echo "=========================================="

CURRENT_DIR=$(pwd)
USER=$(whoami)

SERVICE_FILE="/etc/systemd/system/social-poster.service"

sudo cat > $SERVICE_FILE << EOF
[Unit]
Description=Social Media Auto Poster
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/run.py --mode all
Restart=always
RestartSec=30
StandardOutput=append:$CURRENT_DIR/logs/service.log
StandardError=append:$CURRENT_DIR/logs/service-error.log
SyslogIdentifier=social-poster

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created: $SERVICE_FILE"

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable social-poster

echo ""
echo "Service Commands:"
echo "  Start:   sudo systemctl start social-poster"
echo "  Stop:    sudo systemctl stop social-poster"
echo "  Restart: sudo systemctl restart social-poster"
echo "  Status:  sudo systemctl status social-poster"
echo "  Logs:    sudo journalctl -u social-poster -f"
echo ""
echo "To start now: sudo systemctl start social-poster"