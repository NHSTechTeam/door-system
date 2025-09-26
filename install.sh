dir="/opt/NHSTechTeam/door-system"

sudo apt update && apt install -y git python3 python3-pip usbrelay xinit openbox chromium-browser
git clone https://github.com/NHSTechTeam/door-system.git $dir
cd $dir
pip install -r requirements.txt --break-system-packages
sudo chmod +x door_scanner.py
cp .env.example .env

sudo mv door-scanner.service /etc/systemd/system/door-scanner.service
sudo systemctl daemon-reload
sudo systemctl enable door-scanner.service
sudo systemctl start door-scanner.service

echo "Installation complete. Please edit the .env file with your configuration."