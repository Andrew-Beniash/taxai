# Postman Testing Guide for Tax AI API

This guide explains how to use Postman to test the Tax AI API endpoints, validate responses, and ensure the system is functioning correctly.

## Setup Postman

1. **Install Postman**: Download and install from [postman.com](https://www.postman.com/downloads/)
2. **Import Collection**: Import the provided `taxai-postman-collection.json` file

## Import Steps

1. Open Postman
2. Click **Import** in the upper left corner
3. Select **Raw text** or **File** and import the collection JSON
4. The collection "Tax AI API" will appear in your collections list

## Configure Environment

1. Create a new environment in Postman
2. Add a variable called `base_url` with the value set to your API URL
   - For local testing: `http://localhost:8000`
   - For Kubernetes with port forwarding: `http://localhost:8000`
   - For deployed environments: Use the appropriate URL

## Running the Tests

The collection includes several requests to test different API functionalities:

### 1. Health Check

First, verify that the API is running and healthy:

1. Select the **Health Check** request
2. Click **Send**
3. Expected response:
   - Status code: `200 OK`
   - JSON body: `{"status": "healthy", "model_loaded": true}`

If `model_loaded` is `false`, the AI model is still loading. Wait a few minutes and try again.

### 2. Basic Tax Query

This tests the core functionality of the API:

1. Select the **Basic Tax Query** request
2. Click **Send**
3. Expected response:
   - Status code: `200 OK`
   - JSON body containing:
     - `response`: The AI-generated answer
     - `citations`: Array of sources
     - `confidence_score`: A float between 0-1
     - `processing_time`: Time taken to generate the response

### 3. Query with Context

This tests the ability to include additional context with a query:

1. Select the **Query with Context** request
2. Click **Send**
3. Expected response:
   - Status code: `200 OK`
   - Response that takes the context into account

### 4. Complex Tax Query

Tests the AI's ability to handle more complex questions:

1. Select the **Complex Tax Query** request
2. Click **Send**
3. Expected response:
   - Status code: `200 OK`
   - Response addressing multiple aspects of the query

### 5. Validation Testing

Test error handling with:

- **Invalid Query (Empty)**: Should return 400 Bad Request
- **Non-Tax Query**: Should handle non-tax queries appropriately

## Adding Tests in Postman

You can add automated tests to verify responses:

1. Select a request
2. Go to the **Tests** tab
3. Add JavaScript tests, for example:

```javascript
// For Health Check
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("API is healthy", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql("healthy");
});

// For Tax Query
pm.test("Response includes citations", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.citations).to.be.an('array').that.is.not.empty;
});

pm.test("Confidence score is valid", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.confidence_score).to.be.within(0, 1);
});
```

## Run Collection for End-to-End Testing

To test all endpoints in sequence:

1. Click the "..." (more actions) next to the collection name
2. Select **Run collection**
3. Configure run options (you can exclude certain requests)
4. Click **Run Tax AI API**
5. View the test results for all requests

## Advanced Testing Features

### 1. Environment Variables

You can use environment variables for more complex testing:

1. Create variables for common test values:
   - `test_query`: "What are tax deductions for small businesses?"
   - `complex_query`: "What are the tax implications of selling a rental property?"

2. Use these variables in your requests:
   ```json
   {
     "query": "{{test_query}}"
   }
   ```

### 2. Pre-request Scripts

You can add pre-request scripts to dynamically set up test data:

```javascript
// Generate a random tax query
const queries = [
    "How are capital gains taxed?",
    "Are medical expenses deductible?",
    "What is the standard deduction for 2024?",
    "How do I report freelance income?"
];
pm.variables.set("random_query", queries[Math.floor(Math.random() * queries.length)]);
```

### 3. Response Visualization

For complex responses, you can add visualizations in the Tests tab:

```javascript
// Create a simple visualization of confidence scores
const jsonData = pm.response.json();
if (jsonData.confidence_score) {
    const template = `
        <div style="font-family: Arial; padding: 10px; background-color: #f0f0f0;">
            <h3>Response Confidence</h3>
            <div style="background-color: #e0e0e0; height: 20px; width: 200px;">
                <div style="background-color: #4CAF50; height: 20px; width: ${jsonData.confidence_score * 200}px;"></div>
            </div>
            <p>Score: ${jsonData.confidence_score.toFixed(2)}</p>
        </div>
    `;
    pm.visualizer.set(template);
}
```

## Monitoring Response Times

Pay attention to response times when testing:

- **Health Check**: Should be < 200ms
- **Basic Query**: Initial responses may take 2-5 seconds
- **Complex Query**: May take 3-8 seconds depending on complexity

Response times above these thresholds may indicate performance issues.

## Testing in Different Environments

You can create multiple environments in Postman to test different deployments:

- Local Development
- Kubernetes Development
- Staging
- Production

Simply create a new environment and set the `base_url` variable accordingly.

## Troubleshooting

If you encounter issues:

1. **API not responding**: Check if the API is running with `docker ps` or `kubectl get pods`
2. **Authentication errors**: This sample API doesn't include auth, but production versions might
3. **Slow responses**: Check server logs for bottlenecks
4. **Error responses**: Examine the response body for detailed error messages

## Automated Testing with Newman

You can run Postman collections from the command line using Newman:

1. Install Newman:
   ```bash
   npm install -g newman
   ```

2. Run the collection:
   ```bash
   newman run tests/postman/taxai-postman-collection.json \
     --environment your-environment.json
   ```

3. Generate HTML reports:
   ```bash
   newman run tests/postman/taxai-postman-collection.json \
     --environment your-environment.json \
     --reporters cli,htmlextra \
     --reporter-htmlextra-export ./reports/report.html
   ```

## Next Steps

After validating functionality with Postman, proceed to:

1. **Automated CI/CD Testing**: Integrate these tests in your CI/CD pipeline
2. **Load Testing**: Use the provided load testing scripts to test performance under load
3. **Integration Testing**: Test how the API works with your frontend applications
