dir="/opt/NHSTechTeam/door-system"
tmpdir="/tmp/nhstt"

echo " -- NHS Tech Team Door System Installer --"

#move env if it exists
if [ -d "$dir" ]; then
  echo " --> Directory already exists. Copying .env and re installing."
  sudo mkdir -p $tmpdir
  sudo cp $dir/.env $tmpdir/.env
  sudo rm -rf $dir
fi

echo " --> Installing libraries and dependencies..."
sudo apt update && apt install -y git python3 python3-pip usbrelay xinit openbox firefox
git clone https://github.com/NHSTechTeam/door-system.git $dir
cd $dir
pip install -r requirements.txt --break-system-packages
sudo chmod +x door-scanner.py
cp .env.example .env

echo " --> Setting up services..."
sudo mv door-scanner.service /etc/systemd/system/door-scanner.service
sudo systemctl daemon-reload
sudo systemctl enable door-scanner
sudo systemctl start door-scanner


#auto login user on boot
echo " --> Setting up auto login on tty1"
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $(logname) --noclear %I \$TERM
EOF

#auto start gui on boot
echo " --> Creating the autostart file and setting up xinit and openbox"
sudo cp $dir/.bash_profile /home/$(logname)/.bash_profile
sudo cp $dir/.xinitrc /home/$(logname)/.xinitrc


#restore .env if it was present
if [ -f "$tmpdir/.env" ]; then
  sudo cp $tmpdir/.env $dir/.env
  sudo rm $tmpdir/.env
  echo " --> Reinstallation complete. Your previous .env file has been restored."
else
    echo " --> Installation complete. Please edit the .env file with your configuration."
fi