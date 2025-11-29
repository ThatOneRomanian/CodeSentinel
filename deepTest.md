Scanning 6 files...
Applying AI-powered explanations (placeholder mode)...
# CodeSentinel Security Scan Report

## Scan Summary
- **Total Findings**: 150
- **High Severity**: 126
- **Medium Severity**: 24
- **Low Severity**: 0

## High Severity Findings

### Finding 1
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 9
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  api_key = "sk_test_1234567890abcdefghijklmnop"
  ```

### Finding 2
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 10
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  secret_key = "my_super_secret_key_12345"
  ```

### Finding 3
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 12
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 4
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 12
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 5
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 30
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
  ```

### Finding 6
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 39
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  password = "secure_password_456"
  ```

### Finding 7
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 15
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  database_url = "postgresql://user:password123@localhost:5432/mydb"
  ```

### Finding 8
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 16
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  mysql_conn = "mysql://admin:adminpass@localhost:3306/appdb"
  ```

### Finding 9
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 17
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  redis_url = "redis://user:redispass@localhost:6379/0"
  ```

### Finding 10
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 44
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  connection_string = f"postgresql://{username}:{password}@{host}:{port}/app"
  ```

### Finding 11
- **Rule**: SECRET_AWS_ACCESS_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 30
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
  ```

### Finding 12
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 31
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  ```

### Finding 13
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 9
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  api_key = "sk_test_1234567890abcdefghijklmnop"
  ```

### Finding 14
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 11
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  stripe_key = "sk_live_1234567890abcdefghijklmnop"
  ```

### Finding 15
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 12
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 16
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 29
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "stripe_secret": "sk_test_9876543210zyxwvutsrqponm",
  ```

### Finding 17
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 49
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "google": "ya29.a0AfH6SMBxExampleGoogleOAuthToken",
  ```

### Finding 18
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 50
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "facebook": "EAACEdEose0cBAExampleFacebookAccessToken",
  ```

### Finding 19
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 51
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "slack": "xoxb-1234567890-1234567890-1234567890-abcdefghijkl"
  ```

### Finding 20
- **Rule**: SECRET_HARDCODED_PASSWORD
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 39
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  password = "secure_password_456"
  ```

### Finding 21
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 9
- **Confidence**: 0.5875549647676362
- **Code Excerpt**:
  ```
  api_key = "sk_test_1234567890abcdefghijklmnop"
  ```

### Finding 22
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 11
- **Confidence**: 0.5875549647676362
- **Code Excerpt**:
  ```
  stripe_key = "sk_live_1234567890abcdefghijklmnop"
  ```

### Finding 23
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 12
- **Confidence**: 0.6462406251802887
- **Code Excerpt**:
  ```
  github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 24
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 29
- **Confidence**: 0.5731203125901445
- **Code Excerpt**:
  ```
  "stripe_secret": "sk_test_9876543210zyxwvutsrqponm",
  ```

### Finding 25
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 31
- **Confidence**: 0.5828518619340444
- **Code Excerpt**:
  ```
  "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  ```

### Finding 26
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 49
- **Confidence**: 0.5642243596003866
- **Code Excerpt**:
  ```
  "google": "ya29.a0AfH6SMBxExampleGoogleOAuthToken",
  ```

### Finding 27
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 50
- **Confidence**: 0.5016018619340443
- **Code Excerpt**:
  ```
  "facebook": "EAACEdEose0cBAExampleFacebookAccessToken",
  ```

### Finding 28
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 9
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  api_key = "sk_test_1234567890abcdefghijklmnop"
  ```

### Finding 29
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 11
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  stripe_key = "sk_live_1234567890abcdefghijklmnop"
  ```

### Finding 30
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 29
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  "stripe_secret": "sk_test_9876543210zyxwvutsrqponm",
  ```

### Finding 31
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 9
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  const apiKey = "sk_test_9876543210abcdefghijklmnop";
  ```

### Finding 32
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 12
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  const awsSecretKey = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLESECRET";
  ```

### Finding 33
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 19
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  password: 'javascript_password_789',
  ```

### Finding 34
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 27
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  github: 'ghp_9876543210abcdefghijklmnopqrstuvwxyz'
  ```

### Finding 35
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 33
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  secretKey: 'sk_test_1234567890abcdefghijklmnop',
  ```

### Finding 36
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 38
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  authToken: '1234567890abcdefghijklmnopqrstuvw'
  ```

### Finding 37
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 41
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  apiKey: 'SG.1234567890abcdefghijklmnopqrstuvwxyz.9876543210abcdefghijklmnopqrstuvwxyz'
  ```

### Finding 38
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 52
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  const password = 'function_password_123';
  ```

### Finding 39
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 46
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  const mongoConnection = 'mongodb://user:mongopass123@localhost:27017/app';
  ```

### Finding 40
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 47
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  const redisConnection = 'redis://user:redispass456@localhost:6379/1';
  ```

### Finding 41
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 55
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  return `postgresql://${username}:${password}@${host}:5432/app`;
  ```

### Finding 42
- **Rule**: SECRET_AWS_ACCESS_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 11
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  const awsAccessKey = "AKIAJEXAMPLEACCESSKEY";
  ```

### Finding 43
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 12
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  const awsSecretKey = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLESECRET";
  ```

### Finding 44
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 26
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  facebook: 'EAACEdEose0cBAExampleJavaScriptFacebookToken',
  ```

### Finding 45
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 9
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  const apiKey = "sk_test_9876543210abcdefghijklmnop";
  ```

### Finding 46
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 10
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  const stripeSecret = "sk_live_9876543210abcdefghijklmnop";
  ```

### Finding 47
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 25
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  google: 'ya29.a0AfH6SMBxExampleJavaScriptOAuthToken',
  ```

### Finding 48
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 26
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  facebook: 'EAACEdEose0cBAExampleJavaScriptFacebookToken',
  ```

### Finding 49
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 27
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  github: 'ghp_9876543210abcdefghijklmnopqrstuvwxyz'
  ```

### Finding 50
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 33
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  secretKey: 'sk_test_1234567890abcdefghijklmnop',
  ```

### Finding 51
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 34
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  publishableKey: 'pk_test_1234567890abcdefghijklmnop'
  ```

### Finding 52
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 37
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  accountSid: 'AC1234567890abcdefghijklmnopqrstuv',
  ```

### Finding 53
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 38
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  authToken: '1234567890abcdefghijklmnopqrstuvw'
  ```

### Finding 54
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 41
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  apiKey: 'SG.1234567890abcdefghijklmnopqrstuvwxyz.9876543210abcdefghijklmnopqrstuvwxyz'
  ```

### Finding 55
- **Rule**: SECRET_HARDCODED_PASSWORD
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 10
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  const stripeSecret = "sk_live_9876543210abcdefghijklmnop";
  ```

### Finding 56
- **Rule**: SECRET_HARDCODED_PASSWORD
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 19
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  password: 'javascript_password_789',
  ```

### Finding 57
- **Rule**: SECRET_HARDCODED_PASSWORD
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 52
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  const password = 'function_password_123';
  ```

### Finding 58
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 9
- **Confidence**: 0.5875549647676362
- **Code Excerpt**:
  ```
  const apiKey = "sk_test_9876543210abcdefghijklmnop";
  ```

### Finding 59
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 10
- **Confidence**: 0.5875549647676362
- **Code Excerpt**:
  ```
  const stripeSecret = "sk_live_9876543210abcdefghijklmnop";
  ```

### Finding 60
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 12
- **Confidence**: 0.5903044242607552
- **Code Excerpt**:
  ```
  const awsSecretKey = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLESECRET";
  ```

### Finding 61
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 25
- **Confidence**: 0.5836141031360514
- **Code Excerpt**:
  ```
  google: 'ya29.a0AfH6SMBxExampleJavaScriptOAuthToken',
  ```

### Finding 62
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 26
- **Confidence**: 0.5531398187946426
- **Code Excerpt**:
  ```
  facebook: 'EAACEdEose0cBAExampleJavaScriptFacebookToken',
  ```

### Finding 63
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 27
- **Confidence**: 0.6462406251802887
- **Code Excerpt**:
  ```
  github: 'ghp_9876543210abcdefghijklmnopqrstuvwxyz'
  ```

### Finding 64
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 33
- **Confidence**: 0.5875549647676362
- **Code Excerpt**:
  ```
  secretKey: 'sk_test_1234567890abcdefghijklmnop',
  ```

### Finding 65
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 34
- **Confidence**: 0.5875549647676362
- **Code Excerpt**:
  ```
  publishableKey: 'pk_test_1234567890abcdefghijklmnop'
  ```

### Finding 66
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 37
- **Confidence**: 0.6359328551562923
- **Code Excerpt**:
  ```
  accountSid: 'AC1234567890abcdefghijklmnopqrstuv',
  ```

### Finding 67
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 38
- **Confidence**: 0.630549264919807
- **Code Excerpt**:
  ```
  authToken: '1234567890abcdefghijklmnopqrstuvw'
  ```

### Finding 68
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 41
- **Confidence**: 0.6462406251802887
- **Code Excerpt**:
  ```
  apiKey: 'SG.1234567890abcdefghijklmnopqrstuvwxyz.9876543210abcdefghijklmnopqrstuvwxyz'
  ```

### Finding 69
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 41
- **Confidence**: 0.6462406251802887
- **Code Excerpt**:
  ```
  apiKey: 'SG.1234567890abcdefghijklmnopqrstuvwxyz.9876543210abcdefghijklmnopqrstuvwxyz'
  ```

### Finding 70
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 9
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  const apiKey = "sk_test_9876543210abcdefghijklmnop";
  ```

### Finding 71
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 10
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  const stripeSecret = "sk_live_9876543210abcdefghijklmnop";
  ```

### Finding 72
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 33
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  secretKey: 'sk_test_1234567890abcdefghijklmnop',
  ```

### Finding 73
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 34
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  publishableKey: 'pk_test_1234567890abcdefghijklmnop'
  ```

### Finding 74
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 13
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "github_token": "ghp_5555555555abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 75
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 16
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  "mongodb": "mongodb://user:mongopass555@localhost:27017/app",
  ```

### Finding 76
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 17
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  "redis": "redis://user:redispass555@localhost:6379/2",
  ```

### Finding 77
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 18
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  "postgres": "postgresql://user:postgrespass555@localhost:5432/app"
  ```

### Finding 78
- **Rule**: SECRET_AWS_ACCESS_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 11
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  "aws_access_key_id": "AKIA5555555555EXAMPLE",
  ```

### Finding 79
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 12
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCY5555555555",
  ```

### Finding 80
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 22
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  "facebook": "EAACEdEose0cBAExampleJsonFacebookToken555",
  ```

### Finding 81
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 10
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "stripe_secret_key": "sk_test_5555555555abcdefghijklmnop",
  ```

### Finding 82
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 13
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "github_token": "ghp_5555555555abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 83
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 21
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "google": "ya29.a0AfH6SMBxExampleJsonOAuthToken555",
  ```

### Finding 84
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 22
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  "facebook": "EAACEdEose0cBAExampleJsonFacebookToken555",
  ```

### Finding 85
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 12
- **Confidence**: 0.54268075889569
- **Code Excerpt**:
  ```
  "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCY5555555555",
  ```

### Finding 86
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 13
- **Confidence**: 0.5308958996633665
- **Code Excerpt**:
  ```
  "github_token": "ghp_5555555555abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 87
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 21
- **Confidence**: 0.5743340040453973
- **Code Excerpt**:
  ```
  "google": "ya29.a0AfH6SMBxExampleJsonOAuthToken555",
  ```

### Finding 88
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 22
- **Confidence**: 0.5260372460688345
- **Code Excerpt**:
  ```
  "facebook": "EAACEdEose0cBAExampleJsonFacebookToken555",
  ```

### Finding 89
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 10
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  "stripe_secret_key": "sk_test_5555555555abcdefghijklmnop",
  ```

### Finding 90
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 9
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  password: "yaml_password_789"
  ```

### Finding 91
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 14
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  secret_key: "sk_test_7777777777abcdefghijklmnop"
  ```

### Finding 92
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 20
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  token: "ghp_7777777777abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 93
- **Rule**: hardcoded-api-key
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 20
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  token: "ghp_7777777777abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 94
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 23
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  mongodb: "mongodb://user:mongopass777@localhost:27017/app"
  ```

### Finding 95
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 24
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  redis: "redis://user:redispass777@localhost:6379/3"
  ```

### Finding 96
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 25
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  postgres: "postgresql://user:postgrespass777@localhost:5432/app"
  ```

### Finding 97
- **Rule**: SECRET_AWS_ACCESS_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 17
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  access_key_id: "AKIA7777777777EXAMPLE"
  ```

### Finding 98
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 18
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  secret_access_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCY7777777777"
  ```

### Finding 99
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 29
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  facebook: "EAACEdEose0cBAExampleYamlFacebookToken777"
  ```

### Finding 100
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 14
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  secret_key: "sk_test_7777777777abcdefghijklmnop"
  ```

### Finding 101
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 15
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  publishable_key: "pk_test_7777777777abcdefghijklmnop"
  ```

### Finding 102
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 20
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  token: "ghp_7777777777abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 103
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 28
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  google: "ya29.a0AfH6SMBxExampleYamlOAuthToken777"
  ```

### Finding 104
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 29
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  facebook: "EAACEdEose0cBAExampleYamlFacebookToken777"
  ```

### Finding 105
- **Rule**: SECRET_HARDCODED_PASSWORD
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 9
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  password: "yaml_password_789"
  ```

### Finding 106
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 18
- **Confidence**: 0.5275730499702631
- **Code Excerpt**:
  ```
  secret_access_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCY7777777777"
  ```

### Finding 107
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 20
- **Confidence**: 0.5308958996633665
- **Code Excerpt**:
  ```
  token: "ghp_7777777777abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 108
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 28
- **Confidence**: 0.5642057411697963
- **Code Excerpt**:
  ```
  google: "ya29.a0AfH6SMBxExampleYamlOAuthToken777"
  ```

### Finding 109
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 29
- **Confidence**: 0.5286432002525947
- **Code Excerpt**:
  ```
  facebook: "EAACEdEose0cBAExampleYamlFacebookToken777"
  ```

### Finding 110
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 14
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  secret_key: "sk_test_7777777777abcdefghijklmnop"
  ```

### Finding 111
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 15
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  publishable_key: "pk_test_7777777777abcdefghijklmnop"
  ```

### Finding 112
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 24
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  MONGODB_URI=mongodb://user:mongopass999@localhost:27017/app
  ```

### Finding 113
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 25
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  REDIS_URL=redis://user:redispass999@localhost:6379/4
  ```

### Finding 114
- **Rule**: hardcoded-database
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 26
- **Confidence**: 0.9
- **Code Excerpt**:
  ```
  POSTGRES_URL=postgresql://user:postgrespass999@localhost:5432/app
  ```

### Finding 115
- **Rule**: SECRET_AWS_ACCESS_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 14
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  AWS_ACCESS_KEY_ID=AKIA9999999999EXAMPLE
  ```

### Finding 116
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 15
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCY9999999999
  ```

### Finding 117
- **Rule**: SECRET_AWS_SECRET_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 20
- **Confidence**: 0.85
- **Code Excerpt**:
  ```
  FACEBOOK_ACCESS_TOKEN=EAACEdEose0cBAExampleEnvFacebookToken999
  ```

### Finding 118
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 13
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  STRIPE_SECRET_KEY=sk_test_9999999999abcdefghijklmnop
  ```

### Finding 119
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 16
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  GITHUB_TOKEN=ghp_9999999999abcdefghijklmnopqrstuvwxyz
  ```

### Finding 120
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 19
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  GOOGLE_OAUTH_TOKEN=ya29.a0AfH6SMBxExampleEnvOAuthToken999
  ```

### Finding 121
- **Rule**: SECRET_AZURE_CLIENT_SECRET
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 20
- **Confidence**: 0.8
- **Code Excerpt**:
  ```
  FACEBOOK_ACCESS_TOKEN=EAACEdEose0cBAExampleEnvFacebookToken999
  ```

### Finding 122
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 15
- **Confidence**: 0.5518205192301252
- **Code Excerpt**:
  ```
  AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCY9999999999
  ```

### Finding 123
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 16
- **Confidence**: 0.5308958996633665
- **Code Excerpt**:
  ```
  GITHUB_TOKEN=ghp_9999999999abcdefghijklmnopqrstuvwxyz
  ```

### Finding 124
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 19
- **Confidence**: 0.5670837819570663
- **Code Excerpt**:
  ```
  GOOGLE_OAUTH_TOKEN=ya29.a0AfH6SMBxExampleEnvOAuthToken999
  ```

### Finding 125
- **Rule**: SECRET_HIGH_ENTROPY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 20
- **Confidence**: 0.5518051629618713
- **Code Excerpt**:
  ```
  FACEBOOK_ACCESS_TOKEN=EAACEdEose0cBAExampleEnvFacebookToken999
  ```

### Finding 126
- **Rule**: SECRET_STRIPE_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 13
- **Confidence**: 0.95
- **Code Excerpt**:
  ```
  STRIPE_SECRET_KEY=sk_test_9999999999abcdefghijklmnop
  ```

## Medium Severity Findings

### Finding 1
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 9
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  api_key = "sk_test_1234567890abcdefghijklmnop"
  ```

### Finding 2
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 10
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  secret_key = "my_super_secret_key_12345"
  ```

### Finding 3
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 11
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  stripe_key = "sk_live_1234567890abcdefghijklmnop"
  ```

### Finding 4
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 12
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 5
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 49
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  "google": "ya29.a0AfH6SMBxExampleGoogleOAuthToken",
  ```

### Finding 6
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/app.py`
- **Line**: 50
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  "facebook": "EAACEdEose0cBAExampleFacebookAccessToken",
  ```

### Finding 7
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 9
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  const apiKey = "sk_test_9876543210abcdefghijklmnop";
  ```

### Finding 8
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 11
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  const awsAccessKey = "AKIAJEXAMPLEACCESSKEY";
  ```

### Finding 9
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 33
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  secretKey: 'sk_test_1234567890abcdefghijklmnop',
  ```

### Finding 10
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 34
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  publishableKey: 'pk_test_1234567890abcdefghijklmnop'
  ```

### Finding 11
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 25
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  google: 'ya29.a0AfH6SMBxExampleJavaScriptOAuthToken',
  ```

### Finding 12
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 26
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  facebook: 'EAACEdEose0cBAExampleJavaScriptFacebookToken',
  ```

### Finding 13
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.js`
- **Line**: 38
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  authToken: '1234567890abcdefghijklmnopqrstuvw'
  ```

### Finding 14
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 13
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  "github_token": "ghp_5555555555abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 15
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 21
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  "google": "ya29.a0AfH6SMBxExampleJsonOAuthToken555",
  ```

### Finding 16
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.json`
- **Line**: 22
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  "facebook": "EAACEdEose0cBAExampleJsonFacebookToken555",
  ```

### Finding 17
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 14
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  secret_key: "sk_test_7777777777abcdefghijklmnop"
  ```

### Finding 18
- **Rule**: SECRET_GENERIC_API_KEY
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 15
- **Confidence**: 0.7
- **Code Excerpt**:
  ```
  publishable_key: "pk_test_7777777777abcdefghijklmnop"
  ```

### Finding 19
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 20
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  token: "ghp_7777777777abcdefghijklmnopqrstuvwxyz"
  ```

### Finding 20
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 28
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  google: "ya29.a0AfH6SMBxExampleYamlOAuthToken777"
  ```

### Finding 21
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/config.yaml`
- **Line**: 29
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  facebook: "EAACEdEose0cBAExampleYamlFacebookToken777"
  ```

### Finding 22
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 16
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  GITHUB_TOKEN=ghp_9999999999abcdefghijklmnopqrstuvwxyz
  ```

### Finding 23
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 19
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  GOOGLE_OAUTH_TOKEN=ya29.a0AfH6SMBxExampleEnvOAuthToken999
  ```

### Finding 24
- **Rule**: SECRET_OAUTH_TOKEN
- **File**: `/mnt/c/Users/andre/Desktop/CodeSentinel/sample-project/credentials.env`
- **Line**: 20
- **Confidence**: 0.75
- **Code Excerpt**:
  ```
  FACEBOOK_ACCESS_TOKEN=EAACEdEose0cBAExampleEnvFacebookToken999
  ```

---
*Generated by CodeSentinel*
