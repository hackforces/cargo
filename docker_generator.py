from cement.core.foundation import CementApp
from cement.core import hook
from cement.utils.misc import init_defaults
import json
import os
import re

# Function for adding ssh-server
# Based on https://docs.docker.com/engine/examples/running_ssh_service/
# Have only 'root' user and you can set 'passowrd'
# But after using this function, please, read https://habrahabr.ru/company/infopulse/blog/237737/
def sshd_config(dockerfile, install, password):
    dockerfile.write("RUN " + install + " openssh-server"+ "\n")
    dockerfile.write("RUN mkdir /var/run/sshd"+ "\n")

    #? May be change password before sshd_config
    dockerfile.write("RUN echo 'root:%s' | chpasswd \n" % password)

    # This string replace all rules in sshd_config
    # It's setting by default only for testing
    # I recommend change this default settings in future.
    dockerfile.write("RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config"+ "\n")

    # For ssh docker will use 22th port
    dockerfile.write("EXPOSE 22\nCMD [\"/usr/sbin/sshd\", \"-D\"]"+ "\n")

def telnetd_config(dockerfile, install, password):
    dockerfile.write("RUN " + install + " telnetd"+ "\n")

    #? May be change password before telnetd_config
    dockerfile.write("RUN echo 'root:%s' | chpasswd \n" % password)
    dockerfile.write("EXPOSE 23\nCMD [\"/usr/sbin/sshd\", \"-D\"]"+ "\n")

# Function for checking of existence some package in
# repository of OS
def check_existence_in_repository(os_name, utils):
    dirlist = os.listdir(os.path.dirname(__file__))
    if os_name not in dirlist:
        return None
    # TODO: This checking works only in Unix systems
    # If file less than 3 (grabber.py , ., ..), that list of files in
    # OS's repositories doesn't downloaded yet
    directories = (os.listdir(os.path.dirname(__file__)+"/%s/" % os_name))
    if len(directories) < 3 :

        # Executing script for parsing all utils's names and versions in repositories
        os.execl("python2.7", os.path.dirname(__file__)+"/%s/grabber.py" % os_name)
        directories = (os.listdir(os.path.dirname(__file__) + "/%s/" % os_name))

    # Any directory's name corresponds of repository's version
    for file in directories:
        filepath = os.listdir(os.path.dirname(__file__) + "/" + file)
        if os.path.isdir(filepath):

            # Opening json file (packeges.json - result of grubber.py)
            with open(filepath+"/packeges.json") as datafile:
                repositorylist = json.load(datafile)
                if utils in repositorylist["name"]:
                    datafile.close()
                    return True
                datafile.close()
    return False

# Function for choice of specific utils from OS's repository
def check_existence(os_name, default):
    input_value = raw_input("You can choose default package '%s' (press Enter) or enter your own package" % default)
    while input_value:
        if check_existence_in_repository(os_name, input_value):
            return input_value
        else:
            input_value = raw_input("This package is not in repository. Please, press Enter for choice default ('%s') "
                                    "value, or enter your own package" % default)
    return default

maintainer = "MAINTAINER Stepanov Denis den-isk1995@mail.ru\n"

defaults = init_defaults('docker_generator')
defaults['docker_generator']['debug'] = False
defaults['docker_generator']['some_param'] = 'some value'

dockerfile = open("Dockerfile","w")

# define any hook functions here
def my_cleanup_hook(app):
    pass

# define the application class
class MyApp(CementApp):
    class Meta:
        label = 'docker_generator'
        config_defaults = defaults
        hooks = [
            ('pre_close', my_cleanup_hook),
        ]

with MyApp() as app:
    # add arguments to the parser
    app.args.add_argument('-o', '--os', action='store',
                          help='choice Operation System')

    app.args.add_argument('-l', '--language', action='store',
                          help='choice programming language')

    app.args.add_argument('-db', '--database', action='store',
                          help='choice DataBase')

    app.args.add_argument('-p', '--ports', action='store',
                          help='choice using ports')

    app.args.add_argument('-s', '--ssh', action='store',
                          help='make active ssh-server and set root\'s password' )

    app.args.add_argument('-t', '--telnet', action='store',
                          help='make active telnet-server and set root\'s password' )

    # TODO: Change this flag to argumentless
    app.args.add_argument('-r', '--restart', action='store',
                          help='choice container restart condition' )

    # TODO: Change this flag to argumentless
    app.args.add_argument('-v', '--volume', action='store',
                          help='choice common (shared) directory(-ies)' )

    # TODO: Change this flag to argumentless
    app.args.add_argument('-a', '--add', action='store',
                          help='choice voulume directory(-ies)' )

    # TODO: Change this flag to argumentless
    app.args.add_argument('-w', '--workdir', action='store',
                          help='choice workdir path' )
    # run the application
    app.run()

    install = "apt-get"
    operation_system = ''

    # TODO: Make checking of OS (if it exist)
    # Choice Operation System and set install
    if app.pargs.os:
        choicen_os = app.pargs.os#choise_os_version(app.pargs.os.lower())
        dockerfile.write("FROM %s\n" % choicen_os)
        app.log.info("Received option: os => %s" % choicen_os)

        if "ubuntu" in app.pargs.os.lower() or "debian" in app.pargs.os.lower():
            install = "apt-get"
        elif "arch" in app.pargs.os.lower():
            install = "pacman -S"
        elif "centos" in app.pargs.os.lower():
            install = "yum"
        else:
            print "We are cannot support this OS %s" % app.pargs.os

        # TODO: Except choice of unsupport OS. May be via WHILE
        operation_system = app.pargs.os


    dockerfile.write(maintainer)

    # Make install some language interpretator, independently from OS
    # Language pull: Rust, Go, Ruby, Python, PHP, Javascript, C, C++, Java
    # For Rust: curl https://sh.rustup.rs -sSf | sh

    # TODO: Make checking - if user entered not standart value
    if app.pargs.language:
        specify_language = 0
        language_packet = ""
        app.log.info("Received option: l => %s" % app.pargs.language.lower())
        if "ruby" in app.pargs.language.lower():
            if "ubuntu" in app.pargs.os.lower() or "debian" in app.pargs.os.lower():
                language_packet = "ruby-full"
            else:
                language_packet = "ruby"

        print "You chosen language '%s'" % app.pargs.language.lower()

        # Make a choice of version
        if "python" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "python")

        # Make a choice of version
        if "php" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "php")

        if "javascript" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "nodejs")

        if "c" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "gcc")

        if "c++" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "g++")

        # Make a choice of interpretator
        if "java" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "default-jre")

        if "rust" in app.pargs.language.lower():
            print "This is specify language, which are not in %s's repository. Default value is used" % operation_system
            dockerfile.write("RUN " + install + " curl")
            dockerfile.write("RUN " + "curl https://sh.rustup.rs -sSf | sh"+ "\n")
            specify_language = 1

        if "go" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "golang-go")

        if not specify_language:
            dockerfile.write("RUN "+install+ " " + language_packet+ "\n")

    # Make a choice of Databases
    # Pull of DBs: MySQL, PostgreSQL, MongoDB
    # TODO: Make checking - if user entered not standart value
    if app.pargs.database:
        app.log.info("Received option: db => %s" % app.pargs.database)
        database = ""

        print "You chosen database '%s'" % app.pargs.database.lower()

        # Make a choice of version
        if "mysql" in app.pargs.database.lower():
            database = check_existence(operation_system, "mysql-server")

        # PostgreSQL have a some dependencies, a like
        # 'postgresql-contrib', which provides additional functionality
        if "postgresql" in app.pargs.database.lower():
            database = check_existence(operation_system, "postgresql")

        if "mongodb" in app.pargs.database.lower():
            database = check_existence(operation_system, "mongodb-org")

        dockerfile.write("RUN " + install + " " + database+ "\n")

    # Make a choice of ports, using by Docker
    if app.pargs.ports:

        # If sequence is given
        if "," in app.pargs.ports:
            ports = re.findall(r"[, ]*(\d)[, ]*[^-]", app.pargs.ports)
            for port in ports:
                if port:
                    dockerfile.write("EXPOSE " + str(port)+ "\n")

        # If range is given
        if "-" in app.pargs.ports:
            ports = re.findall(r"(\d)-(\d)", app.pargs.ports)
            print ports, len(ports)
            i = 0
            while i < len(ports):
                for i in range(int(ports[i][0]), int(ports[i][1])+1):
                    dockerfile.write("EXPOSE " + str(i)+ "\n")
                i +=1


        app.log.info("Received option: p => %s" % app.pargs.ports)

    # Make active ssh-server and setting root's password
    if app.pargs.ssh:
        sshd_config(dockerfile, install, app.pargs.ssh)

    # Make active telnet-server and setting root's password
    if app.pargs.telnet:
        sshd_config(dockerfile, install, app.pargs.telnet)

    # List of docker restart conditions
    restart_conditions = ['on-failure', 'always', 'unless-stopped']

    # Make choice container restart condition
    if app.pargs.restart:
        if app.pargs.restart.lower() in restart_conditions:
            dockerfile.write("CMD [\"--restart\", \"%s\"]\n" % app.pargs.restart.lower())

    # Make a choice of volume directory
    if app.pargs.volume:
        choice = ''

        # Processing of directory volume choice
        while choice not in ["Q", "q"]:
            choice = raw_input("Choice next common(shared) directory (or \'Q\' for finish choice)")
            if choice in ["Q", "q"]:
                continue
            dockerfile.write("VOLUME [\"%s\"]\n" % choice)

    # Make a choice of addition files to docker image
    if app.pargs.add:
        choice_paths_from = ''

        # Processing of adding files to image
        while choice_paths_from not in ["Q", "q"]:
            choice_paths_from = raw_input("Choice next file (or \'Q\' for finish choice)")
            choice_paths_to = raw_input("Choice destination directory")
            if choice_paths_from in ["Q", "q"]:
                continue

            if choice_paths_from == '' or choice_paths_to == '':
                print "Wrong parametrs"
                continue

            choice = ''
            while choice not in ["Y", "y", "N", "n"]:
                choice = raw_input("This file on your local machine? [Y/N]")
                if choice in ["Y", "y"]:
                    dockerfile.write("COPY \"%s\" \"%s\"\n" % choice_paths_from, choice_paths_to)
                elif choice in ["N", "n"]:
                    dockerfile.write("ADD \"%s\" \"%s\"\n" % choice_paths_from, choice_paths_to)

    if app.pargs.workdir:
        dockerfile.write("WORKDIR %s\n" % app.pargs.workdir)


    dockerfile.close()