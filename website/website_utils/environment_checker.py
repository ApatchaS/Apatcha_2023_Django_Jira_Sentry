import os
from dotenv import load_dotenv


class Environment():
	"""
According to security measurences sensitive data should be stored in environment
and never be pushed to git
To perform this secret keys (like: django SECRET_KEY, API_KEY e.t.c) will be stored in .env file
 * That file will be found on runserver (or will be created by script)
 * File's content will be loaded into environment by dotenv library
 * By calling get(variable) method value of data with name <variable> will be checked and returned	
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
							"to store sensitive variables as SECRET_KEY, API_KEY e.t.c; "
							"Please put such values there: <VAR>='<VALUE>'")
	
	def load(self):
		load_dotenv(self.env_path)		
	
	def get(self, variable):
		value = os.environ.get(variable)
		if value == None or len(value) == 0:
			raise ValueError(f"Please check value of {variable}; "
								"You should not leave variable value empty")
		return value