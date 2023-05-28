# Ticket Service

This is a sample event ticketing service that handles listing events, 
making reservations, modifying and cancelling reservations.

## Rebuild
Run this command if you make changes to the Dockerfile

``` docker build -t ticket-service .```

## Run Unit Tests
``` python3 -m unittest discover -s test```

## Running the Flask server
### Directly
```python main.py```

### In a Docker container
```docker run -p 8000:8000 ticket-service```

## Viewing the Swagger UI Console
The swagger UI console will be viewable by default under the `/ui/` path, e.g.: http://localhost:8000/ui