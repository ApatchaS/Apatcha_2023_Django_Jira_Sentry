import json

class IssueReqResHandler():
	
	def __init__(self, _content_type, _body):
		self.full_json = None
		self.message = "Issue successfully recieved!"
		self.status_code = 202
		self.check_request(_content_type, _body)
	
	def check_request(self, _content_type, _body):
		if _content_type != 'application/json':
			self.message = "Issue should be sent as json: check request's body and headers"
			self.status_code = 406
		else:
			try:
				self.full_json = json.loads(_body)
			except json.JSONDecodeError:
				self.message = "Sent json have syntaxis errors"
				self.status_code = 400
		return (self.full_json, self.message, self.status_code)

	def get_sentry_project_name(self):
		name = 'sentry_project_name'
		value = None
		try:
			value = self.full_json['project_name']
		except:
			self.message = "One or several fields couldn't be found"
			self.status_code = 400
		return {name:value}

	def get_sentry_type(self):
		name = 'type'
		value = None
		try:
			value = self.full_json['event']['exception']['values'][0]['type']
		except:
			self.message = "One or several fields couldn't be found"
			self.status_code = 400
		return {name:value}
		
	def get_sentry_value(self):
		name = 'value'
		value = None
		try:
			value = self.full_json['event']['exception']['values'][0]['value']
		except:
			self.message = "One or several fields couldn't be found"
			self.status_code = 400
		return {name:value}

	def get_sentry_traceback(self):
		name = 'traceback'
		value = None
		try:
			value = self.full_json['event']['exception']['values'][0]['stacktrace']['frames'][-1]
		except:
			self.message = "One or several fields couldn't be found"
			self.status_code = 400
		return {name:value}

	
	def get_sentry_url(self):
		name = 'url'
		value = None
		try:
			value = self.full_json['url']
		except:
			self.message = "One or several fields couldn't be found"
			self.status_code = 400
		return {name:value}

	def form_response(self):
		if self.status_code != 202:
			return {}
		return {
		**self.get_sentry_project_name(),
		**self.get_sentry_type(),
		**self.get_sentry_value(),
		**self.get_sentry_traceback(),
		**self.get_sentry_url(),
		}
	
	def form_meta_response(self):
		content = self.form_response()
		return {
			'message': self.message,
			'status code': self.status_code,
			'content': content
		}