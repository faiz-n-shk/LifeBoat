# Changelog

## [v1.1.0] - 2025-02-21

**Commit:** `aa0613c`

### Major Features

- **Configuration System Overhaul**: Introduced YAML-based configuration with hot-reload support
- **Database Template System**: Automatic template creation for easy database restoration
- **Read-Only App Metadata**: App version, name, and author now protected from user modification

### Added

- `src/core/config_template.py` - Auto-generates config.yaml on first run
- `src/core/constants.py` - Read-only application metadata (version, name, author)
- Hot-reload functionality via `reload_config()` - Apply settings without restart
- Database template auto-creation in `initialize_database()`
- `refresh_all_modules()` in LifeboatApp for instant UI updates
- Matrix theme - Classic green-on-black hacker aesthetic
- All default themes now included: Dark, Light, Catppuccin Mocha, Cyberpunk, Matrix

### Changed

- Config system now uses YAML instead of hardcoded Python values
- Settings changes apply immediately without requiring app restart
- Database restore now recreates from fresh template with current schema
- Config restore recreates from template instead of copying
- Improved backup messaging and safety prompts in Settings UI

### Fixed

- Config restore WinError 32 (file lock issue)
- Database restore schema mismatch (missing 'time' column)
- Theme initialization - all default themes now properly created

### Removed

- `scripts/create_default_db.py` - Functionality moved to database.py
- Hardcoded app metadata from config.yaml (now in constants.py)

## [v1.0.4] - 2025-02-20

**Commit:** `3a0e3bc`

### Added

- **Locale Settings**: Comprehensive date/time/currency customization
- Currency settings: symbol, code, position, decimal places
- Time mode toggle: 12-hour vs 24-hour format
- Date/time format preview in settings
- `format_time()` and `format_currency()` helper functions

### Changed

- TimePicker now respects 12hr/24hr mode with AM/PM controls
- Expenses display uses configured time format
- All date/time formatting now uses config values
- Settings UI prompts restart for full effect (now obsolete in v1.1.0)

### Fixed

- Expenses page crash from previous commit

---

## [v1.0.3] - 2025-02-19

**Commit:** `191bd47`

### Added

- **Modular Date/Time Pickers**: Created `pickers.py` with reusable UI components
- DatePicker and TimePicker can now be used across all modules

### Changed

- Calendar module refactored to use new picker components
- Improved code reusability and maintainability

---

## [v1.0.2] - 2025-02-18

**Commit:** `c235c94`

### Added

- **Custom File Locations**: Users can set custom paths for config and database
- Path management UI in Settings
- `src/core/path_manager.py` for handling custom locations

### Known Issues

- WinError 2 when config.yaml doesn't exist and restore defaults is executed
- (Fixed in v1.1.0)

---

## [v1.0.1] - 2025-02-17

**Commit:** `2bca09b`

### Added

- Edit button in Expenses module
- Clickable events in Calendar module

### Improved

- Performance optimizations to reduce lag and freezing
- Overall UI responsiveness

---

## [v1.0.0] - Initial Release

**Commit:** `c9a3a24`

### Features

- Dashboard with overview of all data
- Calendar with event management
- Tasks and Todo management
- Expense and Income tracking
- Goals and Habits tracking
- Notes module
- Theme system with Dark and Light themes
- SQLite database with Peewee ORM
- CustomTkinter-based modern UI
