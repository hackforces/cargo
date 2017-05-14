from cement.core.foundation import CementApp
from cement.core import hook
from cement.utils.misc import init_defaults
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

    # run the application
    app.run()

    install = "apt-get"

    # Choice Operation System and set install
    if app.pargs.os:
        dockerfile.write("FROM %s\n" % app.pargs.os.lower())
        app.log.info("Received option: os => %s" % app.pargs.os.lower())

        if "ubuntu" in app.pargs.os.lower() or "debian" in app.pargs.os.lower():
            install = "apt-get"
        if "arch" in app.pargs.os.lower():
            install = "pacman -S"
        if "centos" in app.pargs.os.lower():
            install = "yum"

    dockerfile.write(maintainer)

    # Make install some language interpretator, independently from OS
    # Language pull: Rust, Go, Ruby, Python, PHP, Javascript, C, C++, Java
    # For Rust: curl https://sh.rustup.rs -sSf | sh

    if app.pargs.language:
        specify_language = 0
        language_packet = ""
        app.log.info("Received option: l => %s" % app.pargs.language.lower())
        if "ruby" in app.pargs.language.lower():
            if "ubuntu" in app.pargs.os.lower() or "debian" in app.pargs.os.lower():
                language_packet = "ruby-full"
            else:
                language_packet = "ruby"

        #Make a choice of version
        if "python" in app.pargs.language.lower():
            language_packet = "python"

        # Make a choice of version
        if "php" in app.pargs.language.lower():
            language_packet = "php"

        if "javascript" in app.pargs.language.lower():
            language_packet = "nodejs"

        if "c" in app.pargs.language.lower():
            language_packet = "gcc"

        if "c++" in app.pargs.language.lower():
            language_packet = "g++"

        # Make a choice of interpritator
        if "java" in app.pargs.language.lower():
            language_packet = "default-jre"

        if "rust" in app.pargs.language.lower():
            dockerfile.write("RUN " + install + " curl")
            dockerfile.write("RUN " + "curl https://sh.rustup.rs -sSf | sh"+ "\n")
            specify_language = 1

        if "go" in app.pargs.language.lower():
            language_packet = "golang-go"

        if not specify_language:
            dockerfile.write("RUN "+install+ " " + language_packet+ "\n")

    # Make a choice of Databases
    # Pull of DBs: MySQL, PostgreSQL, MongoDB
    if app.pargs.database:
        app.log.info("Received option: db => %s" % app.pargs.database)
        database = ""

        # Make a choice of version
        if "mysql" in app.pargs.database.lower():
            database = "mysql-server"

        # PostgreSQL have a some dependencies, a like
        # 'postgresql-contrib', which provides additional functionality
        if "postgresql" in app.pargs.database.lower():
            database = "postgresql"

        if "mongodb" in app.pargs.database.lower():
            database = "mongodb-org"

        dockerfile.write("RUN " + install + " " + database+ "\n")

    # Make a choice of ports, using by Docker
    if app.pargs.ports:

        # If sequence is given
        if "," in app.pargs.ports:
            ports = re.findall(r"[, ]*(\d)[, ]*[^-]", app.pargs.ports)
            for port in ports:
                if port:
                    dockerfile.write("EXPOSE " + str(port)+ "\n")

        #If range is given
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

    dockerfile.close()