"""
Explanation Engine for CodeSentinel Phase 2 AI Explainer Mode.

Provides AI-powered security explanations, CWE mapping, and remediation guidance
without modifying the core scanning logic.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pathlib
from typing import Dict, List, Optional, Union

from sentinel.rules.base import Finding
from sentinel.llm.provider import LLMProvider
from sentinel.llm.safety import SafetyLayer, sanitize_input, filter_sensitive_data, truncate_excerpt
from sentinel.llm.validation import OutputValidator, create_fallback_explanation


class ExplanationEngine:
    """
    Engine for generating AI-powered security explanations.
    
    During Phase 2, this uses real LLM integration when configured,
    with graceful fallbacks to placeholder data.
    """
    
    def __init__(self, prompts_dir: Optional[pathlib.Path] = None):
        """
        Initialize the explanation engine.
        
        Args:
            prompts_dir: Directory containing prompt templates. If None, uses default.
        """
        if prompts_dir is None:
            prompts_dir = pathlib.Path(__file__).parent / "prompts"
        self.prompts_dir = prompts_dir
        self.safety_layer = SafetyLayer(max_excerpt_length=500, enable_filtering=True)
        self.validator = OutputValidator()
    
    def _load_prompt_template(self, template_name: str) -> str:
        """
        Load a prompt template from the prompts directory.
        
        Args:
            template_name: Name of the template file (without .txt extension)
            
        Returns:
            The template content as a string
            
        Raises:
            FileNotFoundError: If the template file doesn't exist
        """
        template_path = self.prompts_dir / f"{template_name}.txt"
        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")
        
        return template_path.read_text(encoding="utf-8")
    
    def _populate_template(self, template: str, finding: Finding) -> str:
        """
        Populate a template with finding data.
        
        Args:
            template: The template string with {{variable}} placeholders
            finding: The finding to extract data from
            
        Returns:
            The populated template string
        """
        # Convert file_path to string for template
        file_path_str = str(finding.file_path)
        
        # Get language if available, otherwise "unknown"
        language = getattr(finding, 'language', 'unknown') or 'unknown'
        
        # Get category if available, otherwise "unknown"
        category = getattr(finding, 'category', 'unknown') or 'unknown'
        
        # Get tags if available, otherwise empty list
        tags = getattr(finding, 'tags', []) or []
        tags_str = ', '.join(tags) if tags else 'none'
        
        # Handle optional excerpt field and apply safety processing
        excerpt = finding.excerpt or "No excerpt available"
        safe_excerpt = self.safety_layer.process_for_ai(excerpt)
        
        # Replace template variables
        populated = template.replace("{{rule_id}}", finding.rule_id)
        populated = populated.replace("{{severity}}", finding.severity)
        populated = populated.replace("{{file_path}}", file_path_str)
        populated = populated.replace("{{line}}", str(finding.line))
        populated = populated.replace("{{excerpt}}", safe_excerpt)
        populated = populated.replace("{{language}}", language)
        populated = populated.replace("{{category}}", category)
        populated = populated.replace("{{tags}}", tags_str)
        
        return populated
    
    def _validate_environment_safety(self) -> bool:
        """
        Validate that the environment is safe for AI operations.
        
        Returns:
            True if environment is safe, False otherwise
        """
        return self.safety_layer.validate_environment()
    
    def _is_provider_configured(self, provider: LLMProvider) -> bool:
        """
        Check if the provider is properly configured for real API calls.
        
        Args:
            provider: The LLM provider instance
            
        Returns:
            True if provider is configured for real API calls, False otherwise
        """
        # For DeepSeekProvider, check if it has the _is_configured method and it returns True
        if hasattr(provider, '_is_configured'):
            return provider._is_configured()
        
        # For other providers, we'll assume they're configured if they're not returning placeholders
        # This is a heuristic - we'll check if the response contains "placeholder"
        test_response = provider.generate("test")
        return "placeholder" not in test_response.lower()
    
    def explain_finding(self, finding: Finding, provider: LLMProvider) -> Dict[str, Union[str, None, float, List[str]]]:
        """
        Generate AI-powered explanation for a security finding.
        
        Uses real LLM integration when provider is configured, otherwise
        falls back to placeholder data.
        
        Args:
            finding: The security finding to explain
            provider: The LLM provider to use for generation
            
        Returns:
            Dictionary with explanation fields:
            - "explanation": Security risk explanation
            - "cwe_id": CWE identifier (if applicable)
            - "remediation": Fix instructions
            - "risk_score": Numeric risk score (1-10)
            - "references": List of reference URLs
        """
        # Validate environment safety first
        if not self._validate_environment_safety():
            return {
                "explanation": "Safety check failed: Environment contains private keys. AI explanation disabled.",
                "cwe_id": None,
                "remediation": None,
                "risk_score": None,
                "references": [],
            }
        
        # Check if provider is configured for real API calls
        if self._is_provider_configured(provider):
            try:
                # Use template-based approach with real LLM
                return self.explain_finding_with_templates(finding, provider)
            except Exception as e:
                # Fall back to placeholder if real LLM fails
                print(f"Warning: Real LLM explanation failed, using fallback: {e}")
                return self._get_placeholder_explanation(finding)
        else:
            # Provider not configured, use placeholder
            return self._get_placeholder_explanation(finding)
    
    def _get_placeholder_explanation(self, finding: Finding) -> Dict[str, Union[str, None, float, List[str]]]:
        """
        Generate placeholder explanation for when LLM is not configured.
        
        Args:
            finding: The security finding to explain
            
        Returns:
            Dictionary with placeholder explanation fields
        """
        # Create more realistic placeholder data that includes finding context
        explanation = f"[PLACEHOLDER] Security finding detected: {finding.rule_id} with {finding.severity} severity. "
        explanation += f"Found in {finding.file_path} at line {finding.line}. "
        if finding.excerpt:
            safe_excerpt = self.safety_layer.process_for_ai(finding.excerpt)
            explanation += f"Context: {safe_excerpt[:100]}..."
        
        remediation = f"[PLACEHOLDER] Review the {finding.rule_id} finding in {finding.file_path}. "
        remediation += "Consult security documentation for appropriate remediation steps."
        
        # Assign risk score based on severity for placeholder
        severity_scores = {"low": 3.0, "medium": 5.5, "high": 7.5, "critical": 9.0}
        risk_score = severity_scores.get(finding.severity.lower(), 5.0)
        
        return {
            "explanation": explanation,
            "cwe_id": None,  # Will be populated with actual CWE mapping in Phase 2
            "remediation": remediation,
            "risk_score": risk_score,
            "references": [
                "https://cwe.mitre.org/",
                "https://owasp.org/www-project-top-ten/"
            ],
        }
    
    def explain_finding_with_templates(self, finding: Finding, provider: LLMProvider) -> Dict[str, Union[str, None, float, List[str]]]:
        """
        Generate AI-powered explanation using prompt templates and real LLM.
        
        This uses actual LLM API calls when the provider is properly configured.
        
        Args:
            finding: The security finding to explain
            provider: The LLM provider to use for generation
            
        Returns:
            Dictionary with explanation fields (same as explain_finding)
        """
        # Validate environment safety first
        if not self._validate_environment_safety():
            return {
                "explanation": "Safety check failed: Environment contains private keys. AI explanation disabled.",
                "cwe_id": None,
                "remediation": None,
                "risk_score": None,
                "references": [],
            }
        
        # Load templates
        try:
            explanation_template = self._load_prompt_template("explanation")
            remediation_template = self._load_prompt_template("remediation")
            cwe_template = self._load_prompt_template("cwe_mapping")
            severity_template = self._load_prompt_template("severity_justification")
        except FileNotFoundError:
            # Fallback if templates aren't available
            return self._get_placeholder_explanation(finding)
        
        # Populate templates
        explanation_prompt = self._populate_template(explanation_template, finding)
        remediation_prompt = self._populate_template(remediation_template, finding)
        cwe_prompt = self._populate_template(cwe_template, finding)
        severity_prompt = self._populate_template(severity_template, finding)
        
        try:
            # Use real LLM calls
            explanation = provider.generate(explanation_prompt)
            remediation = provider.generate(remediation_prompt)
            cwe_response = provider.generate(cwe_prompt)
            severity_response = provider.generate(severity_prompt)
            
            # Parse CWE ID from response (simple extraction)
            cwe_id = None
            if "CWE-" in cwe_response:
                import re
                cwe_match = re.search(r'CWE-(\d+)', cwe_response)
                if cwe_match:
                    cwe_id = f"CWE-{cwe_match.group(1)}"
            
            # Parse risk score from response (simple extraction)
            risk_score = None
            try:
                # Try to extract a number between 1-10
                import re
                score_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:out of\s*10|/10|score)', severity_response, re.IGNORECASE)
                if score_match:
                    risk_score = float(score_match.group(1))
                    # Ensure it's within reasonable bounds
                    if risk_score < 1:
                        risk_score = 1.0
                    elif risk_score > 10:
                        risk_score = 10.0
            except (ValueError, TypeError):
                pass
            
            # If risk_score is still None, use severity-based fallback
            if risk_score is None:
                severity_scores = {"low": 3.0, "medium": 5.5, "high": 7.5, "critical": 9.0}
                risk_score = severity_scores.get(finding.severity.lower(), 5.0)
            
            # Create structured response
            response_data = {
                "explanation": explanation,
                "cwe_id": cwe_id,
                "remediation": remediation,
                "risk_score": risk_score,
                "references": [
                    "https://cwe.mitre.org/",
                    "https://owasp.org/www-project-top-ten/"
                ],
            }
            
            # Validate and fix the response - use rule_id as finding_id
            validated_data = self.validator.validate_and_fix(response_data, finding.rule_id)
            
            return validated_data
            
        except Exception as e:
            # If LLM calls fail, return fallback explanation
            print(f"Warning: LLM template processing failed: {e}")
            return create_fallback_explanation(finding.rule_id, [str(e)])
    
    def explain_batch(self, findings: List[Finding], provider: LLMProvider) -> Dict[str, Dict[str, Union[str, None, float, List[str]]]]:
        """
        Generate explanations for multiple findings in batch.
        
        Groups findings by rule_id and generates one explanation per rule type
        to minimize LLM API calls.
        
        Args:
            findings: List of security findings to explain
            provider: The LLM provider to use for generation
            
        Returns:
            Dictionary mapping rule_id to explanation data
        """
        # Validate environment safety first
        if not self._validate_environment_safety():
            return {
                finding.rule_id: {
                    "explanation": "Safety check failed: Environment contains private keys. AI explanation disabled.",
                    "cwe_id": None,
                    "remediation": None,
                    "risk_score": None,
                    "references": [],
                }
                for finding in findings
            }
        
        # Group findings by rule_id
        findings_by_rule: Dict[str, List[Finding]] = {}
        for finding in findings:
            if finding.rule_id not in findings_by_rule:
                findings_by_rule[finding.rule_id] = []
            findings_by_rule[finding.rule_id].append(finding)
        
        # Generate one explanation per rule type
        explanations = {}
        for rule_id, rule_findings in findings_by_rule.items():
            if rule_findings:
                # Use the first finding as representative for the batch
                representative_finding = rule_findings[0]
                explanation_data = self.explain_finding(representative_finding, provider)
                
                # Enhance the explanation to indicate it's a batch explanation
                if len(rule_findings) > 1:
                    # Safely handle string concatenation with type checking
                    if isinstance(explanation_data["explanation"], str):
                        explanation_data["explanation"] = f"[Batch explanation for {len(rule_findings)} findings] " + explanation_data["explanation"]
                    if isinstance(explanation_data["remediation"], str):
                        explanation_data["remediation"] = f"[Applies to {len(rule_findings)} instances] " + explanation_data["remediation"]
                
                explanations[rule_id] = explanation_data
        
        return explanations