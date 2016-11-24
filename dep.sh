rem=$(git ls-remote git://github.com/melanholy/WEB-PAGE-BABYYYYYYYY.git HEAD | egrep -o '[a-z0-9]+')
loc=$(git rev-parse HEAD)

if [ "$rem" != "$loc" ]; then
    git pull
    sudo uwsgi --reload /tmp/wsgimaker.pid
fi
echo 'up to date'
