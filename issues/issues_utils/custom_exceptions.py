class SentryRequestExceptions(Exception):
	
	def __init__(self, _status_code, _message, _fields=[]):
		super(SentryRequestExceptions, self).__init__()
		self.status_code = _status_code
		self.message = _message
		self.fields = _fields

class InvalidContentType(SentryRequestExceptions):
	pass

class InvalidJSON(SentryRequestExceptions):
	pass

class InvalidJSONFields(SentryRequestExceptions):
	pass