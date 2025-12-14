#!/bin/bash

# Script to update proprietary license headers to MIT license in all Python files

echo "Updating license headers to MIT License in Python files..."

# Find all Python files in the src directory
find src -name "*.py" -type f | while read file; do
  echo "Processing $file"
  
  # Replace proprietary license header with MIT license header
  sed -i 's/© 2025 Andrei Antonescu. All rights reserved./Copyright (c) 2025 Andrei Antonescu/g' "$file"
  sed -i 's/Proprietary – not licensed for public redistribution./SPDX-License-Identifier: MIT/g' "$file"
done

echo "License header update completed!"