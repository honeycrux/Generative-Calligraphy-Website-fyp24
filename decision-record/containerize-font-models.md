# Use Different Containers For Different Font Models

## Status

Accepted

## Context

2025 sees the third group to attempt this FYP topic and the integration of the second font model to the website. It is likely that more models will be tried and demonstrated through the website in the future.

The approach of a single API application requires both models to be on the same runtime, requiring a single install configuration to run both models. The install configuration for multiple models can quite hard to figure out, since their respective projects require different version dependencies and install methods. It is hard to scale up to more models.

## Decision

Use a separate container for each font model, running its own API application with a job queue.

Use a gateway API application to process incoming requests from the frontend application and send requests to font model containers.

The use of tools to run multi-container applications such as Docker Compose should be considered in the future.

## Consequences

Effects

- Increase in scalability of models, reducing integration difficulties/impossibilities

Trade-offs

- More code needs to be written, increasing the complexity of the project
- A longer install and set up time is required
- More API surfaces need to be maintained
