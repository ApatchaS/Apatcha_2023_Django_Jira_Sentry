from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from issues.models import Sentry
import datetime
import logging

DEFAULT_TIME_IN_DAYS=30
logger = logging.getLogger('site')

class Command(BaseCommand):
	help = 'Clears the database of Sentry projects that have <days> no new issue'

	def add_arguments(self, parser):
		parser.add_argument('days',
		      				nargs='?',
		      				type=int,
							help=f'Number of days, from the current moment, \
								at which it is necessary to delete the project. \
								By default this value is {DEFAULT_TIME_IN_DAYS} days',
							default=DEFAULT_TIME_IN_DAYS)
		parser.add_argument('--force', '-f', 
		      				action='store_true',
							help='Disable warning before deletion',)
		
	def handle(self, *args, **options):
		logger.debug('Command-line command delete_outdated_sentry_projects were called')
		current_time = timezone.now()
		objects_to_delete = Sentry.objects.exclude(
				last_updated__gte=current_time - datetime.timedelta(days=options['days']),
				last_updated__lte=current_time
		)
		number_of_projects_to_delete = len(objects_to_delete)
		if not options['force']:
			warning = input(f'Are you sure to delete {number_of_projects_to_delete} projects? (Y/N): ')
			if warning != 'Y':
				output_message = 'The deletion of sentry projects has been cancelled'
				logger.info(output_message)
				return self.style.HTTP_NOT_MODIFIED(output_message)
		try:
			result = objects_to_delete.delete()
			output_message = f'Successfuly deleted {result[0]} projects from sentry datatable'
			logger.info(output_message)
			return self.style.SUCCESS(output_message)
		except:
			output_message = f'Unable to delete {number_of_projects_to_delete}; \
		 					command arguments: \
		 					*records-{len(Sentry.objects.all())} \
		 					*time_in_days-{options["days"]} \
		 					*force_flag-{options["force"]}'
			logging.error(output_message)
			raise CommandError(output_message)