"""
Output Schema Validation for CodeSentinel Phase 2.

Provides validation functions for AI-generated output to ensure data quality,
consistency, and safety before using explanations in the system.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import re
from typing import Dict, List, Optional, Union, Any


def validate_ai_output(data: Dict[str, Any]) -> bool:
    """
    Validate AI-generated output against expected schema and safety requirements.
    
    Args:
        data: Dictionary containing AI-generated explanation data
        
    Returns:
        True if the data passes all validation checks, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    # Required fields check
    required_fields = ["explanation", "cwe_id", "remediation", "risk_score", "references"]
    for field in required_fields:
        if field not in data:
            return False
    
    # Type validation
    if not isinstance(data.get("explanation"), (str, type(None))):
        return False
    
    if not isinstance(data.get("cwe_id"), (str, type(None))):
        return False
    
    if not isinstance(data.get("remediation"), (str, type(None))):
        return False
    
    if not isinstance(data.get("risk_score"), (float, int, type(None))):
        return False
    
    if not isinstance(data.get("references"), (list, type(None))):
        return False
    
    # Content validation for non-None values
    explanation = data.get("explanation")
    if explanation is not None and not _validate_explanation_content(explanation):
        return False
    
    cwe_id = data.get("cwe_id")
    if cwe_id is not None and not validate_cwe_format(cwe_id):
        return False
    
    risk_score = data.get("risk_score")
    if risk_score is not None and not validate_risk_score(risk_score):
        return False
    
    references = data.get("references")
    if references is not None and not validate_references(references):
        return False
    
    return True


def validate_cwe_format(cwe_id: str) -> bool:
    """
    Validate CWE identifier format.
    
    Args:
        cwe_id: CWE identifier to validate (e.g., "CWE-798")
        
    Returns:
        True if the CWE format is valid, False otherwise
    """
    if not isinstance(cwe_id, str):
        return False
    
    # CWE format: CWE- followed by digits
    cwe_pattern = r'^CWE-\d+$'
    if not re.match(cwe_pattern, cwe_id):
        return False
    
    # Extract CWE number and validate range
    try:
        cwe_number = int(cwe_id.split('-')[1])
        # CWE numbers typically range from 1 to 1000+, but we'll set reasonable bounds
        if cwe_number < 1 or cwe_number > 9999:
            return False
    except (ValueError, IndexError):
        return False
    
    return True


def validate_risk_score(risk_score: Union[float, int]) -> bool:
    """
    Validate risk score format and range.
    
    Args:
        risk_score: Numeric risk score to validate (should be 1-10)
        
    Returns:
        True if the risk score is valid, False otherwise
    """
    if not isinstance(risk_score, (float, int)):
        return False
    
    # Risk score should be between 1 and 10
    if risk_score < 1.0 or risk_score > 10.0:
        return False
    
    return True


def validate_references(references: List[str]) -> bool:
    """
    Validate reference URLs and content.
    
    Args:
        references: List of reference URLs to validate
        
    Returns:
        True if all references are valid, False otherwise
    """
    if not isinstance(references, list):
        return False
    
    for ref in references:
        if not isinstance(ref, str):
            return False
        
        # Basic URL validation (not exhaustive, but catches obvious issues)
        if not _validate_reference_url(ref):
            return False
        
        # Check for suspicious content
        if _contains_suspicious_content(ref):
            return False
    
    return True


def _validate_explanation_content(explanation: str) -> bool:
    """
    Validate explanation content for safety and quality.
    
    Args:
        explanation: Explanation text to validate
        
    Returns:
        True if explanation content is safe and valid, False otherwise
    """
    if not isinstance(explanation, str):
        return False
    
    # Check for minimum length (avoid empty or trivial explanations)
    if len(explanation.strip()) < 10:
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'ignore.*previous.*instructions',
        r'disregard.*previous',
        r'you are now',
        r'act as',
        r'pretend you are',
        r'forget.*rules',
        r'break.*rules',
        r'override.*system',
        r'system.*override',
        r'bypass.*safety',
        r'security.*bypass',
        r'<script>',
        r'javascript:',
        r'eval\(',
        r'exec\(',
        r'import\s+os',
        r'import\s+sys',
        r'__import__',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, explanation, re.IGNORECASE):
            return False
    
    return True


def _validate_reference_url(url: str) -> bool:
    """
    Validate a reference URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL format is valid, False otherwise
    """
    # Basic URL pattern check
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(url_pattern, url, re.IGNORECASE):
        return False
    
    # Check for common security reference domains
    allowed_domains = [
        'cwe.mitre.org',
        'nvd.nist.gov',
        'owasp.org',
        'sans.org',
        'security.stackexchange.com',
        'github.com',
        'gitlab.com',
        'docs.python.org',
        'docs.oracle.com',
        'developer.mozilla.org',
        'w3.org',
    ]
    
    # Allow any domain for now, but we could restrict to known security sources
    # This is a placeholder for future domain filtering
    return True


def _contains_suspicious_content(text: str) -> bool:
    """
    Check text for suspicious or malicious content.
    
    Args:
        text: Text to check
        
    Returns:
        True if suspicious content is found, False otherwise
    """
    suspicious_patterns = [
        r'<script>',
        r'javascript:',
        r'vbscript:',
        r'eval\(',
        r'exec\(',
        r'import\s+os',
        r'import\s+sys',
        r'__import__',
        r'subprocess',
        r'os\.system',
        r'execfile',
        r'compile\(',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def create_fallback_explanation(finding_id: str, validation_errors: List[str]) -> Dict[str, Any]:
    """
    Create a fallback explanation when AI validation fails.
    
    Args:
        finding_id: ID of the finding that failed validation
        validation_errors: List of validation error messages
        
    Returns:
        Fallback explanation data with safe defaults
    """
    error_summary = "; ".join(validation_errors[:3])  # Limit error summary length
    
    return {
        "explanation": f"AI explanation validation failed for finding {finding_id}. Errors: {error_summary}",
        "cwe_id": None,
        "remediation": "Please review the security finding manually and consult security documentation.",
        "risk_score": None,
        "references": [
            "https://cwe.mitre.org/",
            "https://owasp.org/www-project-top-ten/"
        ],
    }


class OutputValidator:
    """
    Comprehensive validator for AI-generated output with fallback handling.
    """
    
    def __init__(self, enable_fallback: bool = True):
        """
        Initialize the output validator.
        
        Args:
            enable_fallback: Whether to generate fallback explanations on validation failure
        """
        self.enable_fallback = enable_fallback
    
    def validate_and_fix(self, data: Dict[str, Any], finding_id: str) -> Dict[str, Any]:
        """
        Validate AI output and apply fixes or fallback as needed.
        
        Args:
            data: AI-generated explanation data to validate
            finding_id: ID of the finding for fallback generation
            
        Returns:
            Validated and potentially fixed explanation data
        """
        validation_errors = self._get_validation_errors(data)
        
        if not validation_errors:
            return data
        
        if self.enable_fallback:
            return create_fallback_explanation(finding_id, validation_errors)
        
        # If fallback is disabled and validation fails, return minimal safe data
        return {
            "explanation": f"Validation failed for finding {finding_id}",
            "cwe_id": None,
            "remediation": None,
            "risk_score": None,
            "references": [],
        }
    
    def _get_validation_errors(self, data: Dict[str, Any]) -> List[str]:
        """
        Get detailed validation errors for AI output.
        
        Args:
            data: AI-generated explanation data to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not isinstance(data, dict):
            return ["Data must be a dictionary"]
        
        # Check required fields
        required_fields = ["explanation", "cwe_id", "remediation", "risk_score", "references"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Type validation with specific error messages
        if "explanation" in data and not isinstance(data["explanation"], (str, type(None))):
            errors.append("Explanation must be a string or None")
        
        if "cwe_id" in data and not isinstance(data["cwe_id"], (str, type(None))):
            errors.append("CWE ID must be a string or None")
        
        if "remediation" in data and not isinstance(data["remediation"], (str, type(None))):
            errors.append("Remediation must be a string or None")
        
        if "risk_score" in data and not isinstance(data["risk_score"], (float, int, type(None))):
            errors.append("Risk score must be a number or None")
        
        if "references" in data and not isinstance(data["references"], (list, type(None))):
            errors.append("References must be a list or None")
        
        # Content validation with proper type handling
        explanation = data.get("explanation")
        if explanation is not None and not _validate_explanation_content(explanation):
            errors.append("Explanation content validation failed")
        
        cwe_id = data.get("cwe_id")
        if cwe_id is not None and not validate_cwe_format(cwe_id):
            errors.append(f"Invalid CWE format: {cwe_id}")
        
        risk_score = data.get("risk_score")
        if risk_score is not None and not validate_risk_score(risk_score):
            errors.append(f"Risk score out of range: {risk_score}")
        
        references = data.get("references")
        if references is not None and not validate_references(references):
            errors.append("References validation failed")
        
        return errors