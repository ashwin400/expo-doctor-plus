# expo-doctor-plus 🔬

Enhanced Expo/React Native project health checker that goes beyond `expo doctor`.

## What It Does

Detects issues that the official `expo doctor` misses:

- **Performance Anti-Patterns** - Inline functions in JSX, unoptimized images, console logs
- **Platform-Specific Issues** - Missing SafeAreaView, iOS/Android differences
- **Configuration Problems** - Deep linking setup, push notifications, app store metadata
- **Accessibility Issues** - Missing accessibilityLabels, contrast problems
- **Common Gotchas** - Hardcoded API URLs, missing error boundaries

## Installation

```bash
# Copy to your project or add to PATH
cp expo_doctor_plus.py /usr/local/bin/expo-doctor-plus
chmod +x /usr/local/bin/expo-doctor-plus
```

## Usage

```bash
# Check current directory
python3 expo_doctor_plus.py

# Check specific project
python3 expo_doctor_plus.py /path/to/expo-project

# JSON output (for CI)
python3 expo_doctor_plus.py --json
```

## Example Output

```
🔬 Scanning Expo project: my-app

📋 Issues Found (8):

⚡ Performance
  ⚠️ Console statement found (src/Home.tsx:45)
     💡 Remove console logs from production code
  ⚠️ Inline arrow function in JSX (src/Button.tsx:12)
     💡 Extract to useCallback or define outside render

⚙️ Config
  ⚠️ No deep linking scheme configured (app.json)
     💡 Add 'expo.scheme' for universal links support
  ⚠️ Hardcoded API URL found (src/api.ts)
     💡 Use environment variables (e.g., process.env.API_URL)

♿ Accessibility
  ℹ️ Touchable without accessibilityLabel (src/Button.tsx:23)
     💡 Add accessibilityLabel for screen readers

Health Score: 65/100

Summary: 0 critical | 5 warnings | 3 info
```

## vs. Official `expo doctor`

| Feature | `expo doctor` | `expo-doctor-plus` |
|---------|---------------|-------------------|
| Package compatibility | ✅ | ❌ |
| Config validation | ✅ | ✅ |
| Performance checks | ❌ | ✅ |
| Accessibility | ❌ | ✅ |
| Platform-specific | ❌ | ✅ |
| Code pattern analysis | ❌ | ✅ |
| App store readiness | ❌ | ✅ |

**Recommendation:** Use both! Run `expo doctor` for package compatibility, then `expo-doctor-plus` for everything else.

## Checks Performed

### Performance
- Console statements in production
- Inline arrow functions in JSX (causes unnecessary re-renders)
- Unoptimized images (suggests WebP or expo-image)
- Missing React.memo/useCallback opportunities

### Configuration
- Deep linking scheme (app.json)
- Splash screen setup
- App icon configuration
- iOS privacy descriptions (App Store requirement)
- Push notification config

### Platform Issues
- SafeAreaView usage for iOS notch
- Platform.select usage
- Hardcoded dimensions (should use Dimensions API)

### Accessibility
- Missing accessibilityLabels on touchables
- Screen reader support

### Reliability
- Missing error boundaries
- Hardcoded API URLs (should use env vars)
- Unhandled promise rejections

### Dependencies
- Outdated React Native version
- Missing common packages (react-native-safe-area-context)

## CI Integration

```yaml
# GitHub Actions example
- name: Check Expo project health
  run: |
    python3 expo_doctor_plus.py --json > health.json
    SCORE=$(jq '.score' health.json)
    if [ "$SCORE" -lt 70 ]; then
      echo "Health score too low: $SCORE"
      exit 1
    fi
```

## Roadmap

- [ ] Image size analysis (detect large assets)
- [ ] Bundle size estimation
- [ ] Detect platform-specific code without Platform.select
- [ ] Check for proper keyboard handling
- [ ] Validate app store screenshots/metadata
- [ ] Integration with Expo EAS

## Why This Exists

The official `expo doctor` is great for package compatibility, but doesn't check for:
- Code quality issues that hurt performance
- Common beginner mistakes
- App store rejection issues
- Accessibility problems

This tool fills those gaps.

## License

MIT

## Contributing

PRs welcome! Add more checks to `_check_file()` or `_check_config()`.
