import json
import operator as op
from django.http import JsonResponse

class IssueReqResHandler():
	"""
This class needed to:
	* check if request have type "application/json"
	* deserialize request body as json and check it's sintaxis
	* get necessary for sending to django and Jira fields from converted json
	* forming response with accepted data / corresponding errors as JSONResponse
It's possible to reach any field of converted json by passing it's "path" represented by list of indexes in json
	"""

	statuses = {
		0: [202, "Issue successfully received!"],
		1: [406, "Issue should be sent as json: check request's body and headers"],
		2: [400, "Sent json have syntaxis errors"],
		3: [400, "One or several fields couldn't be found (marked as None)"],
	}

	required_fields = {
		'sentry_project_name': ['project_name'],
		'type': ['event', 'exception', 'values', 0, 'type'],
		'value': ['event', 'exception', 'values', 0, 'value'],
		'traceback': ['event', 'exception', 'values', 0, 'stacktrace', 'frames', -1],
		'url': ['url'],
	}

	CONTENT_TYPE = "application/json"

	def __init__(self, _request):
		self.status = 0
		self.content_type = _request.content_type
		self.body = _request.body
		self.check_content_type()
		self.body_json = self.get_json_body() if self.status == 0 else {}
		self.fields = self.get_fields() if self.status == 0 else {}
	
	def check_content_type(self, desire_content_type=CONTENT_TYPE):
		if self.content_type != desire_content_type:
			self.status = 1
			return False
		return True

	def get_json_body(self):
		try:
			js = json.loads(self.body)
		except json.JSONDecodeError:
				self.status = 2
				return {}
		return js

	def get_field(self, name, path):
		obj = self.body_json
		try:
			for item in path:
				func = op.itemgetter(item)
				obj = func(obj)
		except:
			self.status = 3
			return {name: None}
		return {name: obj}

	def get_fields(self, dictionary=required_fields):
		result = {}
		for key, value in dictionary.items():
			result.update(self.get_field(key, value))
		return result

	def form_feedback(self):
		stat = IssueReqResHandler.statuses[self.status]
		content = {
			'message': stat[1],
			'status code': stat[0],
			'content': self.fields,
		}
		return JsonResponse(data=content,
							status=stat[0],
							content_type=IssueReqResHandler.CONTENT_TYPE)