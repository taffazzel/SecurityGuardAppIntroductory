# SecurityGuardAppIntroductory
use the right db URL in .env
if using the MAC local db, the tunnel like this 
ssh -i ~/Downloads/LightsailDefaultKey-eu-west-2.pem   -o ExitOnForwardFailure=yes   -o ServerAliveInterval=30   -o ServerAliveCountMax=3   -N   -R 7001:127.0.0.1:8000   ubuntu@18.130.239.150
then run the app
python app.py
