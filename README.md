# Aurora

next generation of the portfolio

## Getting started

- Install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/)
- Clone the project `git clone git@github.com:martflu/aurora.git`
- cd to your project folder `cd aurora`
- start the vagrant box `vagrant up` (this will take quite a while and download a lot of data)
- ssh to it `vagrant ssh`
- you should now be in the project folder with active virtualenv: `(py3env)vagrant@vagrant-ubuntu-trusty-64:/vagrant$`
- create the database schema `python manage.py migrate`
- populate the database with some test data `python manage.py populate_demo_data`
- start the dev server `python manage.py runserver 0.0.0.0:8000`
- go to `http://localhost:8000` in your browser (find credentials in `AuroraUser/management/commands/populate_demo_data.py`)
- have fun hacking!

p.s. we use [PyCharm](https://www.jetbrains.com/pycharm/) for development. They provide free educational licences for owners of university email addresses.
