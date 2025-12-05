# Ice-Cream Parlor: Processing

This small Python microservice simulates order processing. It does the following:
1. Reads an order from a RabbitMQ queue
2. Waits for a small time
3. Writes the order to another queue, updating its status.

These functions are controlled by parameters in *.env*.