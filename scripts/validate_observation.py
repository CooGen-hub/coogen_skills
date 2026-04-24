#!/usr/bin/env python3
"""
Coogen Skill Content Quality Validator

Validates observation content before sharing to ensure quality standards.
"""

import json
import re
from typing import Dict, List, Tuple

class ObservationValidator:
    """Validates observation quality before sharing"""
    
    # Minimum content length (characters)
    MIN_CONTENT_LENGTH = 500
    
    # Required sections
    REQUIRED_SECTIONS = [
        "problem",  # Problem Description
        "environment",  # Environment
        "solution",  # Solution(s)
    ]
    
    # Recommended sections
    RECOMMENDED_SECTIONS = [
        "root cause",  # Root Cause
        "verification",  # Verification
        "prevention",  # Prevention
        "reference",  # References
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
    
    def validate(self, observation: Dict) -> Tuple[bool, Dict]:
        """
        Validate an observation
        
        Returns:
            (is_valid, report)
        """
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        title = observation.get("title", "")
        content = observation.get("content", "")
        context = observation.get("context", {})
        
        # 1. Validate title
        self._validate_title(title)
        
        # 2. Validate content length
        self._validate_content_length(content)
        
        # 3. Validate content structure
        self._validate_content_structure(content)
        
        # 4. Validate context
        self._validate_context(context)
        
        # 5. Check for sensitive data
        self._check_sensitive_data(content)
        
        # Generate report
        report = {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "metrics": {
                "title_length": len(title),
                "content_length": len(content),
                "has_code_blocks": "```" in content,
                "code_block_count": content.count("```") // 2,
                "section_count": self._count_sections(content),
                "quality_score": self._calculate_quality_score(content, context),
            },
        }
        
        return report["valid"], report
    
    def _validate_title(self, title: str):
        """Validate title quality"""
        if len(title) < 20:
            self.errors.append(f"Title too short ({len(title)} chars). Minimum: 20 characters")
        elif len(title) < 50:
            self.warnings.append(f"Title could be more descriptive ({len(title)} chars)")
        
        # Check for error message in title
        if not any(keyword in title.lower() for keyword in ["error", "fail", "issue", "problem"]):
            self.suggestions.append("Consider including error message or problem in title")
        
        # Check for environment in title
        if not any(env in title.lower() for env in ["macos", "linux", "windows", "docker", "npm", "python"]):
            self.suggestions.append("Consider including environment/tool in title for searchability")
    
    def _validate_content_length(self, content: str):
        """Validate content length"""
        length = len(content)
        
        if length < 200:
            self.errors.append(f"Content critically short ({length} chars). Minimum: {self.MIN_CONTENT_LENGTH}")
        elif length < self.MIN_CONTENT_LENGTH:
            self.errors.append(f"Content too short ({length} chars). Minimum: {self.MIN_CONTENT_LENGTH} characters for quality")
        elif length < 1000:
            self.warnings.append(f"Content acceptable but could be more detailed ({length} chars). Recommended: 1000+ characters")
        else:
            self.suggestions.append(f"Content length excellent ({length} chars)")
    
    def _validate_content_structure(self, content: str):
        """Validate content has required sections"""
        content_lower = content.lower()
        
        # Check required sections
        missing_required = []
        for section in self.REQUIRED_SECTIONS:
            if section not in content_lower:
                missing_required.append(section)
        
        if missing_required:
            self.errors.append(f"Missing required sections: {', '.join(missing_required)}")
        
        # Check recommended sections
        missing_recommended = []
        for section in self.RECOMMENDED_SECTIONS:
            if section not in content_lower:
                missing_recommended.append(section)
        
        if missing_recommended:
            self.warnings.append(f"Missing recommended sections: {', '.join(missing_recommended)}")
        
        # Check for code blocks
        if "```" not in content:
            self.warnings.append("No code blocks found. Consider adding executable code examples")
        
        # Check for multiple solutions
        solution_count = content_lower.count("solution 1") + content_lower.count("solution 2") + content_lower.count("method 1")
        if solution_count < 1:
            self.suggestions.append("Consider providing multiple solution approaches if applicable")
    
    def _validate_context(self, context: Dict):
        """Validate context metadata"""
        required_fields = ["tools", "category"]
        
        for field in required_fields:
            if field not in context:
                self.warnings.append(f"Missing context field: '{field}'")
        
        # Check confidence level
        confidence = context.get("confidence")
        if not confidence:
            self.suggestions.append("Add confidence level (A/B/C) to context")
        
        # Check environment
        if "environment" not in context:
            self.suggestions.append("Add environment details (OS, versions) to context")
    
    def _check_sensitive_data(self, content: str):
        """Check for potentially sensitive data"""
        patterns = [
            (r'/home/[a-zA-Z0-9_]+', "User home path"),
            (r'/Users/[a-zA-Z0-9_]+', "macOS user path"),
            (r'C:\\Users\\[a-zA-Z0-9_]+', "Windows user path"),
            (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', "IP address"),
            (r'sk-[a-zA-Z0-9]{20,}', "API key (OpenAI style)"),
            (r'ghp_[a-zA-Z0-9]{30,}', "GitHub token"),
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email address"),
        ]
        
        for pattern, description in patterns:
            if re.search(pattern, content):
                self.warnings.append(f"Potential sensitive data detected: {description}. Ensure data is sanitized")
    
    def _count_sections(self, content: str) -> int:
        """Count markdown sections"""
        return len(re.findall(r'^#{2,3}\s', content, re.MULTILINE))
    
    def _calculate_quality_score(self, content: str, context: Dict) -> int:
        """Calculate quality score 0-100"""
        score = 0
        
        # Length score (max 30)
        length = len(content)
        if length >= 2000:
            score += 30
        elif length >= 1000:
            score += 25
        elif length >= 500:
            score += 20
        elif length >= 200:
            score += 10
        else:
            score += 5
        
        # Structure score (max 30)
        content_lower = content.lower()
        sections_found = sum(1 for s in self.REQUIRED_SECTIONS if s in content_lower)
        sections_found += sum(1 for s in self.RECOMMENDED_SECTIONS if s in content_lower)
        score += min(30, sections_found * 5)
        
        # Code blocks score (max 20)
        code_blocks = content.count("```") // 2
        score += min(20, code_blocks * 5)
        
        # Context score (max 20)
        if "tools" in context:
            score += 5
        if "category" in context:
            score += 5
        if "environment" in context:
            score += 5
        if "confidence" in context:
            score += 5
        
        return min(100, score)


def validate_observation(observation: Dict, verbose: bool = True) -> bool:
    """
    Validate an observation before sharing
    
    Args:
        observation: The observation to validate
        verbose: Print detailed report
    
    Returns:
        True if valid, False otherwise
    """
    validator = ObservationValidator()
    is_valid, report = validator.validate(observation)
    
    if verbose:
        print("=" * 70)
        print("OBSERVATION QUALITY REPORT")
        print("=" * 70)
        
        print(f"\nQuality Score: {report['metrics']['quality_score']}/100")
        
        # Quality rating
        score = report['metrics']['quality_score']
        if score >= 80:
            rating = "⭐⭐⭐⭐⭐ Outstanding"
        elif score >= 60:
            rating = "⭐⭐⭐⭐ Good"
        elif score >= 40:
            rating = "⭐⭐⭐ Acceptable"
        elif score >= 20:
            rating = "⭐⭐ Needs Improvement"
        else:
            rating = "⭐ Poor"
        print(f"Rating: {rating}")
        
        print(f"\nMetrics:")
        print(f"  • Title Length: {report['metrics']['title_length']} chars")
        print(f"  • Content Length: {report['metrics']['content_length']} chars")
        print(f"  • Code Blocks: {report['metrics']['code_block_count']}")
        print(f"  • Sections: {report['metrics']['section_count']}")
        
        if report['errors']:
            print(f"\n❌ ERRORS ({len(report['errors'])}):")
            for error in report['errors']:
                print(f"  • {error}")
        
        if report['warnings']:
            print(f"\n⚠️  WARNINGS ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  • {warning}")
        
        if report['suggestions']:
            print(f"\n💡 SUGGESTIONS ({len(report['suggestions'])}):")
            for suggestion in report['suggestions']:
                print(f"  • {suggestion}")
        
        print(f"\n{'='*70}")
        print(f"Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
        print(f"{'='*70}\n")
    
    return is_valid


# Example usage
if __name__ == "__main__":
    # Test with a poor observation (like the initial one)
    poor_observation = {
        "title": "Docker error",
        "content": "Use --platform flag to fix",
        "context": {"tools": ["docker"]},
        "outcome": "success"
    }
    
    print("Testing POOR observation:")
    validate_observation(poor_observation)
    
    # Test with a good observation
    good_observation = {
        "title": "Docker build fails on macOS ARM64: 'no matching manifest for linux/arm64/v8'",
        "content": """## Problem Description
When running `docker build` on macOS with Apple Silicon (M1/M2/M3), the build fails with:

```
ERROR: failed to solve: no matching manifest for linux/arm64/v8 in the manifest list entries
```

## Environment
- OS: macOS Sonoma 14.2.1
- Chip: Apple M2 Pro
- Docker Desktop: 4.27.1

## Root Cause
The Docker image doesn't have ARM64 manifest.

## Solution
```bash
docker build --platform linux/amd64 -t myapp .
```

## Verification
docker inspect myapp:latest | grep Architecture

## References
- https://docs.docker.com/build/building/multi-platform/
""",
        "context": {
            "tools": ["docker"],
            "category": "error_fix",
            "environment": {"os": "macOS", "chip": "M2"},
            "confidence": "A"
        },
        "outcome": "success"
    }
    
    print("\nTesting GOOD observation:")
    validate_observation(good_observation)
