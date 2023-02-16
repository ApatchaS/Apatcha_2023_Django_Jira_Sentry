import aiohttp

class JiraClient():

	def __init__(self, token, timeout):
		session_timeout = aiohttp.ClientTimeout(total=timeout)
		session_token = 'Bearer ' + token
		self.session = aiohttp.ClientSession(timeout=session_timeout)
		self.session.headers.add('Authorization', session_token)
	
	async def jira_post_request(self,
			     				url,
								data,
								ssl=True,
								status=201,
								content_type='application/json;charset=UTF-8',):
		headers={'Content-Type': content_type}
		response = None
		try:
			async with self.session.post(url, ssl=ssl, headers=headers, data=data) as resp:
				if resp.status==status:
					response = await resp.read()
		except:
			return None
		return response

	async def close(self):
		if not self.session.closed:
			await self.session.close()
		return