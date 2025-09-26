dir="/opt/NHSTechTeam/door-system"

if [ -d "$dir" ]; then
  echo "Directory already exists. Copying .env and re installing."
  sudo cp $dir/.env /tmp/nhstt/.env
  sudo rm -rf $dir
fi

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



if [ -d "/tmp/nhstt/.env" ]; then
  sudo cp /tmp/nhstt/.env $dir/.env
  sudo rm /tmp/nhstt/.env
  echo "Reinstallation complete. Your previous .env file has been restored."
else
    echo "Installation complete. Please edit the .env file with your configuration."
fi