# Load Testing Guide for Tax AI API

This guide explains how to conduct load testing on the Tax AI API using Locust to ensure it can handle concurrent requests efficiently.

## Understanding Load Testing

Load testing helps us verify that the API:

1. Maintains response time under load
2. Handles concurrent requests properly
3. Scales appropriately when traffic increases
4. Recovers from failures and errors
5. Does not experience memory leaks or resource exhaustion

## Prerequisites

- Install Locust: `pip install locust`
- A running instance of the Tax AI API (local or in Kubernetes)
- Basic understanding of API endpoints and expected behavior

## Running Basic Load Tests

### Command Line Testing

For quick load tests, you can run Locust in headless mode:

```bash
locust -f load_test.py --host=http://localhost:8000 --headless -u 10 -r 2 --run-time 30s
```

Parameters explained:
- `-f load_test.py`: The load testing script
- `--host=http://localhost:8000`: The API endpoint
- `--headless`: Run without the web interface
- `-u 10`: Simulate 10 concurrent users
- `-r 2`: Spawn rate of 2 users per second
- `--run-time 30s`: Run the test for 30 seconds

### Web Interface Testing

For more detailed control and real-time monitoring:

```bash
locust -f load_test.py --host=http://localhost:8000
```

Then open http://localhost:8089 in your browser where you can:
- Set the number of users to simulate
- Control the spawn rate (users per second)
- Start and stop tests
- View real-time statistics

## Analyzing Load Test Results

When looking at the test results, focus on these key metrics:

1. **Response Time**:
   - Median response time should be under 2 seconds for the Tax AI API
   - 95th percentile response time should be under 5 seconds
   - Look for spikes in response time that might indicate bottlenecks

2. **Request Rate**:
   - How many requests per second the API can handle
   - At what point does the system start to degrade

3. **Failure Rate**:
   - The percentage of failed requests
   - Types of failures (timeouts, errors, etc.)

4. **Resource Utilization**:
   - CPU usage (should be monitored separately)
   - Memory usage (should be monitored separately)
   - Network throughput

## Common Load Testing Scenarios

For the Tax AI API, consider testing:

### 1. Sustained Load

Run a test with a constant number of users (e.g., 20-50) for an extended period (10-30 minutes) to ensure the system remains stable under continuous use.

```bash
locust -f load_test.py --host=http://localhost:8000 --headless -u 20 -r 5 --run-time 10m
```

### 2. Spike Testing

Test how the system handles sudden spikes in traffic:

```bash
# Run with 5 users
locust -f load_test.py --host=http://localhost:8000 --headless -u 5 -r 5 --run-time 1m

# Then immediately run with 50 users (10x spike)
locust -f load_test.py --host=http://localhost:8000 --headless -u 50 -r 50 --run-time 2m

# Then back to normal
locust -f load_test.py --host=http://localhost:8000 --headless -u 5 -r 5 --run-time 2m
```

### 3. Ramp-up Testing

Gradually increase the load to find the breaking point:

```bash
locust -f load_test.py --host=http://localhost:8000 --headless --step-load \
  --step-users 10 --step-time 30s --users 100 --run-time 10m
```

## Interpreting Results for Kubernetes Auto-scaling

When running in Kubernetes with HPA (Horizontal Pod Autoscaler), look for:

1. At what load does auto-scaling trigger?
2. How quickly does the system scale up?
3. Does scaling actually improve performance?
4. After the load decreases, how long does it take to scale down?

You can check the HPA status during load tests:

```bash
kubectl get hpa -n taxai -w
```

## Modifying the Load Test Script

The provided `load_test.py` includes basic scenarios. You can extend it by:

1. Adding different types of queries (simple, complex, with context)
2. Simulating document uploads and processing
3. Creating more realistic user behavior with wait times
4. Adding failure scenarios to test error handling

Example additions to `load_test.py`:

```python
@task(3)  # Lower weight task
def query_with_context(self):
    """Send a tax query with additional context."""
    query = random.choice(SAMPLE_QUERIES)
    context = ["Small business context", "Tax year 2024"]
    
    payload = {"query": query, "context": context}
    
    with self.client.post(
        "/api/v1/query",
        json=payload,
        catch_response=True,
        name="Query with Context"
    ) as response:
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Failed with status code: {response.status_code}")
```

## Performance Bottlenecks and Solutions

When load testing reveals performance issues, consider these common bottlenecks and solutions:

### 1. Slow AI Model Inference

**Symptoms**:
- High response times scaling linearly with user count
- CPU usage near 100% on API pods

**Solutions**:
- Implement response caching using Redis
- Use model quantization to reduce computation requirements
- Scale horizontally with more API pods
- Consider model distillation for faster inference

### 2. Database Bottlenecks

**Symptoms**:
- Database CPU usage high
- Slow responses when querying the knowledge base

**Solutions**:
- Optimize ChromaDB or PostgreSQL configuration
- Implement connection pooling
- Add database read replicas
- Scale up database resources

### 3. Network Limitations

**Symptoms**:
- High network latency
- Timeouts between services

**Solutions**:
- Ensure services are in the same region/zone
- Optimize payload sizes
- Implement persistent connections

## Best Practices

1. **Start Small**: Begin with a few virtual users and increase gradually
2. **Monitor Resources**: Watch CPU, memory, and network during tests
3. **Realistic Data**: Use realistic queries that match actual usage patterns
4. **Separate Environment**: Test in an environment similar to production but separate
5. **Regular Testing**: Run load tests regularly, not just before releases

## Conclusion

Load testing is crucial for ensuring the Tax AI API can handle real-world usage. By systematically testing different scenarios and analyzing the results, you can identify bottlenecks and determine the appropriate scaling configuration for your deployment.

Remember that the goal is not just to find the breaking point, but to ensure the system performs reliably under expected load conditions.
