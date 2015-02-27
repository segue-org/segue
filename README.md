installing
==========

  local$ pip install ansible==1.8.1
  local$ git clone http://github.com/segue-org/segue
  local$ cd segue
  local$ vagrant up

In case the provisioner fails with a weird ssh message, just try again
with. There seems to be a weird timing issue with ansible and vagrant
on the first try.

  local$ vagrant provision

  local$ vagrant ssh

  vagrant> source /home/vagrant/.venv/segue/bin/activate
  vagrant> cd /opt/segue
  vagrant> nosetests .
  vagrant> python manage.py db upgrade
  vagrant> python manage.py populate_reference_data

At this point, the API should be up and running at http://192.168.33.91/api.
A good health check is to hit /api/proposal/tracks.

contributing
============

Feel free to report issues and submit pull requests. We prefer
pull requests that are covered by unit tests if possible. Any changes
to model (new columns, new tables, etc) should be acommpanied by an
alembic migration.

If you figure out a security issue, kindly report it to the maintainers
(@fmobus, @dwolff) right away.
