import unittest
import random
import string
from docker_generator import *

def selectOs(os):
	if os.lower() in ["ubuntu", "debian"]:
		return "apt-get -qq -y install"
	elif os is "arch":
		return "pacman -S"
	elif os is "centos":
		return "yum"
	else:
		return None

class testAppFunctions(unittest.TestCase):
	lang  = ['python', 'go', 'php', 'nodejs', 'c', 'c++', 'java', 'ruby', 'rust']
	dbms  = ['mysql', 'postgres', 'mongo']
	os    = ['ubuntu', 'debian', 'arch', 'centos']
	outf  = ""

	def setUp(self):
		self.outf  = open("test_Dockerfile","r+")

	def test_sshd_config(self):
		#preset
		example = "RUN {} openssh-server\nRUN mkdir /var/run/sshd\nRUN echo 'root:{}' | chpasswd\nRUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config\nEXPOSE 22\nCMD [\"/usr/sbin/sshd\", \"-D\"]\n"
		tmp_os = random.choice(self.os)
		tmp_pw = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
		# _ln = random.choice(self.languagesc)

		# test №1. All data ok
		# self.outf.seek(0)
		self.outf.truncate()
		sshd_config(self.outf, selectOs(tmp_os), tmp_pw)
		self.outf.seek(0)
		result = self.outf.read()
		self.assertEqual(example.format(selectOs(tmp_os), tmp_pw), result)

		#test №2. OS incorrect
		# self.outf.seek(0)
		# self.outf.truncate()
		# sshd_config(self.outf, "sadasd", tmp_pw)
		# self.outf.seek(0)
		# result = self.outf.read()
		# self.assertEqual(example.format("sadasd", tmp_pw), result)


		# self.assertEqual('foo'.upper(), 'FOO')

	def test_telnetd_config(self):
		#preset
		example = "RUN {} telnetd\nRUN echo 'root:{}' | chpasswd\nEXPOSE 23\nCMD [\"/usr/sbin/sshd\", \"-D\"]\n"
		tmp_os = random.choice(self.os)
		tmp_pw = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

		# test №1. All data ok
		self.outf.truncate()
		telnetd_config(self.outf, selectOs(tmp_os), tmp_pw)
		self.outf.seek(0)
		result = self.outf.read()
		self.assertEqual(example.format(selectOs(tmp_os), tmp_pw), result)

	@unittest.expectedFailure
	def test_check_existence_in_repository(self):
		tmp_os = random.choice(self.os)
		# check_existence_in_repository("debian", "mysql-server")
		# test №1. All data ok
		self.assertTrue(check_existence_in_repository(tmp_os, "mysql-server"))
		# test №2. Bad OS
		self.assertFalse(check_existence_in_repository("4lenOS", "mysql-server"))
		# test №3. Bad package
		self.assertFalse(check_existence_in_repository(tmp_os, "berdsk"))

	# def test_add_external_file(self):
	# 	return 0
	# def test_language_interactive(self):
	# 	return 0
	# def test_database_interactive(self):
	# 	return 0
	# def test_check_existence(self):
	# 	return 0
	def tearDown(self):
		self.outf.close()

if __name__ == '__main__':
	unittest.main(verbosity=2)
	# dockerfile = open("test_Dockerfile","w")
	# dockerfile.write("KUES")
	# ksshd_config(dockerfile, "KEK", "MEK")
	# dockerfile.close()







# import sys
# sys.path.insert(0, '../')
# from cement.utils import test
# from docker_generator import MyApp

# class MyTestCase(test.CementTestCase):
#     app_class = MyApp

#     def setUp(self):
#         super(MyTestCase, self).setUp()

#         # Clear existing hooks/handlers/etc
#         self.reset_backend()

#         # Create a default application for the test functions to use.
#         # Note that some tests make require you to perform this in the
#         # test function in order to alter functionality.  That perfectly
#         # fine, this is only hear for convenience
#         self.app = MyApp(argv=[], config_files=[])

#     def test_myapp(self):
#         # Parameters
#         self.app = self.make_app(argv=['--ssh', 'bar'])
#         # Setup the application
#         self.app.setup()
#         print("KEK")
#         # Perform basic assertion checks.  You can do this anywhere in the
#         # test function, depending on what the assertion is checking.
#         # self.ok(self.config.has_key('myapp', 'debug'))
#         # self.eq(self.config.get('myapp', 'debug'), False)

#         # Run the applicaion, if necessary
#         self.app.run()

#         # Close the application, again if necessary
#         self.app.close()

#     @test.raises(Exception)
#     def test_exception(self):
#         try:
#             # Perform tests that intentionally cause an exception.  The
#             # test passes only if the exception is raised.
#             raise Exception('test')
#         except Exception as e:
#             # Do further checks to ensure the proper exception was raised
#             self.eq(e.args[0], 'Some Exception Message')

#             # Finally, call raise again which re-raises the exception that
#             # we just caught.  This completes out test (to actually
#             # verify that the exception was raised)
#             raise

# def main():
#     MyTestCase()

# if __name__ == '__main__':
#     main()
