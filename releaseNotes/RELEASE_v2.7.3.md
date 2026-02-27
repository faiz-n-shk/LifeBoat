# Lifeboat v2.7.3 Beta Release

**Release Date:** February 27, 2026  
**Build Type:** Beta  
**Commit:** `592edd4`  
**Tag:** `v2.7.3`

---

## 📋 Summary

This release focuses on **UI/UX improvements** and **bug fixes** from the Issues.md backlog. Major highlights include a complete custom dialog system overhaul, fixing annoying scroll behavior on input fields, and resolving 5 critical bugs from the issue tracker.

**Commit:** 592edd416c637f4c9242bb340db6f26c77157188

---

## 🔧 Improvements

### Dialog System Enhancements

- Replaced all system dialogs with custom frameless design
- Created shared dialog helpers: `show_warning()`, `show_information()`, `show_critical()`, `show_question()`
- Theme editor dialog now uses BaseDialog for consistency

### Input Field Improvements

- Created NoScroll wrapper classes for all scrollable input widgets
- Applied to all features: Tasks, Todos, Expenses, Notes, Goals, Habits, Calendar, Settings
- Improved user experience when navigating forms with mouse wheel

---

## 🐛 Bug Fixes

**Note:** For GitHub issues, visit: https://github.com/faiz-n-shk/LifeBoat/issues

1. **App Instance Bug** - Multiple instances prevention with QSharedMemory
2. **Window Management** - Dialog minimize loop fixed with independent windows
3. **Visual Glitches** - Notes search icon positioning
4. **Text Field Behavior** - Scroll behavior removed from input fields

---

## 📦 Installation

### Standard Installation

Download and run `LifeBoatSetup-Standard-2.7.3.exe` for a traditional installation with system integration.

### Portable Version

Download and run `LifeBoatSetup-Portable-2.7.3.exe` to create a portable version that can run from any location.

### Upgrading from v2.7.2

1. Download the new installer
2. Run the installer - it will detect your existing installation
3. Click "Yes" to update, or "No" to proceed with fresh installation
4. Your data and settings will be preserved automatically

### From Source

```bash
git clone https://github.com/faiz-n-shk/LifeBoat.git
cd LifeBoat
pip install -r requirements.txt
python main.py
```

---

## ⚠️ Known Issues

### Open Issues

**Feature Requests (Not Yet Implemented):**

- Built-in Pomodoro Timer with "Always on Top" mode
- Quick Journaling ("Vibe Check") system
- Keyboard Shortcuts (Alt+Space global command, navigation shortcuts)
- Undo/Redo functionality
- Calendar year navigation
- Task/Todo consolidation

**UI/UX Improvements (Planned):**

- Notes placeholder text alignment (currently top-left, should be centered)
- Tags not being displayed in views (needs investigation)

**Note:** Beta status - some features still under testing. Please report any new issues on GitHub.

---

## 🔄 Upgrade Notes

**From v2.7.2:**

- Direct upgrade supported
- All data and settings preserved
- No manual migration needed

---

## 📝 Full Changelog

For a complete list of changes, see [CHANGELOG_v2.md](/changelogs/CHANGELOG_v2.md)

## 🙏 Feedback

Please report bugs and feature requests on [GitHub Issues](https://github.com/faiz-n-shk/LifeBoat/issues)

---

**Made with ❤️ by Fayz212**
