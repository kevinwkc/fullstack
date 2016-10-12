
README
=======================================
1 - start the virtual machine by typing `vagrant up`.

2 - log into the VM using the following command `vagrant ssh`.

2a - cd /vagrant/tournament

3 - import the database schema using `psql` application:
    - `psql``
    - \i tournament.sql
    - \q

4 - execute the tests module by invoking the python script: `python tournament_test.py`

5 - enjoy! :)