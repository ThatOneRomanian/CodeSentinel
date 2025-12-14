"""
Unit tests for AI Output Validation in CodeSentinel Phase 2.

Tests the validation functions and classes that ensure AI-generated
output meets quality and safety standards.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pytest

from sentinel.llm.validation import (
    validate_ai_output,
    validate_cwe_format,
    validate_risk_score,
    validate_references,
    create_fallback_explanation,
    OutputValidator
)


class TestAIValidationFunctions:
    """Test individual AI validation functions."""
    
    def test_validate_ai_output_valid_data(self):
        """Test validate_ai_output with valid data."""
        valid_data = {
            "explanation": "This is a valid security explanation",
            "cwe_id": "CWE-798",
            "remediation": "Fix the issue by doing X, Y, Z",
            "risk_score": 7.5,
            "references": ["https://cwe.mitre.org/data/definitions/798.html"]
        }
        
        assert validate_ai_output(valid_data) is True
    
    def test_validate_ai_output_missing_required_fields(self):
        """Test validate_ai_output with missing required fields."""
        invalid_data = {
            "explanation": "Missing some fields",
            "cwe_id": "CWE-798"
            # Missing remediation, risk_score, references
        }
        
        assert validate_ai_output(invalid_data) is False
    
    def test_validate_ai_output_invalid_types(self):
        """Test validate_ai_output with invalid data types."""
        invalid_data = {
            "explanation": 123,  # Should be string
            "cwe_id": "CWE-798",
            "remediation": "Fix it",
            "risk_score": "high",  # Should be number
            "references": "not a list"
        }
        
        assert validate_ai_output(invalid_data) is False
    
    def test_validate_ai_output_none_values(self):
        """Test validate_ai_output with None values."""
        data_with_none = {
            "explanation": "Valid explanation",
            "cwe_id": None,
            "remediation": None,
            "risk_score": None,
            "references": None
        }
        
        assert validate_ai_output(data_with_none) is True
    
    def test_validate_cwe_format_valid(self):
        """Test validate_cwe_format with valid CWE IDs."""
        valid_cwes = ["CWE-798", "CWE-79", "CWE-200", "CWE-89"]
        
        for cwe in valid_cwes:
            assert validate_cwe_format(cwe) is True
    
    def test_validate_cwe_format_invalid(self):
        """Test validate_cwe_format with invalid CWE IDs."""
        invalid_cwes = [
            "CWE-",           # Missing number
            "CWE-0",          # Zero not allowed
            "CWE-10000",      # Out of range
            "CWE-ABC",        # Non-numeric
            "CWE-79.1",       # Decimal not allowed
            "CWE79",          # Missing dash
            "cwe-798",        # Lowercase
            "",               # Empty string
            None              # None value
        ]
        
        for cwe in invalid_cwes:
            assert validate_cwe_format(cwe) is False
    
    def test_validate_risk_score_valid(self):
        """Test validate_risk_score with valid scores."""
        valid_scores = [1.0, 5.5, 10.0, 7, 3.14159]
        
        for score in valid_scores:
            assert validate_risk_score(score) is True
    
    def test_validate_risk_score_invalid(self):
        """Test validate_risk_score with invalid scores."""
        invalid_scores = [
            0.9,    # Below minimum
            10.1,   # Above maximum
            -1.0,   # Negative
            "5.5",  # String
            None,   # None
            [],     # List
            {}      # Dict
        ]
        
        for score in invalid_scores:
            assert validate_risk_score(score) is False
    
    def test_validate_references_valid(self):
        """Test validate_references with valid reference lists."""
        valid_references = [
            ["https://cwe.mitre.org/data/definitions/798.html"],
            [
                "https://cwe.mitre.org/data/definitions/798.html",
                "https://owasp.org/www-project-top-ten/"
            ],
            []  # Empty list is valid
        ]
        
        for refs in valid_references:
            assert validate_references(refs) is True
    
    def test_validate_references_invalid(self):
        """Test validate_references with invalid reference lists."""
        invalid_references = [
            ["javascript:alert('xss')"],  # Suspicious protocol
            ["<script>alert('xss')</script>"],  # HTML injection
            [123],  # Non-string
            "not a list",  # Not a list
            None  # None
        ]
        
        for refs in invalid_references:
            assert validate_references(refs) is False
    
    def test_create_fallback_explanation(self):
        """Test create_fallback_explanation creates valid fallback."""
        finding_id = "test_rule_1"
        errors = ["Missing explanation field", "Invalid CWE format"]
        
        fallback = create_fallback_explanation(finding_id, errors)
        
        assert isinstance(fallback, dict)
        assert "explanation" in fallback
        assert "cwe_id" in fallback
        assert "remediation" in fallback
        assert "risk_score" in fallback
        assert "references" in fallback
        
        assert finding_id in fallback["explanation"]
        assert "Missing explanation field" in fallback["explanation"]
        assert fallback["cwe_id"] is None
        assert fallback["risk_score"] is None
        assert isinstance(fallback["references"], list)
        assert len(fallback["references"]) > 0


class TestOutputValidator:
    """Test the comprehensive OutputValidator class."""
    
    def test_output_validator_initialization(self):
        """Test OutputValidator initialization."""
        validator = OutputValidator(enable_fallback=True)
        assert validator.enable_fallback is True
        
        validator_no_fallback = OutputValidator(enable_fallback=False)
        assert validator_no_fallback.enable_fallback is False
    
    def test_validate_and_fix_valid_data(self):
        """Test validate_and_fix with valid data."""
        validator = OutputValidator()
        valid_data = {
            "explanation": "Valid explanation",
            "cwe_id": "CWE-798",
            "remediation": "Fix it",
            "risk_score": 7.5,
            "references": ["https://cwe.mitre.org/data/definitions/798.html"]
        }
        
        result = validator.validate_and_fix(valid_data, "test_rule_1")
        
        # Should return the original data unchanged
        assert result == valid_data
    
    def test_validate_and_fix_invalid_data_with_fallback(self):
        """Test validate_and_fix with invalid data and fallback enabled."""
        validator = OutputValidator(enable_fallback=True)
        invalid_data = {
            "explanation": "Missing fields",
            # Missing other required fields
        }
        
        result = validator.validate_and_fix(invalid_data, "test_rule_1")
        
        # Should return fallback explanation
        assert "explanation" in result
        assert "test_rule_1" in result["explanation"]
        assert result["cwe_id"] is None
        assert result["risk_score"] is None
    
    def test_validate_and_fix_invalid_data_without_fallback(self):
        """Test validate_and_fix with invalid data and fallback disabled."""
        validator = OutputValidator(enable_fallback=False)
        invalid_data = {
            "explanation": "Missing fields",
            # Missing other required fields
        }
        
        result = validator.validate_and_fix(invalid_data, "test_rule_1")
        
        # Should return minimal safe data
        assert "explanation" in result
        assert "test_rule_1" in result["explanation"]
        assert result["cwe_id"] is None
        assert result["remediation"] is None
        assert result["risk_score"] is None
        assert result["references"] == []
    
    def test_get_validation_errors_detects_all_issues(self):
        """Test _get_validation_errors detects multiple validation issues."""
        validator = OutputValidator()
        invalid_data = {
            "explanation": 123,  # Wrong type
            "cwe_id": "INVALID",  # Invalid format
            "remediation": "Valid remediation",
            "risk_score": 15.0,  # Out of range
            "references": "not a list"  # Wrong type
        }
        
        errors = validator._get_validation_errors(invalid_data)
        
        assert len(errors) >= 4  # Should have multiple errors
        assert any("explanation" in error.lower() for error in errors)
        assert any("cwe" in error.lower() for error in errors)
        assert any("risk score" in error.lower() for error in errors)
        assert any("references" in error.lower() for error in errors)
    
    def test_get_validation_errors_empty_dict(self):
        """Test _get_validation_errors with empty dictionary."""
        validator = OutputValidator()
        errors = validator._get_validation_errors({})
        
        assert len(errors) == 5  # All required fields missing
        assert all("missing required field" in error.lower() for error in errors)
    
    def test_get_validation_errors_non_dict(self):
        """Test _get_validation_errors with non-dictionary input."""
        validator = OutputValidator()
        errors = validator._get_validation_errors("not a dict")
        
        assert errors == ["Data must be a dictionary"]


if __name__ == "__main__":
    pytest.main([__file__])