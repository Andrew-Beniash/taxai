#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script to save the Postman collection to a file

echo -e "${BLUE}Saving Postman collection for Tax AI API...${NC}"

# Directory to save the collection
DIRECTORY="$PWD/tests/postman"

# Create directory if it doesn't exist
mkdir -p $DIRECTORY

# Save collection to file
cat > "$DIRECTORY/taxai-postman-collection.json" << 'EOF'
{
	"info": {
		"_postman_id": "9e5c4fac-8a4d-4e34-b8e4-ecc0dbf21b5a",
		"name": "Tax AI API",
		"description": "Collection for testing the AI-powered tax law API",
		"schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
	},
	"item": [
		{
			"name": "Health Check",
			"request": {
				"method": "GET",
				"header": [],
				"url": {
					"raw": "{{base_url}}/health",
					"host": [
						"{{base_url}}"
					],
					"path": [
						"health"
					]
				},
				"description": "Checks if the API is healthy and ready to process requests"
			},
			"response": []
		},
		{
			"name": "Basic Tax Query",
			"request": {
				"method": "POST",
				"header": [
					{
						"key": "Content-Type",
						"value": "application/json"
					}
				],
				"body": {
					"mode": "raw",
					"raw": "{\n    \"query\": \"What are the tax deductions for a small business?\"\n}"
				},
				"url": {
					"raw": "{{base_url}}/api/v1/query",
					"host": [
						"{{base_url}}"
					],
					"path": [
						"api",
						"v1",
						"query"
					]
				},
				"description": "Sends a basic tax law query to the AI system"
			},
			"response": []
		},
		{
			"name": "Query with Context",
			"request": {
				"method": "POST",
				"header": [
					{
						"key": "Content-Type",
						"value": "application/json"
					}
				],
				"body": {
					"mode": "raw",
					"raw": "{\n    \"query\": \"Are home office expenses deductible?\",\n    \"context\": [\n        \"I am a self-employed consultant\",\n        \"I use 25% of my home exclusively for business\",\n        \"Tax year 2024\"\n    ]\n}"
				},
				"url": {
					"raw": "{{base_url}}/api/v1/query",
					"host": [
						"{{base_url}}"
					],
					"path": [
						"api",
						"v1",
						"query"
					]
				},
				"description": "Sends a tax query with additional context for more accurate responses"
			},
			"response": []
		},
		{
			"name": "Complex Tax Query",
			"request": {
				"method": "POST",
				"header": [
					{
						"key": "Content-Type",
						"value": "application/json"
					}
				],
				"body": {
					"mode": "raw",
					"raw": "{\n    \"query\": \"What are the tax implications of selling a rental property that I've owned for 5 years and depreciated according to IRS guidelines?\"\n}"
				},
				"url": {
					"raw": "{{base_url}}/api/v1/query",
					"host": [
						"{{base_url}}"
					],
					"path": [
						"api",
						"v1",
						"query"
					]
				},
				"description": "Tests the AI with a complex tax scenario requiring detailed knowledge"
			},
			"response": []
		},
		{
			"name": "Invalid Query (Empty)",
			"request": {
				"method": "POST",
				"header": [
					{
						"key": "Content-Type",
						"value": "application/json"
					}
				],
				"body": {
					"mode": "raw",
					"raw": "{\n    \"query\": \"\"\n}"
				},
				"url": {
					"raw": "{{base_url}}/api/v1/query",
					"host": [
						"{{base_url}}"
					],
					"path": [
						"api",
						"v1",
						"query"
					]
				},
				"description": "Tests validation by sending an empty query (should return 400 Bad Request)"
			},
			"response": []
		},
		{
			"name": "Non-Tax Query",
			"request": {
				"method": "POST",
				"header": [
					{
						"key": "Content-Type",
						"value": "application/json"
					}
				],
				"body": {
					"mode": "raw",
					"raw": "{\n    \"query\": \"What is the weather like today?\"\n}"
				},
				"url": {
					"raw": "{{base_url}}/api/v1/query",
					"host": [
						"{{base_url}}"
					],
					"path": [
						"api",
						"v1",
						"query"
					]
				},
				"description": "Tests how the system handles queries that are not tax-related"
			},
			"response": []
		},
		{
			"name": "API Root",
			"request": {
				"method": "GET",
				"header": [],
				"url": {
					"raw": "{{base_url}}/",
					"host": [
						"{{base_url}}"
					],
					"path": [
						""
					]
				},
				"description": "Gets the root endpoint information"
			},
			"response": []
		}
	],
	"event": [
		{
			"listen": "prerequest",
			"script": {
				"type": "text/javascript",
				"exec": [
					""
				]
			}
		},
		{
			"listen": "test",
			"script": {
				"type": "text/javascript",
				"exec": [
					""
				]
			}
		}
	],
	"variable": [
		{
			"key": "base_url",
			"value": "http://localhost:8000",
			"type": "string",
			"description": "Base URL for the Tax AI API"
		}
	]
}
EOF

echo -e "${GREEN}Postman collection saved to $DIRECTORY/taxai-postman-collection.json${NC}"
echo -e "${BLUE}You can now import this collection into Postman to test the API.${NC}"
