# geo_ip

I wanted to get most of the boilerplate out of the way, so I used:

https://github.com/s3rius/FastAPI-template

The difficult part of the project is that we want the rate limiter to be global, so we can replicate the servers but have a correct rate limit overall.

I decided to use redis for rate limiting.

https://redis.com/redis-best-practices/basic-rate-limiting/

For testing, I use minutes rather than hours but changes can be made easily.

Cache relies on in-memory first then redis as well.

Having `docker-compose` make it easy to start two (or more) replicas of the server and redis to test it out.

## Local deployment

This will **NOT** use the rate limiter as I only implemented the global version that is using redis.

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m geo_ip
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Docker Compose

This is recommended way to test the functionality as it will use proper caching and rate limiting.

You can start the project with docker using this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build
```

If you want to develop in docker with autoreload add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up
```

This command exposes the web application on port 4001, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . build
```

To test it, open `http://0.0.0.0:4001/api/geo_ip/70.23.35.53` in your browser. Note that `meta` will contain the source of the data (service, if it was cached and what server received the request).

Rate limiting is set at 5 per minute and cache expires after 2 minutes but could easily be configured.


## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variables should start with "GEO_IP_" prefix.

For example if you see in your "geo_ip/settings.py" a variable named like
`random_parameter`, you should provide the "GEO_IP_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `geo_ip.settings.Settings.Config`.

An example of .env file:
```bash
GEO_IP_RELOAD="True"
GEO_IP_PORT="8000"
GEO_IP_ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Testing

I spent already quite a lot of time getting this to work with docker-compose, redis and fastapi (which I was not really familiar with but wanted to have fun -- the annoying part was how to get the redis connection pool).

I therefore didn't add tests, and it would be the first thing to do as well as fixing the pre-commit checks.

Note that I broke different functionalities into different services, so it would be possible to test many aspect to the route using dependency injection.

One thing that bothers me is that the redis_pool is passed to the cache and limiter API and maybe passing the request would be a tiny bit better, but I couldn't find a way to get the app globally to get the redis_pool and all the docs I found was using the pattern of getting the pool from the request.app.
