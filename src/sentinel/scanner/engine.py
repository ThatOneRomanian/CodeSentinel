"""
Rule engine for CodeSentinel.

Dynamically loads and executes security rules against text files, returning
normalized finding objects according to the Phase 1 specification.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import importlib
import inspect
import pathlib
import sys
from typing import List, Optional, Protocol, Type, Any, Dict, Tuple
import logging

from sentinel.rules.base import Finding, Rule
from sentinel.rules.token_types import TokenType, classify_token


logger = logging.getLogger(__name__)


class RuleLoader:
    """
    Discovers and loads rule modules from the rules directory.

    Handles dynamic discovery of rule modules, collects all Rule objects
    exported by those modules, and manages import errors gracefully.
    """

    def __init__(self, rules_directory: pathlib.Path):
        """
        Initialize the rule loader.

        Args:
            rules_directory: Path to the directory containing rule modules
        """
        self.rules_directory = rules_directory
        self._loaded_rules: List[Rule] = []

    def load_rules(self) -> List[Rule]:
        """
        Discover and load all available rule modules.

        Returns:
            List of loaded Rule objects

        Raises:
            FileNotFoundError: If rules directory doesn't exist
            PermissionError: If rules directory cannot be accessed
        """
        if not self.rules_directory.exists():
            raise FileNotFoundError(f"Rules directory not found: {self.rules_directory}")

        if not self.rules_directory.is_dir():
            raise ValueError(f"Rules path is not a directory: {self.rules_directory}")

        self._loaded_rules.clear()

        # Add rules directory to Python path for dynamic imports
        rules_parent = self.rules_directory.parent
        if str(rules_parent) not in sys.path:
            sys.path.insert(0, str(rules_parent))

        # Discover and import rule modules
        for file_path in self.rules_directory.glob("*.py"):
            if file_path.name.startswith("__") or file_path.name == "base.py":
                continue  # Skip __init__.py and base.py

            module_name = file_path.stem
            self._load_rule_module(module_name)

        # Also check rule pack subdirectories
        for subdir in self.rules_directory.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("__"):
                self._load_rule_pack(subdir)

        logger.info(f"Successfully loaded {len(self._loaded_rules)} rules from {len(list(self.rules_directory.glob('*.py')))} modules")
        return self._loaded_rules.copy()

    def _load_rule_module(self, module_name: str) -> None:
        """
        Load a single rule module and extract Rule objects.

        Args:
            module_name: Name of the module to load (without .py extension)
        """
        # Use importlib.util to load module from file path directly
        import importlib.util

        file_path = self.rules_directory / f"{module_name}.py"

        try:
            # Load module from file path
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                logger.error(f"Failed to create spec for module: {module_name}")
                return

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # First, try to load from consolidated 'rules' list
            if hasattr(module, 'rules') and isinstance(module.rules, list):
                rules_loaded = 0
                for rule_instance in module.rules:
                    if self._is_valid_rule(rule_instance):
                        self._loaded_rules.append(rule_instance)
                        rules_loaded += 1
                        logger.debug(f"Loaded rule from rules list: {rule_instance.id}")
                    else:
                        logger.warning(f"Invalid rule instance in {module_name}.rules: {rule_instance}")
                
                if rules_loaded > 0:
                    logger.info(f"Loaded {rules_loaded} rules from {module_name}.rules")
                else:
                    logger.warning(f"No valid rules found in {module_name}.rules list")
                return

            # Fallback: Find all Rule objects in the module (legacy support)
            logger.warning(f"Module {module_name} does not export 'rules' list, using legacy class discovery")
            legacy_rules_loaded = 0
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    self._is_rule_class(obj) and
                    not name.startswith('_')):
                    try:
                        rule_instance = obj()
                        if self._is_valid_rule(rule_instance):
                            self._loaded_rules.append(rule_instance)
                            legacy_rules_loaded += 1
                            logger.debug(f"Loaded rule (legacy): {rule_instance.id}")
                        else:
                            logger.warning(f"Rule validation failed for {name}: missing required attributes or methods")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate rule {name}: {e}")
            
            if legacy_rules_loaded > 0:
                logger.info(f"Loaded {legacy_rules_loaded} rules from {module_name} (legacy mode)")
            else:
                logger.warning(f"No valid rules found in {module_name} using legacy discovery")

        except Exception as e:
            logger.error(f"Failed to load rule module {module_name}: {e}")

    def _load_rule_pack(self, pack_directory: pathlib.Path) -> None:
        """
        Load rules from a rule pack subdirectory.

        Args:
            pack_directory: Path to rule pack directory
        """
        # Check if this is a scaffold directory (empty or only has README)
        py_files = list(pack_directory.glob("*.py"))
        if len(py_files) == 0:
            logger.debug(f"Skipping empty rule pack: {pack_directory.name}")
            return

        # Load __init__.py from rule pack
        init_file = pack_directory / "__init__.py"
        if init_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(pack_directory.name, init_file)
                if spec is None or spec.loader is None:
                    logger.error(f"Failed to create spec for rule pack: {pack_directory.name}")
                    return

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Load from consolidated 'rules' list
                if hasattr(module, 'rules') and isinstance(module.rules, list):
                    rules_loaded = 0
                    for rule_instance in module.rules:
                        if self._is_valid_rule(rule_instance):
                            self._loaded_rules.append(rule_instance)
                            rules_loaded += 1
                            logger.debug(f"Loaded rule from pack {pack_directory.name}: {rule_instance.id}")
                    
                    if rules_loaded > 0:
                        logger.info(f"Loaded {rules_loaded} rules from rule pack: {pack_directory.name}")
                    else:
                        logger.warning(f"No valid rules found in rule pack: {pack_directory.name}")
                else:
                    logger.warning(f"Rule pack {pack_directory.name} does not export 'rules' list")

            except Exception as e:
                logger.error(f"Failed to load rule pack {pack_directory.name}: {e}")

    def _is_rule_class(self, obj: Type[Any]) -> bool:
        """
        Check if a class appears to be a Rule implementation.

        Args:
            obj: Class to check

        Returns:
            True if class appears to implement Rule protocol
        """
        # Check if class has the apply method (which should be on the class)
        # The other attributes (id, description, severity) may be set in __init__
        return (hasattr(obj, 'apply') and 
                inspect.isfunction(getattr(obj, 'apply')))

    def _is_valid_rule(self, rule_instance: Any) -> bool:
        """
        Validate that an object fully implements the Rule protocol.

        Args:
            rule_instance: Object to validate

        Returns:
            True if object is a valid Rule implementation
        """
        required_attrs = ['id', 'description', 'severity', 'precedence'] # Added 'precedence'
        required_methods = ['apply']

        # Check for abstract classes and protocols
        if inspect.isabstract(rule_instance):
            logger.warning(f"Skipping abstract class: {rule_instance}")
            return False

        # Check if it's the Rule protocol itself
        if hasattr(rule_instance, '__name__') and rule_instance.__name__ == 'Rule':
            logger.warning(f"Skipping Rule protocol: {rule_instance}")
            return False

        # Check if the instance inherits from the Rule protocol
        # This prevents classes that directly inherit from Rule protocol from being instantiated
        rule_class = type(rule_instance)
        if hasattr(rule_class, '__bases__'):
            for base in rule_class.__bases__:
                if hasattr(base, '__name__') and base.__name__ == 'Rule':
                    logger.warning(f"Skipping class that inherits from Rule protocol: {rule_instance}")
                    return False

        for attr in required_attrs:
            if not hasattr(rule_instance, attr):
                logger.warning(f"Rule missing required attribute '{attr}': {rule_instance}")
                return False

        for method in required_methods:
            if not (hasattr(rule_instance, method) and callable(getattr(rule_instance, method))):
                logger.warning(f"Rule missing required method '{method}': {rule_instance}")
                return False

        # Additional validation: ensure attributes have non-empty values
        if not rule_instance.id or not isinstance(rule_instance.id, str):
            logger.warning(f"Rule has invalid id: {rule_instance}")
            return False

        if not rule_instance.description or not isinstance(rule_instance.description, str):
            logger.warning(f"Rule has invalid description: {rule_instance}")
            return False

        if not rule_instance.severity or not isinstance(rule_instance.severity, str):
            logger.warning(f"Rule has invalid severity: {rule_instance}")
            return False
            
        # Validate precedence is an integer (Phase 2.7 addition)
        if not isinstance(rule_instance.precedence, int) or not (1 <= rule_instance.precedence <= 100):
            logger.warning(f"Rule has invalid precedence value '{rule_instance.precedence}': {rule_instance}")
            return False

        # Validate severity is one of the expected values
        valid_severities = ['critical', 'high', 'medium', 'low', 'info']
        if rule_instance.severity.lower() not in valid_severities:
            logger.warning(f"Rule has invalid severity value '{rule_instance.severity}': {rule_instance}")
            return False

        return True


def _get_rule_precedence(finding: Finding) -> int:
    """
    Determine precedence score for a finding based on rule type and token classification.
    
    Higher precedence values take priority during deduplication.
    """
    # Check if precedence is explicitly set on the finding (Phase 2.7 addition)
    if finding.rule_precedence is not None:
        return finding.rule_precedence
        
    # Fallback to logic used before explicit precedence fields were mandatory
    
    # Extract token from excerpt for classification
    excerpt = finding.excerpt or ""
    token = _extract_token_from_excerpt(excerpt)
    token_type = classify_token(token) if token else None
    
    # Provider-specific rules have highest precedence
    provider_specific_rules = {
        'SECRET_AWS_ACCESS_KEY', 'SECRET_AWS_SECRET_KEY', 'SECRET_GCP_SERVICE_ACCOUNT',
        'SECRET_AZURE_CLIENT_SECRET', 'SECRET_STRIPE_API_KEY', 'SECRET_JWT',
        'SECRET_PRIVATE_KEY', 'SECRET_SLACK_BOT_TOKEN', 'SECRET_SLACK_USER_TOKEN',
        'SECRET_GITHUB_TOKEN', 'SECRET_FACEBOOK_ACCESS_TOKEN'
    }
    
    if finding.rule_id in provider_specific_rules:
        return 100  # Highest precedence for provider-specific
    
    # OAuth tokens and hardcoded passwords
    if finding.rule_id in {'SECRET_OAUTH_TOKEN', 'SECRET_HARDCODED_PASSWORD'}:
        return 90
    
    # Generic API keys
    if finding.rule_id in {'SECRET_GENERIC_API_KEY', 'hardcoded-api-key'}:
        return 80
    
    # High entropy strings (lowest precedence for secrets)
    if finding.rule_id == 'SECRET_HIGH_ENTROPY':
        return 70
        
    # Specialized Misconfiguration rules (Phase 2.7) - We hardcode this here 
    # to maintain backward compatibility for Phase 2.5 core rules (60)
    # Since Phase 2.7 rules explicitly set precedence=65, this branch is mainly for Phase 2.5
    # config rules which do not have the 'precedence' attribute on the finding.
    
    # Configuration rules (separate category, Phase 2.5 era)
    config_rules = {
        'insecure-bind', 'debug-enabled', 'weak-crypto', 'exposed-env-vars',
        'insecure-literals', 'development-settings', 'tls-issues', 'hardcoded-database'
    }
    if finding.rule_id in config_rules:
        return 60
    
    # Default precedence for unknown rules
    return 50


def _extract_token_from_excerpt(excerpt: str) -> Optional[str]:
    """
    Extract potential token value from excerpt for classification.
    """
    if not excerpt:
        return None
        
    # Look for common assignment patterns
    patterns = [
        r'[\'"]([A-Za-z0-9+/=\-_\.]{16,})[\'"]',  # Quoted strings
        r'=\s*([A-Za-z0-9+/=\-_\.]{16,})\s*',     # Assignment without quotes
        r':\s*[\'"]([A-Za-z0-9+/=\-_\.]{16,})[\'"]',  # YAML-style
    ]
    
    import re
    for pattern in patterns:
        match = re.search(pattern, excerpt)
        if match:
            return match.group(1)
    
    # Fallback: look for any long alphanumeric string
    long_strings = re.findall(r'\b[A-Za-z0-9+/=\-_\.]{16,}\b', excerpt)
    if long_strings:
        return long_strings[0]
    
    return None


def _get_finding_group_key(finding: Finding) -> Tuple[str, int, str]:
    """
    Create a grouping key for findings based on file, line, and overlapping excerpt.
    """
    # Normalize file path to string for consistent comparison
    file_path = str(finding.file_path)
    
    # Use 0 as placeholder for None line numbers
    line_number = finding.line or 0
    
    # Normalize excerpt by removing extra whitespace, use empty string for None
    excerpt = finding.excerpt or ""
    normalized_excerpt = ' '.join(excerpt.strip().split())
    
    return (file_path, line_number, normalized_excerpt)


def _deduplicate_findings(findings: List[Finding]) -> List[Finding]:
    """
    Deduplicate findings by keeping only the highest-precedence finding per group.
    """
    if not findings:
        return []
    
    # Group findings by file/line/excerpt
    grouped_findings: Dict[Tuple[str, int, str], List[Finding]] = {}
    
    for finding in findings:
        group_key = _get_finding_group_key(finding)
        if group_key not in grouped_findings:
            grouped_findings[group_key] = []
        grouped_findings[group_key].append(finding)
    
    # For each group, keep only the highest-precedence finding
    deduplicated = []
    
    for group_key, group_findings in grouped_findings.items():
        if len(group_findings) == 1:
            # No duplicates in this group
            deduplicated.append(group_findings[0])
        else:
            # Multiple findings for same location - apply precedence rules
            best_finding = _select_best_finding(group_findings)
            deduplicated.append(best_finding)
            
            # Log deduplication for debugging
            if len(group_findings) > 1:
                logger.debug(
                    f"Deduplicated {len(group_findings)} findings for {group_key[0]}:{group_key[1]} "
                    f"-> keeping {best_finding.rule_id} (precedence: {_get_rule_precedence(best_finding)})"
                )
    
    logger.info(f"Deduplication reduced {len(findings)} findings to {len(deduplicated)} unique findings")
    return deduplicated


def _select_best_finding(findings: List[Finding]) -> Finding:
    """
    Select the best finding from a group of duplicates based on precedence rules.
    """
    if len(findings) == 1:
        return findings[0]
    
    # Sort by precedence, then confidence, then rule_id for deterministic selection
    sorted_findings = sorted(
        findings,
        key=lambda f: (
            _get_rule_precedence(f),  # Higher precedence first
            f.confidence or 0.0,      # Higher confidence first  
            f.rule_id                 # Alphabetical for tie-breaking
        ),
        reverse=True
    )
    
    return sorted_findings[0]


def run_rules(files: List[pathlib.Path]) -> List[Finding]:
    """
    Main function to run all loaded rules against a list of files.
    """
    # Initialize rule loader with rules directory
    rules_dir = pathlib.Path(__file__).parent.parent / "rules"
    loader = RuleLoader(rules_dir)

    # Load all available rules
    rules = loader.load_rules()

    if not rules:
        raise RuntimeError("No rules were successfully loaded")

    logger.info(f"Loaded {len(rules)} rules for scanning")

    # Process files and collect findings
    all_findings: List[Finding] = []

    for file_path in files:
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            continue

        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Apply all rules to this file
            for rule in rules:
                try:
                    findings = rule.apply(file_path, content)
                    if findings:
                        all_findings.extend(findings)
                        logger.debug(f"Rule {rule.id} found {len(findings)} issues in {file_path}")
                except Exception as e:
                    logger.error(f"Rule {rule.id} failed on file {file_path}: {e}")
                    continue

        except (IOError, UnicodeDecodeError, PermissionError) as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing file {file_path}: {e}")
            continue

    # Apply deduplication to remove duplicate findings for the same token
    deduplicated_findings = _deduplicate_findings(all_findings)
    
    logger.info(f"Scan complete: {len(deduplicated_findings)} unique findings across {len(files)} files "
                f"(reduced from {len(all_findings)} total findings)")
    return deduplicated_findings
