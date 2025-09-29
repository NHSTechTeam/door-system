# ~/.bash_profile for techteam
# Start X automatically on tty1

if [[ -z $DISPLAY ]] && [[ $(tty) == /dev/tty1 ]]; then
  exec startx /bin/sh /opt/NHSTechTeam/door-system/gui.sh --
fi