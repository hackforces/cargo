from cement.core.foundation import CementApp
from cement.utils.misc import init_defaults
import json
import os
import re

# This variable for forming Dockerfile before writing it to real file
dockerstrings = []

# Function for adding ssh-server
# Based on https://docs.docker.com/engine/examples/running_ssh_service/
# Have only 'root' user and you can set 'passowrd'
# But after using this function, please, read https://habrahabr.ru/company/infopulse/blog/237737/
def sshd_config(install, password):
    dockerstrings.append("RUN {} openssh-server\n".format(install))
    dockerstrings.append("RUN mkdir /var/run/sshd\n")

    # TODO: May be change password before sshd_config
    dockerstrings.append("RUN echo 'root:{}' | chpasswd\n".format(password))

    # This string replace all rules in sshd_config
    # It's setting by default only for testing
    # I recommend change this default settings in future.
    dockerstrings.append("RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config\n")

    # For ssh docker will use 22th port
    dockerstrings.append("EXPOSE 22\nCMD [\"/usr/sbin/sshd\", \"-D\"]\n")

def telnetd_config(install, password):
    dockerstrings.append("RUN {} telnetd\n".format(install))

    # TODO: May be change password before telnetd_config
    dockerstrings.append("RUN echo 'root:{}' | chpasswd\n".format(password))
    dockerstrings.append("EXPOSE 23\nCMD [\"/usr/sbin/sshd\", \"-D\"]\n")

# Function for checking of existence some package in
# repository of OS
def check_existence_in_repository(os_name, utils):

    if os_name not in os.listdir(os.path.dirname(__file__) + "/os/"):
        return None
    # TODO: This checking works only in Unix systems
    # If file less than 3 (grabber.py , ., ..), that list of files in
    # OS's repositories doesn't downloaded yet
    path = os.path.dirname(__file__) + "/os/{}/".format(os_name)
    if len(os.listdir(path)) < 2:

        # Executing script for parsing all utils's names and versions in repositories
        os.execl("python", path + "grabber.py")

    # Any directory's name corresponds of repository's version
    for file in os.listdir(path):

        filepath = path + file
        if os.path.isdir(filepath):
            # Opening json file (packages.json - result of grabber.py)
            with open(filepath + "/packages.json") as datafile:
                repositorylist = json.load(datafile)
                for item in enumerate(repositorylist):
                    if utils in item[1]["name"]:
                        datafile.close()
                        return True
                    datafile.close()
    return False

# This functions for external file adding unification (requests.txt, DB, composer.json, etc.)
def add_external_file():
    answer = ''
    local_machine = 1
    while answer.lower() not in "ny":
        answer = input("This file on local machine? [Y/N]: ")

    if answer.lower() is "n":
        local_machine = 0

    answer = ''
    while not answer and len(answer) != 2:
        answer = input("Please, enter path (or link) of your file and destination path in your Docker: ")

    if local_machine:
        dockerstrings.append("COPY {} {}\n".format(answer[0], answer[1]))
    else:
        dockerstrings.append("ADD {} {}\n".format(answer[0], answer[1]))

    return answer

# This function for interactive mode. It allows to expand
# program functions for more detail settings
def language_interactive(os_installer, language):
    files = []

    answer = ''
    while answer.lower() not in "ny":
        answer = input("This file on local machine? [Y/N]: ")

    if answer.lower() is "n":
        return 0
    else:
        files = add_external_file()

    if 'python' in language.lower():
        dockerstrings.append("RUN {} python-pip\n".format(os_installer))
        dockerstrings.append("RUN p=pwn && cd {}".format(os.path.dirname(files[1])))
        if "3" in language:
            dockerstrings.append(" && pip3 install -r ./requests.txt ")
        else:
            dockerstrings.append(" && pip install -r ./requests.txt ")

        dockerstrings.append("&& cd $p\n")

    if 'php' in language.lower():
        dockerstrings.append("RUN curl -sS https://getcomposer.org/installer | sudo {} --install-dir=/usr/local/bin --filename=composer\n".format(language))
        # As php's composer make install all references from composer.json in current directory
        # we need to enter to this directory and return come back
        dockerstrings.append("RUN p=pwn && cd {} && composer install && cd $p\n".format(os.path.dirname(files[1])))

    if 'node' in language.lower():
        dockerstrings.append("RUN {} npm\n".format(os_installer))
        # As nodejs's npm make install all references from package.json in current directory
        # we need to enter to this directory and return come back
        dockerstrings.append("RUN p=pwn && cd {} && npm install && cd $p\n".format(os.path.dirname(files[1])))

def database_interactive(database):
    answer = ''
    while answer.lower() not in "yn":
        answer = input("This file on local machine? [Y/N]: ")

    if answer.lower() is "n":
        return 0
    else:
        files = add_external_file()

    username = input("Please, enter username: ")
    password = input("Please, enter password: ")
    database_name = input("Please, enter database name: ")

    # https://stackoverflow.com/questions/25920029/setting-up-mysql-and-importing-dump-within-dockerfile
    # https://stackoverflow.com/questions/4546778/how-can-i-import-a-database-with-mysql-from-terminal
    if "mysql" in database.lower():
        dockerstrings.append("RUN /bin/bash -c \"/usr/bin/mysqld_safe &\" && \
                            sleep 5 && \
                            mysql -u {} -e \"CREATE DATABASE {}\" && \
                            mysql -u {} -p {} {} < {}\n".format(username, database_name,
                            username, password, database_name, files[1]))

    if "postgresql" in database.lower():
        dockerstrings.append("RUN psql -U {} {} < {}\n".format(username, database_name, files[1]))

    # https://docs.mongodb.com/manual/tutorial/backup-and-restore-tools/
    if "mongodb" in database.lower():
        dockerstrings.append("RUN mongorestore {}".format(files[1]))



# Function for choice of specific utils from OS's repository
def check_existence(os_name, default):
    input_value = input("You can choose default package '{}' (press Enter) or enter your own package: ".format(default))
    while input_value:
        if check_existence_in_repository(os_name, input_value):
            return input_value
        else:
            input_value = input("This package is not in repository. Please, press Enter to choose default ('{}'): "
                                    "value, or enter your own package".format(default))
    return default

maintainer = "MAINTAINER Stepanov Denis den-isk1995@mail.ru\n"

defaults = init_defaults('docker_generator')
defaults['docker_generator']['debug'] = False
defaults['docker_generator']['some_param'] = 'some value'

# define any hook functions here
def my_cleanup_hook(app):
    pass

# define the application class
class Cargo(CementApp):
    class Meta:
        label = 'docker_generator'
        config_defaults = defaults
        hooks = [
            ('pre_close', my_cleanup_hook),
        ]
        languages = ['python', 'go', 'php', 'js', 'c', 'c++', 'java', 'ruby', 'rust']
        restart = ['on-failure', 'always', 'unless-stopped']
with Cargo() as app:
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

    app.args.add_argument('-r', '--restart', action='store',
                          help='choice container restart condition' )

    app.args.add_argument('-v', '--volume', action='store_true',
                          help='choice common (shared) directory(-ies)' )

    app.args.add_argument('-a', '--add', action='store_true',
                          help='choice voulume directory(-ies)' )

    app.args.add_argument('-w', '--workdir', action='store_true',
                          help='choice workdir path' )
    # run the application
    app.run()

    install = "apt-get"
    operation_system = ''

    # TODO: Make checking of OS (if it exist)
    # Choice Operation System and set install
    if app.pargs.os:
        choicen_os = app.pargs.os#choise_os_version(app.pargs.os.lower())
        dockerstrings.append("FROM {}\n".format(choicen_os))
        app.log.info("Received option: os => {}".format(choicen_os))

        if "ubuntu" in app.pargs.os.lower() or "debian" in app.pargs.os.lower():
            install = "apt-get -qq -y install"
        elif "arch" in app.pargs.os.lower():
            install = "pacman -S install"
        elif "centos" in app.pargs.os.lower():
            install = "yum install"
        else:
            print("We are cannot support this OS: {}".format(app.pargs.os))

        # TODO: Except choice of unsupport OS. May be via WHILE
        operation_system = app.pargs.os


    dockerstrings.append(maintainer)

    # Make install some language interpretator, independently from OS
    # Language pull: Rust, Go, Ruby, Python, PHP, Javascript, C, C++, Java
    # For Rust: curl https://sh.rustup.rs -sSf | sh

    if app.pargs.language:
        specify_language = 0
        language_packet = ""
        app.log.info("Received option: l => {}".format(app.pargs.language.lower()))
        if "ruby" in app.pargs.language.lower():
            if "ubuntu" in app.pargs.os.lower() or "debian" in app.pargs.os.lower():
                language_packet = "ruby-full"
            else:
                language_packet = "ruby"

        print("You chosen language '{}'".format(app.pargs.language.lower()))

        # Make a choice of version
        if "python" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "python")
        if "php" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "php")
        if "js" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "nodejs")
        if "c" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "gcc")
        if "c++" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "g++")
        # Make a choice of interpretator
        if "java" in app.pargs.language.lower():
            language_packet = check_existence(operation_system, "default-jre")
        if "rust" in app.pargs.language.lower():
            print("This is specify language, which are not in {}'s repository. Default value is used".format(operation_system))
            dockerstrings.append("RUN {} curl".format(install))
            dockerstrings.append("RUN curl https://sh.rustup.rs -sSf | sh\n")
            specify_language = 1

        if not specify_language:
            dockerstrings.append("RUN {} {}\n".format(install, language_packet))

    # Make a choice of Databases
    # Pull of DBs: MySQL, PostgreSQL, MongoDB
    if app.pargs.database:
        app.log.info("Received option: db => {}".format(app.pargs.database))
        database = ""

        print("You chosen database '{}'".format(app.pargs.database.lower()))

        # Make a choice of version
        if "mysql" in app.pargs.database.lower():
            database = check_existence(operation_system, "mysql-server")

        # PostgreSQL have a some dependencies, a like
        # 'postgresql-contrib', which provides additional functionality
        if "postgresql" in app.pargs.database.lower():
            database = check_existence(operation_system, "postgresql")

        if "mongodb" in app.pargs.database.lower():
            database = check_existence(operation_system, "mongodb-org")

        dockerstrings.append("RUN {} {}\n".format(install, database))

        # Interactive mode for import DB to Docker
        database_interactive(database)

    # Make a choice of ports, using by Docker
    if app.pargs.ports:

        # If sequence is given
        if "," in app.pargs.ports:
            ports = re.findall(r"[, ]*(\d)[, ]*[^-]", app.pargs.ports)
            for port in ports:
                if port:
                    dockerstrings.append("EXPOSE {}\n".format(str(port)))

        # If range is given
        if "-" in app.pargs.ports:
            ports = re.findall(r"(\d)-(\d)", app.pargs.ports)
            print(ports, len(ports))
            i = 0
            while i < len(ports):
                for port in range(int(ports[i][0]), int(ports[i][1])+1):
                    dockerstrings.append("EXPOSE {}\n".format(str(port)))
                i +=1


        app.log.info("Received option: p => {}".format(app.pargs.ports))

    # Make active ssh-server and setting root's password
    if app.pargs.ssh:
        sshd_config(install, app.pargs.ssh)

    # Make active telnet-server and setting root's password
    if app.pargs.telnet:
        telnetd_config(install, app.pargs.telnet)

    # List of docker restart conditions
    restart_conditions = ['on-failure', 'always', 'unless-stopped']

    # Make choice container restart condition
    if app.pargs.restart:
        if app.pargs.restart.lower() in restart_conditions:
            dockerstrings.append("CMD [\"--restart\", \"{}\"]\n".format(app.pargs.restart.lower()))

    # Make a choice of volume directory
    if app.pargs.volume:
        choice = ''

        # Processing of directory volume choice
        while choice.lower() != "q":
            choice = input("Choose next common(shared) directory (or \'Q\' for finish choice): ")
            if choice.lower() is "q":
                continue
            dockerstrings.append("VOLUME [\"{}\"]\n".format(choice))

    # Make a choice of addition files to docker image
    if app.pargs.add:
        choice_paths_from = ''

        # Processing of adding files to image
        while choice_paths_from.lower() != "q":
            choice_paths_from = input("Choose next file (or \'Q\' for finish choice): ")
            choice_paths_to = input("Choose destination directory: ")
            if choice_paths_from.lower() is "q":
                continue

            if len(choice_paths_from) == 0 or len(choice_paths_to) == 0:
                print("Wrong parameters!")
                continue

            choice = ''
            while choice not in "yn":
                choice = input("Is this file on your local machine? [Y/N]: ")
                if choice.lower() is "y":
                    dockerstrings.append("COPY \"{}\" \"{}\"\n".format(choice_paths_from, choice_paths_to))
                elif choice.lower() is "n":
                    dockerstrings.append("ADD \"{}\" \"{}\"\n".format(choice_paths_from, choice_paths_to))

    if app.pargs.workdir:
        dockerstrings.append("WORKDIR {}\n".format(app.pargs.workdir))

    dockerfile = open("Dockerfile", "w")
    print dockerstrings
    dockerfile.writelines(dockerstrings)
    dockerfile.close()
