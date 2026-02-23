#!/usr/bin/env python3
"""
expo-doctor-plus - Enhanced Expo/React Native project health checker
Detects performance anti-patterns, platform issues, config problems, and common gotchas.
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

# ANSI colors
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
GREEN = '\033[92m'
BOLD = '\033[1m'
RESET = '\033[0m'

class Issue:
    def __init__(self, severity: str, category: str, message: str, file: str = None, line: int = None, suggestion: str = None):
        self.severity = severity  # critical, warning, info
        self.category = category
        self.message = message
        self.file = file
        self.line = line
        self.suggestion = suggestion

class ExpoDoctor:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.issues: List[Issue] = []
        self.stats = defaultdict(int)
        
    def scan(self, quiet=False):
        """Run all checks"""
        if not quiet:
            print(f"{BOLD}🔬 Scanning Expo project: {self.project_path.name}{RESET}\n")
        
        # Check if it's an Expo project
        if not (self.project_path / "app.json").exists():
            if not quiet:
                print(f"{RED}❌ Not an Expo project (no app.json found){RESET}")
            return
        
        # Run checks
        self._check_config()
        self._scan_code_files()
        self._check_dependencies()
        
        # Report results
        if not quiet:
            self._print_results()
    
    def _check_config(self):
        """Check app.json and package.json configuration"""
        app_json_path = self.project_path / "app.json"
        package_json_path = self.project_path / "package.json"
        
        # Check app.json
        if app_json_path.exists():
            with open(app_json_path) as f:
                app_config = json.load(f)
                expo_config = app_config.get("expo", {})
                
                # Check for deep linking
                if not expo_config.get("scheme"):
                    self.issues.append(Issue(
                        "warning", "config",
                        "No deep linking scheme configured",
                        file="app.json",
                        suggestion="Add 'expo.scheme' for universal links support"
                    ))
                
                # Check for splash screen
                if not expo_config.get("splash"):
                    self.issues.append(Issue(
                        "info", "config",
                        "No splash screen configured",
                        file="app.json",
                        suggestion="Add 'expo.splash' for better loading experience"
                    ))
                
                # Check for icon
                if not expo_config.get("icon"):
                    self.issues.append(Issue(
                        "warning", "config",
                        "No app icon configured",
                        file="app.json",
                        suggestion="Add 'expo.icon' (required for app stores)"
                    ))
                
                # Check for privacy policy (iOS requirement)
                ios_config = expo_config.get("ios", {})
                if not ios_config.get("infoPlist", {}).get("NSUserTrackingUsageDescription"):
                    self.issues.append(Issue(
                        "warning", "config",
                        "Missing iOS tracking permission description",
                        file="app.json",
                        suggestion="Add 'expo.ios.infoPlist.NSUserTrackingUsageDescription' (App Store requirement)"
                    ))
        
        # Check package.json
        if package_json_path.exists():
            with open(package_json_path) as f:
                package = json.load(f)
                deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
                
                # Check for common missing dependencies
                if "react-native-safe-area-context" not in deps:
                    self.issues.append(Issue(
                        "warning", "dependencies",
                        "Missing react-native-safe-area-context",
                        file="package.json",
                        suggestion="Install for proper safe area handling on iOS"
                    ))
    
    def _scan_code_files(self):
        """Scan JavaScript/TypeScript files for issues"""
        extensions = ('.js', '.jsx', '.ts', '.tsx')
        
        for file_path in self.project_path.rglob('*'):
            # Skip node_modules, .git, etc.
            if any(part.startswith('.') or part == 'node_modules' for part in file_path.parts):
                continue
            
            if file_path.suffix in extensions:
                self._check_file(file_path)
    
    def _check_file(self, file_path: Path):
        """Check a single file for issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                rel_path = file_path.relative_to(self.project_path)
                
                # Check for console.log in production
                for i, line in enumerate(lines, 1):
                    if re.search(r'\bconsole\.(log|warn|error|debug)\b', line) and '// eslint-disable' not in line:
                        self.issues.append(Issue(
                            "warning", "performance",
                            "Console statement found",
                            file=str(rel_path), line=i,
                            suggestion="Remove console logs from production code"
                        ))
                
                # Check for inline arrow functions in JSX (causes re-renders)
                inline_func_pattern = r'(\w+)=\{(\([^)]*\)|[a-zA-Z_]\w*)\s*=>'
                for i, line in enumerate(lines, 1):
                    if re.search(inline_func_pattern, line) and '<' in line:
                        self.issues.append(Issue(
                            "warning", "performance",
                            "Inline arrow function in JSX (causes re-renders)",
                            file=str(rel_path), line=i,
                            suggestion="Extract to useCallback or define outside render"
                        ))
                
                # Check for missing SafeAreaView
                if 'react-native' in content and 'View' in content and 'SafeAreaView' not in content:
                    if any(word in content for word in ['Screen', 'Container', 'Layout']):
                        self.issues.append(Issue(
                            "info", "platform",
                            "Consider using SafeAreaView for iOS notch support",
                            file=str(rel_path),
                            suggestion="Import SafeAreaView from react-native-safe-area-context"
                        ))
                
                # Check for hardcoded API URLs
                url_pattern = r'["\']https?://(?!localhost)[^"\']+["\']'
                if re.search(url_pattern, content):
                    self.issues.append(Issue(
                        "warning", "config",
                        "Hardcoded API URL found",
                        file=str(rel_path),
                        suggestion="Use environment variables (e.g., process.env.API_URL)"
                    ))
                
                # Check for missing error boundaries
                if 'createStackNavigator' in content or 'createBottomTabNavigator' in content:
                    if 'ErrorBoundary' not in content:
                        self.issues.append(Issue(
                            "info", "reliability",
                            "No error boundary found in navigation setup",
                            file=str(rel_path),
                            suggestion="Wrap navigators with error boundaries for better crash handling"
                        ))
                
                # Check for missing accessibilityLabel on touchables
                touchable_pattern = r'<(Touchable\w+|Pressable)'
                for i, line in enumerate(lines, 1):
                    if re.search(touchable_pattern, line):
                        # Check if accessibilityLabel exists in next few lines
                        context = '\n'.join(lines[i-1:min(i+5, len(lines))])
                        if 'accessibilityLabel' not in context:
                            self.issues.append(Issue(
                                "info", "accessibility",
                                "Touchable without accessibilityLabel",
                                file=str(rel_path), line=i,
                                suggestion="Add accessibilityLabel for screen readers"
                            ))
                
                # Check for unoptimized images
                if re.search(r'require\(["\'].*\.(png|jpg|jpeg)["\']', content):
                    self.issues.append(Issue(
                        "info", "performance",
                        "Consider using optimized images or WebP format",
                        file=str(rel_path),
                        suggestion="Use expo-image or optimize with tinypng.com"
                    ))
                
        except Exception as e:
            pass  # Skip files we can't read
    
    def _check_dependencies(self):
        """Check for outdated or problematic dependencies"""
        package_json_path = self.project_path / "package.json"
        if package_json_path.exists():
            with open(package_json_path) as f:
                package = json.load(f)
                deps = package.get("dependencies", {})
                
                # Check for old React Native version
                rn_version = deps.get("react-native", "")
                if rn_version and rn_version.startswith("0.6"):
                    self.issues.append(Issue(
                        "warning", "dependencies",
                        "Using older React Native version",
                        file="package.json",
                        suggestion="Consider upgrading to 0.71+ for better performance"
                    ))
    
    def _calculate_score(self) -> int:
        """Calculate health score (0-100)"""
        weights = {"critical": 20, "warning": 10, "info": 3}
        total_deductions = sum(weights.get(issue.severity, 0) for issue in self.issues)
        score = max(0, 100 - total_deductions)
        return score
    
    def _print_results(self):
        """Print results to console"""
        # Group by category
        by_category = defaultdict(list)
        for issue in self.issues:
            by_category[issue.category].append(issue)
        
        # Print issues
        if self.issues:
            print(f"\n{BOLD}📋 Issues Found ({len(self.issues)}):{RESET}\n")
            
            for category, issues in sorted(by_category.items()):
                emoji = {"performance": "⚡", "config": "⚙️", "platform": "📱", 
                        "accessibility": "♿", "reliability": "🛡️", "dependencies": "📦"}.get(category, "🔍")
                print(f"{BOLD}{emoji} {category.title()}{RESET}")
                
                for issue in issues:
                    severity_icon = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}[issue.severity]
                    location = f" ({issue.file}:{issue.line})" if issue.file and issue.line else f" ({issue.file})" if issue.file else ""
                    
                    print(f"  {severity_icon} {issue.message}{location}")
                    if issue.suggestion:
                        print(f"     💡 {issue.suggestion}")
                print()
        else:
            print(f"{GREEN}✅ No issues found! Your project looks healthy.{RESET}\n")
        
        # Print score
        score = self._calculate_score()
        score_color = GREEN if score >= 80 else YELLOW if score >= 60 else RED
        print(f"{BOLD}Health Score: {score_color}{score}/100{RESET}\n")
        
        # Print summary
        critical = sum(1 for i in self.issues if i.severity == "critical")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        info = sum(1 for i in self.issues if i.severity == "info")
        
        print(f"Summary: {RED}{critical} critical{RESET} | {YELLOW}{warnings} warnings{RESET} | {BLUE}{info} info{RESET}")
    
    def get_json_output(self) -> dict:
        """Return results as JSON"""
        return {
            "score": self._calculate_score(),
            "total_issues": len(self.issues),
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "file": i.file,
                    "line": i.line,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ]
        }

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Expo/React Native project health checker",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("path", nargs="?", default=".", help="Project path (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    doctor = ExpoDoctor(args.path)
    doctor.scan(quiet=args.json)
    
    if args.json:
        print(json.dumps(doctor.get_json_output(), indent=2))

if __name__ == "__main__":
    main()
