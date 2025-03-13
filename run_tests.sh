#!/bin/bash

# Run tests with coverage
coverage run -m unittest discover

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html

echo "HTML report generated in htmlcov/index.html"
