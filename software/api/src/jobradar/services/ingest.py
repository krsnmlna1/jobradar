import logging
from enum import Enum

logger = logging.getLogger(__name__)


class IngestResult(str, Enum):
    CREATED = "created"
    DUPLICATE = "duplicate"


async def insert_job(conn, job):
    sql = """
            insert into jobs (source, ext_id, title, company, url)
            values (%s, %s, %s, %s, %s)
            on conflict (source, ext_id)
            do nothing RETURNING id
    """
    values = (job.source, job.ext_id, job.title, job.company, job.url)
    async with conn.cursor() as cur:
        await cur.execute(sql, values)
        row = await cur.fetchone()

    if row is None:
        logger.info("job duplicate", extra={"ext_id": job.ext_id, "source": job.source})
        return IngestResult.DUPLICATE, None
    else:
        logger.info("job created", extra={"ext_id": job.ext_id, "source": job.source})
        return IngestResult.CREATED, row[0]
