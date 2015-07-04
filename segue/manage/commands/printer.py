import time

from redis import Redis
from rq import Queue, Worker
from rq.registry import FinishedJobRegistry

from segue.core import config
from support import *

from segue.frontdesk.services import BadgeService

def _print_dot():
    sys.stdout.write(".")
    sys.stdout.flush()

def _print_queue_size(label, size):
    print "queue {}{}{} has {}{}{} jobs".format(F.RED, label, F.RESET, F.RED, size, F.RESET)

def bad_jobs(debug=False):
    init_command()

    service = BadgeService()

    redis_conn = Redis(host=config.QUEUE_HOST, password=config.QUEUE_PASSWORD)
    queue = Queue('failed', connection=redis_conn)

    while True:
        _print_dot()
        jobs = queue.jobs
        if debug: _print_queue_size('failed', len(job))

        for job in jobs:
            print "writing failure status to job {}{}{}...".format(F.RED, job.id, F.RESET),
            print service.report_failure(job.id)
            job.cleanup(0)
        time.sleep(5)

def good_jobs(debug=False):
    init_command()

    service = BadgeService()

    redis_conn = Redis(host=config.QUEUE_HOST, password=config.QUEUE_PASSWORD)

    registries = [ FinishedJobRegistry(printer, connection=redis_conn) for printer in config.PRINTERS ]

    seen_ids = set([])

    while True:
        _print_dot()

        for registry in registries:
            job_ids = registry.get_job_ids()
            if debug: _print_queue_size(registry.name, len(job_ids))
            for job_id in job_ids:
                if job_id in seen_ids:
                    if debug: print "already saw {}{}{}, skipping".format(F.RED, job_id, F.RESET)
                    continue

                print "writing success status to job {}{}{}...".format(F.RED, job_id, F.RESET),
                print service.report_success(job_id)
                seen_ids.add(job_id)
            registry.cleanup(0)
            time.sleep(5)
