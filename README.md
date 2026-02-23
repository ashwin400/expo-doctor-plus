# expo-doctor-plus

Enhanced health checker for Expo and React Native projects. Catches what `expo doctor` misses.

Zero dependencies. Works offline.

```bash
python3 expo_doctor_plus.py /path/to/your/app
```

---

## What `expo doctor` Does Not Check

`expo doctor` verifies SDK compatibility and package versions. It does not catch:

- Performance anti-patterns in your components
- Missing accessibility labels
- Platform-specific configuration errors
- Hardcoded API URLs and secrets
- Missing error boundaries
- SafeAreaView usage issues
- Push notification and deep linking misconfiguration

This tool checks all of that.

## Install

```bash
curl -O https://raw.githubusercontent.com/ashwin400/expo-doctor-plus/main/expo_doctor_plus.py
python3 expo_doctor_plus.py .
```

## Usage

```bash
# Scan current project
python3 expo_doctor_plus.py .

# Scan specific project
python3 expo_doctor_plus.py /path/to/project

# Show only critical and warning issues
python3 expo_doctor_plus.py . --severity warning

# JSON output
python3 expo_doctor_plus.py . --json

# Quiet mode (exit code only, good for CI)
python3 expo_doctor_plus.py . --quiet
```

## What It Checks

**Performance**
- Inline arrow functions in JSX (`onPress={() => ...}` in list renders)
- `console.log` statements left in production code
- Unoptimized image imports without width/height specified
- Missing `keyExtractor` in FlatList/SectionList

**Platform Issues**
- Missing `SafeAreaView` on screens with navigation
- iOS/Android platform-specific code paths that may break on the other platform
- Keyboard avoiding view issues

**Configuration**
- Deep linking scheme not configured
- Push notification setup incomplete
- Missing splash screen configuration
- `app.json` version not bumped

**Accessibility**
- Interactive elements missing `accessibilityLabel`
- Touchable components without accessible hints
- Images missing `accessibilityRole`

**Security**
- Hardcoded API keys or tokens
- HTTP URLs in production config
- Debug flags in production builds

## Example Output

```
expo-doctor-plus: MyApp/
Scanned: 47 files

CRITICAL  Hardcoded API key detected
  src/config.ts:12 -- API_KEY = "sk-..."
  Move to environment variables.

WARNING   Inline function in FlatList render
  src/screens/Feed.tsx:44  renderItem={({ item }) => <Card .../>}
  Extract to a named function or use useCallback to avoid re-renders.

WARNING   Missing accessibilityLabel
  src/components/LikeButton.tsx:18  <TouchableOpacity onPress={...}>
  Add accessibilityLabel="Like post" for screen reader support.

INFO      console.log found (14 instances)
  Remove or replace with a logging library before release.

Summary: 1 critical, 2 warnings, 1 info
```

## Requirements

Python 3.9+. No dependencies. Works with Expo SDK 48+.
