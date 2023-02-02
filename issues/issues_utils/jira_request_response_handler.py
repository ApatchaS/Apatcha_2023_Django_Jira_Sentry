import aiohttp
import asyncio
import json

from global_utils.environment import Environment

TIMEOUT_IN_SEC = int(Environment.get_environment_variable('TIMEOUT_IN_SEC'))
BEARER_TOKEN = Environment.get_environment_variable('BEARER_TOKEN')

class JiraClient():

	def __init__(self):
		timeout = aiohttp.ClientTimeout(total=TIMEOUT_IN_SEC)
		token = 'Bearer ' + BEARER_TOKEN
		self.session = aiohttp.ClientSession(timeout=timeout)
		self.session.headers.add('Authorization', token)

	def get_session_info(self):
		print('\033[33mSESSION:\033[0m')
		print('\033[32mHEADERS:\033[0m\n', self.session.headers)
		print('\033[32mCOOKIES:\033[0m\n', self.session.cookie_jar)
		print('\033[32mAUTH:\033[0m\n', self.session.auth)
		return

	async def jira_get_request(self, url, ssl=True, status=200):
		response = None
		try:
			async with self.session.get(url, ssl=ssl) as resp:
				if resp.status == status:
					response = await resp.read()
		except:
			return None
		return response

	def jira_get_project_list(response):
		projects = set()
		json_response = json.loads(response)
		for project in json_response:
			projects.add(project['name'])
		return projects

	async def close(self):
		print('\033[33mSSESSION DESTROY:\033[0m')
		if not self.session.closed:
			await self.session.close()
		print('\033[32mClosed?:\033[0m\n', self.session.closed)
