from dotenv import load_dotenv
import os

class Environment():
	"""
According to security measurences sensitive data should be stored in environment
and never be pushed to git
To perform this all sensitive and frequently changing data from website/settings.py were moved to .env file
 * That file will be found on runserver (or will be created by script)
 * File's content will be loaded into environment by dotenv library
 * By calling get(variable) method value of data with name <variable> will be checked and returned
 * To correctly fill the .env file check example.env file in projects root	
	"""

	ENV_NAME = '.env'

	def __init__(self, _project_dir):
		self.project_dir = _project_dir
		self.env_name = self.ENV_NAME
		self.env_path = os.path.join(self.project_dir, self.env_name)
		self.check_existence()
		self.load()
	
	def check_existence(self):
		if not os.path.isfile(self.env_path):
			f = open(self.env_path, 'a')
			f.close()
			raise OSError(2, "There are no file "
							"to load necessary environment variables for the project; "
							f"In {self.project_dir} was created file {self.env_name} "
							"to store all sensitive and frequently changing data from website/settings.py; "
							"Please put needed data according to example.env as follows <VAR>='<VALUE>'")
		return

	def load(self):
		load_dotenv(self.env_path)
		return
	
	def get_environment_variable(variable, var_type=str):
		value = os.environ.get(variable)
		if value == None or len(value) == 0:
			raise ValueError(f"Please check value of {variable}; "
		    					"You may inserted inappropriate to type value"
								"Moreover You should not leave variable value empty")
		if var_type == list:
			value = value.split(' ')
		return var_type(value)