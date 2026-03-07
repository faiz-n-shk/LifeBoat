# Lifeboat v2.8.1 - Habit Scoring & Animation Fixes

**Release Date:** March 8, 2026  
**Build Type:** Beta  
**Tag:** `v2.8.1`

---

## 🎯 Summary

This release fixes critical issues with habit scoring and animations introduced in v2.8.0. Habit scores now properly account for frequency counts, and navigation animations work smoothly with the Settings page.

---

## ✨ Improvements

### Frequency-Weighted Habit Scoring

Habit scores now accurately reflect the effort required:

- **Good Habits**: Weighted by frequency count (3x/day habit = 3x impact on score)
- **Partial Credit**: Completing 2 out of 3 gives you 66.7% credit
- **Bad Habits**: Staying below threshold gives full points, exceeding gives zero
- **Fair Comparison**: High-frequency habits no longer undervalued

### Period-Based Streak Display

Non-daily habits now show appropriate streak metrics:

- **Weekly/Monthly/Yearly**: Shows "2 Weeks", "3 Months", "1 Year" instead of days
- **On Hold Status**: Timer icon with "On hold till complete" when period goal not met
- **Success Status**: Fire icon with period count when goal achieved
- **Bad Habits**: Shows "Streak broken" only when actually exceeding threshold

---

## 🐛 Bug Fixes

1. **Habit Score Calculation** - Fixed scoring to weight habits by frequency count
2. **Bad Habit Streaks** - Fixed inverted logic showing "Streak broken" incorrectly
3. **Settings Animation** - Fixed fade animation not playing when navigating to/from Settings
4. **QPainter Errors** - Eliminated painter conflicts from nested opacity effects

---

## 📦 Installation

### Upgrading from v2.7.4

Upgrade from inbuilt migration in Advanced settings:

1. Download the installer for your installation type
2. Run the installer - it will detect your existing installation
3. Your data and settings are preserved automatically
4. Go to settings and search update database, then update it.

### Fresh Installation

Download the installer for your preferred installation type:

- **Standard Installer**: Installs to Program Files (requires admin)
- **Portable Installer**: Installs to user directory (no admin required)

### From Source

```bash
git clone https://github.com/faiz-n-shk/LifeBoat.git
cd LifeBoat
git checkout v2.8.1
pip install -r requirements.txt
python main.py
```

---

## 📝 Full Changelog

For detailed changes, see [CHANGELOG.md](/changelogs/CHANGELOG.md)

---

## 🙏 Feedback

Report bugs and request features on [GitHub Issues](https://github.com/faiz-n-shk/LifeBoat/issues)

---

**Made with ❤️ by Fayz212**
