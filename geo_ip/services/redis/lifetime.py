from fastapi import FastAPI
from redis import ConnectionPool

from geo_ip.settings import settings


def init_redis(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection pool for redis.

    :param app: current fastapi application.
    """
    app.state.redis_pool = ConnectionPool.from_url(
        str(settings.redis_url),
    )


def shutdown_redis(app: FastAPI) -> None:  # pragma: no cover
    """
    Closes redis connection pool.

    :param app: current FastAPI app.
    """
    app.state.redis_pool.disconnect()
