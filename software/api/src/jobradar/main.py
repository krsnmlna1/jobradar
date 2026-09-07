import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from psycopg import AsyncConnection, OperationalError
from psycopg.rows import dict_row

from jobradar.db import get_conn, lifespan
from jobradar.schemas import JobDetail, JobIn, JobSummary
from jobradar.services.ingest import IngestResult, insert_job

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health(conn: Annotated[AsyncConnection, Depends(get_conn)]):
    try:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
    except OperationalError:
        logger.error("Database Unreachable")
        raise HTTPException(status_code=503, detail="Database Error")
    return {"status": "ok", "database": "ok"}


@app.post("/jobs")
async def ingest(job: JobIn, conn: Annotated[AsyncConnection, Depends(get_conn)]):
    result, job_id = await insert_job(conn, job)

    if result is IngestResult.CREATED:
        return JSONResponse(status_code=201, content={"id": job_id})
    return JSONResponse(status_code=200, content={"status": "duplicate"})


@app.get("/jobs", response_model=list[JobSummary])
async def list_jobs(conn: Annotated[AsyncConnection, Depends(get_conn)]):
    sql = """
            select id, title, company, location, posted_at
            from jobs order by posted_at desc nulls last limit 50;
    """
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(sql)
        rows = await cur.fetchall()

    return rows


@app.get("/jobs/{job_id}", response_model=JobDetail)
async def get_job(job_id: int, conn: Annotated[AsyncConnection, Depends(get_conn)]):
    sql = """
            select * from jobs where id=%s
    """
    values = (job_id,)
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(sql, values)
        row = await cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Jobs not found")
    return row
