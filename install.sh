dir="/opt/NHSTechTeam/door-system"
tmpdir="/tmp/nhstt"

#move env if it exists
if [ -d "$dir" ]; then
  echo "Directory already exists. Copying .env and re installing."
  sudo mkdir -p $tmpdir
  sudo cp $dir/.env $tmpdir/.env
  sudo rm -rf $dir
fi

sudo apt update && apt install -y git python3 python3-pip usbrelay xinit openbox chromium-browser
git clone https://github.com/NHSTechTeam/door-system.git $dir
cd $dir
pip install -r requirements.txt --break-system-packages
sudo chmod +x door-scanner.py
cp .env.example .env

sudo mv door-scanner.service /etc/systemd/system/door-scanner.service
sudo mv door-gui.service /etc/systemd/system/door-gui.service
sudo systemctl daemon-reload
sudo systemctl enable door-scanner
sudo systemctl enable door-gui
sudo systemctl start door-scanner
sudo systemctl start door-gui


#auto login user on boot
sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $(logname) --noclear %I \$TERM
EOF

#auto start gui on boot
sudo cp .bash_profile ~/.bash_profile


#restore .env if it was present
if [ -d "$tmpdir/.env" ]; then
  sudo cp $tmpdir/.env $dir/.env
  sudo rm $tmpdir/.env
  echo "Reinstallation complete. Your previous .env file has been restored."
else
    echo "Installation complete. Please edit the .env file with your configuration."
fi