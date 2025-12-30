# Navigation Inconsistency Audit

## Issues Found:

### 1. **home.html**
- ❌ Has "Features" link (anchor to #features section)
- Should have "Home" link like other pages

### 2. **index.html** (Forms Page)
- ✅ Has "Home" link
- ✅ Proper navigation

### 3. **templates_browse.html**
- ✅ Has "Home" link
- ✅ Proper navigation

### 4. **pricing.html**
- ✅ Has "Home" link
- ✅ Proper navigation

### 5. **dashboard.html**
- ❌ NO "Home" link!
- Has: Forms, Templates, Compressor, Pricing, Dashboard, Settings (enterprise)
- Missing navigation back to home page

### 6. **file_compressor.html** ⚠️ CRITICAL
- ❌ **NO NAVBAR AT ALL!**
- Extends base.html which has no navbar
- Users are completely lost when they click File Compressor
- This is the "different world" issue the user mentioned

## Proposed Solution:

Create a standardized navbar that ALL pages use:

**Standard Navigation:**
```
[Logo/Site Name] | Home | Forms | Templates | File Compressor | Pricing | [User Badge] | Dashboard | [Settings] | Logout
```

**When NOT logged in:**
```
[Logo/Site Name] | Home | Forms | Templates | File Compressor | Pricing | Sign In
```

**Implementation:**
- Create navbar include file
- Update all pages to use consistent navigation
- Remove "Features" link from home.html (keep it as "/" instead)
- Add navbar to file_compressor.html
- Add "Home" link to dashboard.html
