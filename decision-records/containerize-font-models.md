# Use Different Containers For Different Font Models

## Status

Accepted

## Context

2025 sees the third group to attempt this FYP topic and the integration of the second font model to the website. It is likely that more models will be tried and demonstrated through the website in the future.

The approach of a single API application requires both models to be on the same runtime, requiring a single install configuration to run both models. The install configuration for multiple models can quite hard to figure out, since their respective projects require different version dependencies and install methods. It is hard to scale up to more models.

## Decision

Use a container to serve the frontend application. Use one container per font model, running its own API application with a job queue.

Use a proxy server or a gateway API application to forward requests from the frontend application to the font model containers.

## Consequences

Effects

- Increase in scalability of models, reducing integration difficulties/impossibilities
- Each container can have independent technology choices
- Improves maintainability by isolating concerns
- Using a job queue in each container removes the need to keep track of container states in a gateway API application

Trade-offs

- More code needs to be written, increasing the complexity of the project
- A longer install and set up time is required
- More API surfaces need to be maintained
- Compared to using a single job queue in a gateway API application, there are more logic scattered and duplicated in the respective containers, making it harder to introduce features to all job queues
