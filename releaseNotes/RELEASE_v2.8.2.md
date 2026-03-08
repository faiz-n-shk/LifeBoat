# Lifeboat v2.8.2 - Icon Theme Fix & Log Control

**Release Date:** March 8, 2026  
**Build Type:** Beta  
**Tag:** `v2.8.2`

---

## 🎯 Summary

This release fixes icon theme update issues and adds log file creation control. Icons now properly refresh when switching themes, and users can disable log file creation in Advanced settings.

---

## ✨ Improvements

### Icon Theme Updates

Icons now properly update when switching themes:

- Accent color changes immediately reflected across all icons
- Smooth visual transitions during theme switches
- No more stale icon cache issues
- Applied to all features: Dashboard, Calendar, Expenses, Habits, Notes, Settings

### Log File Control

New Advanced setting for log file creation:

- Toggle to enable/disable activity log file generation
- Reduces disk I/O when logs aren't needed
- Logs still appear in console for debugging
- Setting persists across sessions

---

## 🐛 Bug Fixes

1. **Icon Theme Updates** - Fixed icons not refreshing after theme changes
2. **Icon Cache** - Eliminated stale icon cache causing visual inconsistencies
3. **Theme Transitions** - Improved icon refresh mechanism for smoother theme switches

---

## 📦 Installation

### Upgrading from v2.8.1

1. Download the installer for your installation type
2. Run the installer - it will detect your existing installation
3. Your data and settings are preserved automatically

### Fresh Installation

Download the installer for your preferred installation type:

- **Standard Installer**: Installs to Program Files (requires admin)
- **Portable Installer**: Installs to user directory (no admin required)

### From Source

```bash
git clone https://github.com/faiz-n-shk/LifeBoat.git
cd LifeBoat
git checkout v2.8.2
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
