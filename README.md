installing
==========

  local$ pip install ansible==1.8.1
  local$ git clone http://github.com/segue-org/segue
  local$ cd segue
  local$ vagrant up
  local$ vagrant ssh

  vagrant> source /home/vagrant/.venv/segue/bin/activate
  vagrant> cd /opt/segue
  vagrant> nosetests .

At this point, the API should be up and running at http://192.168.33.91/api. A good health
check is to hit /api/proposal/tracks.

contributing
============

Fill free to report issues and submit pull requests. We prefer
pull requests that are covered by unit tests if possible.

If you figure out a security issue, feel free to report it to
the maintainers (@fmobus, @dwolff) right away.
