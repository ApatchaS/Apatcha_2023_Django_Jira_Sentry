from .custom_exceptions import InvalidJSONFields
import operator as op

class IssueBodyBuilder():

	required_fields = {
		'sentry_project_name': ['project_name'],
		'type': ['event', 'exception', 'values', 0, 'type'],
		'value': ['event', 'exception', 'values', 0, 'value'],
		'traceback': ['event', 'exception', 'values', 0, 'stacktrace', 'frames', -1],
		'url': ['url'],
	}

	def __init__(self, _json_request_body):
		self.body = _json_request_body
		self.fields = self.get_fields()

	def get_field(self, name, path):
		obj = self.body
		try:
			for item in path:
				func = op.itemgetter(item)
				obj = func(obj)
		except:
			return (False, {name: None})
		return (True, {name: obj})

	def get_fields(self, dictionary=required_fields):
		result = {}
		valid_fields = True
		for key, value in dictionary.items():
			valid_field, field = self.get_field(key, value)
			result.update(field)
			if not valid_field:
				valid_fields = False
		if not valid_fields:
			raise InvalidJSONFields(
						400,
						"One or several fields couldn't be found (marked as None)",
						result,
						)
		return result