#!/bin/bash

# Script to update proprietary license headers to MIT license in all code and documentation files

echo "Updating license headers to MIT License across the codebase..."

# Find all Python files in the project
find . -name "*.py" -type f -not -path "./venv/*" | while read file; do
  echo "Processing $file"
  
  # Replace proprietary license header with MIT license header
  sed -i 's/© 2025 Andrei Antonescu. All rights reserved./Copyright (c) 2025 Andrei Antonescu/g' "$file"
  sed -i 's/Proprietary – not licensed for public redistribution./SPDX-License-Identifier: MIT/g' "$file"
done

# Find all Markdown files in the project
find . -name "*.md" -type f -not -path "./venv/*" | while read file; do
  echo "Processing $file"
  
  # Replace proprietary license header with MIT license header
  sed -i 's/© 2025 Andrei Antonescu. All rights reserved./Copyright (c) 2025 Andrei Antonescu/g' "$file"
  sed -i 's/Proprietary – not licensed for public redistribution./SPDX-License-Identifier: MIT/g' "$file"
done

# Handle other file types if needed
# find . -name "*.json" -type f -not -path "./venv/*" | while read file; do
#   echo "Processing $file"
#   sed -i 's/Proprietary – not licensed for public redistribution./SPDX-License-Identifier: MIT/g' "$file"
# done

echo "License header update completed!"