from cement.core.foundation import CementApp
from cement.core import hook
from cement.utils.misc import init_defaults

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
            install = "packman -S"
        if "centos" in app.pargs.os.lower():
            install = "yum"

    dockerfile.write(maintainer)

    # Make install some language interpretator, independently from OS
    # Language pull: Rust, Go, Ruby, Python, PHP, Javascript, C, C++, Java
    # For Rust: curl https://sh.rustup.rs -sSf | sh
    # Also Go have specify installing process

    if app.pargs.language:
        language_packet = ""
        app.log.info("Received option: l => %s" % app.pargs.language.lower())
        if "ruby" in app.pargs.language.lower():
            if "ubuntu" in app.pargs.os.lower() or "debian" in app.pargs.os.lower():
                language_packet = "ruby-full"
            else:
                language_packet = "ruby"

        if "python" in app.pargs.language.lower():
            language_packet = "python"

        if "php" in app.pargs.language.lower():
            language_packet = "php"

        if "javascript" in app.pargs.language.lower():
            language_packet = "nodejs"

        if "c" in app.pargs.language.lower():
            language_packet = "gcc"

        if "c++" in app.pargs.language.lower():
            language_packet = "g++"

        if "java" in app.pargs.language.lower():
            language_packet = "default-jre"

        dockerfile.write("RUN "+install+ " %s\n" % language_packet)


    if app.pargs.database:
        app.log.info("Received option: db => %s" % app.pargs.database)
    if app.pargs.ports:
        app.log.info("Received option: p => %s" % app.pargs.ports)
