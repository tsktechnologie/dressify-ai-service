"""Single-node worker. External provider execution is disabled until trusted asset resolution exists."""
import logging
import os
import time
from app.job_store import claim_next, finish, get_job

log = logging.getLogger(__name__)

def process_one():
    job_id = claim_next()
    if job_id is None:
        return False
    job = get_job(job_id)
    # Fail closed rather than passing untrusted asset IDs as provider URLs.
    finish(job_id, "failed", error_code="ASSET_RESOLVER_NOT_CONFIGURED")
    log.info("Job %s stopped: trusted asset resolver not configured", job_id)
    return True

def main():
    logging.basicConfig(level=logging.INFO)
    interval = max(0.5, float(os.getenv("WORKER_POLL_SECONDS", "2")))
    while True:
        if not process_one():
            time.sleep(interval)

if __name__ == "__main__":
    main()
