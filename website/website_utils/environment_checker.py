import os
from dotenv import load_dotenv

ENV_NAME = '.env'

class Environment():
	
	def __init__(self, _project_dir):
		self.project_dir = _project_dir
		self.env_name = ENV_NAME
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