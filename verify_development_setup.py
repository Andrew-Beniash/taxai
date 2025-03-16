#!/usr/bin/env python3
"""
Script to verify the development setup for the AI-Powered Tax Law Application.
This script checks:
1. FastAPI server - runs it locally and validates API responses
2. Git version control - checks the repository status
3. Docker containers - tests if they build and start correctly
"""

import os
import sys
import time
import subprocess
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Colors for terminal output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 80}{NC}")
    print(f"{BLUE}=== {text}{NC}")
    print(f"{BLUE}{'=' * 80}{NC}\n")

def print_success(text):
    """Print a success message."""
    print(f"{GREEN}✓ {text}{NC}")

def print_warning(text):
    """Print a warning message."""
    print(f"{YELLOW}⚠ {text}{NC}")

def print_error(text):
    """Print an error message."""
    print(f"{RED}✗ {text}{NC}")

def run_command(command, shell=False):
    """Run a shell command and return stdout, stderr, and return code."""
    try:
        process = subprocess.run(
            command,
            shell=shell,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process.stdout, process.stderr, process.returncode
    except Exception as e:
        return "", str(e), 1

def check_fastapi_server():
    """Check if FastAPI server runs correctly and responds to requests."""
    print_header("Verifying FastAPI Server")
    
    # Start FastAPI server in the background
    print("Starting FastAPI server...")
    server_process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Test API endpoints
    server_running = False
    try:
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print_success("Root endpoint is working!")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
            server_running = True
        else:
            print_error(f"Root endpoint returned status code {response.status_code}")
            
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print_success("Health endpoint is working!")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
        else:
            print_error(f"Health endpoint returned status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print_error("Failed to connect to FastAPI server")
    finally:
        # Stop the server
        print("Stopping FastAPI server...")
        server_process.terminate()
        server_process.wait()
    
    return server_running

def check_git_version_control():
    """Verify Git repository status."""
    print_header("Verifying Git Version Control")
    
    # Check if .git directory exists
    if not os.path.isdir(".git"):
        print_error("No Git repository found in the current directory")
        return False
    
    # Check Git version
    stdout, stderr, rc = run_command(["git", "--version"])
    if rc != 0:
        print_error(f"Git not installed or not working correctly: {stderr}")
        return False
    
    print_success(f"Git is installed: {stdout.strip()}")
    
    # Check repository status
    stdout, stderr, rc = run_command(["git", "status"])
    if rc != 0:
        print_error(f"Failed to get Git status: {stderr}")
        return False
    
    print(f"Git repository status:\n{stdout.strip()}")
    
    # Check remote repositories
    stdout, stderr, rc = run_command(["git", "remote", "-v"])
    if rc != 0:
        print_warning(f"Failed to get Git remotes: {stderr}")
    else:
        if stdout.strip():
            print_success("Git remotes are configured:")
            print(stdout.strip())
        else:
            print_warning("No Git remotes configured")
    
    # Check if GitHub Actions is configured
    if os.path.isdir(".github/workflows"):
        print_success("GitHub Actions workflows are configured")
        for workflow_file in os.listdir(".github/workflows"):
            print(f"  - {workflow_file}")
    else:
        print_warning("GitHub Actions workflows not found")
    
    return True

def check_docker_setup():
    """Check Docker and Docker Compose setup."""
    print_header("Verifying Docker Setup")
    
    # Run verify_docker_setup.sh if it exists
    if os.path.isfile("verify_docker_setup.sh"):
        print("Running verify_docker_setup.sh...")
        stdout, stderr, rc = run_command(["bash", "verify_docker_setup.sh"])
        if rc != 0:
            print_error(f"Docker verification failed: {stderr}")
            return False
        print(stdout)
    else:
        # Manual Docker checks
        # Check if Docker is installed
        stdout, stderr, rc = run_command(["docker", "--version"])
        if rc != 0:
            print_error(f"Docker not installed or not working correctly: {stderr}")
            return False
        
        print_success(f"Docker is installed: {stdout.strip()}")
        
        # Check if Docker Compose is installed
        stdout, stderr, rc = run_command(["docker-compose", "--version"])
        if rc != 0:
            print_error(f"Docker Compose not installed or not working correctly: {stderr}")
            return False
        
        print_success(f"Docker Compose is installed: {stdout.strip()}")
        
        # Check if Docker daemon is running
        stdout, stderr, rc = run_command(["docker", "info"])
        if rc != 0:
            print_error("Docker daemon is not running")
            return False
        
        print_success("Docker daemon is running")
    
    # Check if required Docker files exist
    if not os.path.isfile("Dockerfile"):
        print_error("Dockerfile not found")
        return False
    
    print_success("Dockerfile exists")
    
    if not os.path.isfile("docker-compose.yml"):
        print_error("docker-compose.yml not found")
        return False
    
    print_success("docker-compose.yml exists")
    
    # Ask if user wants to test Docker build and run
    print("\nWould you like to test building and running Docker containers?")
    print("This will execute 'docker-compose up -d' and then 'docker-compose down'.")
    response = input("Run Docker test? (y/N): ").strip().lower()
    
    if response == 'y':
        print("Building and starting Docker containers...")
        stdout, stderr, rc = run_command(["docker-compose", "up", "-d", "--build"])
        if rc != 0:
            print_error(f"Failed to build and start Docker containers: {stderr}")
            return False
        
        print_success("Docker containers built and started successfully")
        
        # Wait a bit for containers to initialize
        print("Waiting for containers to initialize...")
        time.sleep(10)
        
        # Check running containers
        stdout, stderr, rc = run_command(["docker-compose", "ps"])
        if rc != 0:
            print_error(f"Failed to list Docker containers: {stderr}")
        else:
            print("Running containers:")
            print(stdout)
        
        # Check if API is accessible in Docker
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print_success("API is accessible in Docker container!")
            else:
                print_warning(f"API returned status code {response.status_code}")
        except requests.exceptions.RequestException:
            print_warning("API is not accessible in Docker container")
        
        # Stopping containers
        print("Stopping and removing Docker containers...")
        stdout, stderr, rc = run_command(["docker-compose", "down"])
        if rc != 0:
            print_error(f"Failed to stop Docker containers: {stderr}")
        else:
            print_success("Docker containers stopped and removed successfully")
    
    return True

def main():
    """Main function to verify development setup."""
    print_header("AI-Powered Tax Law Application - Development Setup Verification")
    
    # Run all checks
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(check_git_version_control): "Git verification",
            executor.submit(check_docker_setup): "Docker verification",
        }
        
        results = {}
        for future in as_completed(futures):
            check_name = futures[future]
            try:
                results[check_name] = future.result()
            except Exception as exc:
                print_error(f"{check_name} generated an exception: {exc}")
                results[check_name] = False
    
    # Run FastAPI check after other checks (it needs to be synchronous)
    results["FastAPI verification"] = check_fastapi_server()
    
    # Print summary
    print_header("Verification Summary")
    
    all_passed = True
    for check_name, passed in results.items():
        if passed:
            print_success(f"{check_name}: Passed")
        else:
            print_error(f"{check_name}: Failed")
            all_passed = False
    
    if all_passed:
        print("\n" + GREEN + "✓ All checks passed! Your development environment is ready." + NC)
        print("\nYou can proceed with the development of the AI-Powered Tax Law Application.")
        return 0
    else:
        print("\n" + RED + "✗ Some checks failed. Please fix the issues before proceeding." + NC)
        return 1

if __name__ == "__main__":
    sys.exit(main())
