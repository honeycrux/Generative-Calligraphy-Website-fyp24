# Use Different Containers For Different Font Models

## Status

Accepted

## Context

We use multiple font model containers in the backend. We can either expose all endpoints to the frontend, or proxy requests through a proxy layer or a gateway API application.

The GPU machines from the department does not have Docker installed.

Using GPU machines from the department, our experience with the port numbers around 6000 is quite satisfactory. We face less problems with them compared to higher or lower port numbers. (Future users may expand on this with their own findings.)

## Decision

Use the [Traefik binary](https://github.com/traefik/traefik/releases) to run a proxy server and forward requests to the font model containers based on path prefixes (e.g. `/fyp23`, `/fyp24`) ([see this guide](https://fastapi.tiangolo.com/advanced/behind-a-proxy/)).

Current ports used:
- 6700: frontend
- 6701: traefik (backend)
    - 6723: fyp23 container
    - 6724: fyp24 container

## Consequences

Effects

- Encapsulating the concerns of connecting multiple endpoints to a single proxy layer
- Traefik is comparatively easy to configure
- Higher availability guarantee on server environments without certain tools installed

Trade-offs

- Set up and horizontal scaling is harder without the use of orchestration tools like Docker Compose
