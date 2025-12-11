# Ice-Cream Parlor: Processing

This small Python microservice simulates order processing. It does the following:
1. Reads an order from a RabbitMQ queue
2. Waits for a small time
3. Writes the order to another queue, and writes a status update into another queue.

## Configuration

Agent profiles (preparation, delivery...) are defined in *config.yaml*. The agent profile is selected by the first command-line argument, or the environment variable *PROFILE*