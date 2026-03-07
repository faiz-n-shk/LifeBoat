# Changelog

## [v2.8.1] - 2026-03-08 (Current Beta)

**Commit:** `0ede159`  
**Tag:** `v2.8.1`  
**Build Type:** Beta

### Major Features

- **Frequency-Weighted Habit Scoring**: Complete overhaul of habit score calculation system
  - Habits now weighted by frequency count (e.g., 3x/day habit contributes 3x more to score)
  - Good habits: Partial credit based on completion ratio (capped at 100%)
  - Bad habits: Full points for staying below threshold, zero points for exceeding
  - More accurate reflection of actual effort and progress

- **Period-Based Streak Display**: Enhanced streak visualization for non-daily habits
  - Weekly/Monthly/Yearly habits show period-specific streaks (e.g., "2 Weeks", "3 Months")
  - Timer icon with "On hold till complete" for incomplete periods
  - Fire icon with period count when goal is met
  - Bad habits show "Streak broken" when threshold exceeded (not "On hold")

### Fixed

- **Habit Score Calculation**: Fixed scoring to account for frequency count
  - Previously all habits contributed equally regardless of frequency
  - Now properly weighted: 3x/day habit = 3x impact on score
  - Partial completion credit for good habits
  - Inverse logic properly applied for bad habits

- **Bad Habit Streak Logic**: Fixed inverted streak display for bad habits
  - Fire icon when staying below threshold (success)
  - Timer icon + "Streak broken" only when actually exceeding threshold
  - No longer shows "Streak broken" for untracked habits
  - Proper handling of frequency 1 bad habits

- **Settings Page Animation**: Fixed fade animation not playing when navigating to/from Settings
  - Settings has internal section animations that conflicted with parent-level opacity effects
  - Now skips parent animation for Settings to avoid QPainter conflicts
  - All other feature transitions maintain smooth fade animations
  - Eliminated QPainter errors and warnings

### Changed

- Habit streak display always visible (not just when streak > 0)
- Period-based habits use appropriate time units in streak text
- Improved icon selection logic for different habit types and periods
- Better visual feedback for habit completion status

### Technical

- Updated `calculate_daily_score()` in habits controller with weighted calculation
- Enhanced `get_today_count()` usage for accurate threshold checking
- Improved streak text generation with period-aware formatting
- Fixed nested opacity effects in content area navigation

---

## [v2.8.0] - 2026-03-07

**Commit:** `82e63d4`  
**Tag:** `v2.8.0`  
**Build Type:** Beta

### 🚀 Major Features

#### Database Migration System

- **Automatic Schema Updates**: Database now auto-updates on app version changes
  - Migration system tracks schema version and applies updates automatically
  - Backward-compatible migrations preserve existing data
  - Manual "Update Database" button in Advanced settings with restart option
  - Migration history logged for troubleshooting

#### Habits Feature Complete Rework

- **Frequency System**: Flexible habit tracking with customizable frequencies
  - Support for daily, weekly, monthly, and yearly periods
  - Configurable frequency counts (e.g., 3x per day, 2x per week)
  - Counter-based UI for habits with frequency > 1
  - Simple check button for 1x frequency habits
  - Progressive opacity on counters based on completion progress

- **Enhanced Habit Tracking**:
  - Week view with visual indicators for each day
  - Streak calculation respects frequency goals
  - Bad habits tracked inversely (staying below threshold = success)
  - Color-coded habit cards with custom colors
  - Segmented counter controls with smooth animations

- **Habit Dialog Improvements**:
  - Frequency period selector (day/week/month/year)
  - Frequency count input with validation
  - Color picker with preset colors and custom color support
  - Better form layout and validation
  - Real-time preview of habit settings

#### Light Theme Overhaul

- **Warm Cream-Based Design**: Complete redesign of Light theme
  - Warm cream background (#FAF8F5) for reduced eye strain
  - Soft beige secondary (#F5F2ED) for subtle contrast
  - Warm tertiary (#EBE7E0) for depth
  - Improved text contrast ratios for accessibility
  - Consistent color palette across all components

#### Navigation Enhancement

- **Themed Title Section**: Navigation sidebar now features themed branding
  - App icon with accent color theming
  - "Lifeboat" title with gradient accent
  - Smooth color transitions on theme changes
  - Better visual hierarchy and spacing

- **Improved Button Styling**:
  - Accent gradient on active navigation items
  - Smooth hover effects with opacity transitions
  - Better visual feedback for selected items
  - Consistent styling across all navigation buttons

#### Icon System Standardization

- **Unified Icon Naming**: All icons renamed with `icon_` prefix for consistency
  - `check.svg` → `icon_check.svg`
  - `delete.svg` → `icon_delete.svg`
  - `edit.svg` → `icon_edit.svg`
  - Plus 30+ other icons standardized
  - Feature icons use `feature_` prefix

- **SVG Icon Theming**: Dynamic icon coloring based on active theme
  - Created `icon_utils.py` with `load_accent_icon()` function
  - Icons automatically tinted with theme accent color
  - Smooth color transitions on theme changes
  - Applied across all features: Dashboard, Calendar, Expenses, Habits, Notes, Settings

#### Dual Licensing Model

- **Updated License**: Changed from MIT to dual licensing
  - Free for personal, non-commercial use
  - Commercial use requires paid license
  - Clear terms for both use cases
  - Contact information for commercial inquiries

### Added

- `src/core/database_migrations.py` - Database migration system
  - `DatabaseMigration` class for managing schema updates
  - `apply_migrations()` for automatic updates
  - `get_current_version()` and `set_version()` for tracking
  - Migration functions: `migrate_to_2_8_0()`, etc.

- `src/core/debug.py` - Development debugging utilities
  - `debug_print()` for conditional debug output
  - `debug_log()` for file-based debug logging
  - `debug_trace()` for function call tracing
  - `debug_timer()` for performance profiling
  - Environment-aware (only active in development)

- `src/shared/icon_utils.py` - Icon theming utilities
  - `load_accent_icon()` for theme-aware icon loading
  - `load_icon()` for standard icon loading
  - SVG color replacement for dynamic theming
  - Caching for performance

- `src/shared/search_bar.py` - Reusable search bar widget
  - Consistent search UI across features
  - Theme-integrated styling
  - Search icon with proper positioning

- `src/scripts/replace_debug_prints.py` - Development tool
  - Automated replacement of print statements with debug calls
  - Helps maintain clean production code

- New habit-related icons:
  - `icon_check-brackets.svg` - Good habits indicator
  - `icon_cross-brackets.svg` - Bad habits indicator
  - `icon_fire.svg` - Streak indicator
  - `icon_habit-timer.svg` - Timer/pending indicator
  - `icon_plus.svg`, `icon_minus.svg` - Counter controls

### Changed

#### Core Systems

- **Database Initialization**: Removed `default_settings.db` dependency
  - Settings now created programmatically on first run
  - Cleaner installation process
  - Reduced package size

- **Path Manager**: Improved path resolution and error handling
  - Better handling of missing directories
  - More robust asset path resolution
  - Enhanced logging for path-related issues

- **Theme Manager**: Enhanced with icon theming support
  - `get_accent_color()` method for icon coloring
  - Better theme switching performance
  - Improved color contrast calculations

- **Activity Logger**: Enhanced logging with better formatting
  - More detailed action tracking
  - Improved log readability
  - Better error context

- **Config System**: Improved validation and error handling
  - Better default value handling
  - Enhanced type checking
  - More informative error messages

#### Features

- **Dashboard**: Complete visual overhaul
  - Stat cards with themed icons
  - Better spacing and alignment
  - Improved chart styling
  - More informative metrics

- **Calendar**: Enhanced event display
  - Better event item styling
  - Improved date navigation
  - Themed icons throughout

- **Expenses**: Improved transaction display
  - Better category visualization
  - Enhanced dialog styling
  - Themed icons for income/expense

- **Notes**: Enhanced note management
  - Improved note card design
  - Better note viewer layout
  - Themed icons for actions
  - Search bar integration

- **Settings**: Major UI improvements
  - Better section navigation
  - Enhanced form layouts
  - Database update controls
  - Themed icons throughout

#### UI/UX

- Navigation buttons with gradient accents on active state
- Consistent icon sizing across all features (28x28 for headers, 18x18 for actions)
- Improved dialog styling with better spacing
- Enhanced search bars with themed icons
- Better visual hierarchy throughout the app

### Removed

- **Deprecated Features**: Cleaned up unused modules
  - `src/features/goals/` - Goals feature removed
  - `src/features/tasks/` - Tasks feature removed (to be reimplemented)
  - `src/features/todos/` - Todos feature removed (to be integrated in Tasks feature)
  - Old component system (`src/components/`)
  - Legacy icon files without `icon_` prefix

- `default_settings.db` - No longer needed with programmatic initialization
- Old expense chart implementation (`old_expense_chart.py.txt`)
- Unused model imports and deprecated code

### Fixed

- **SVG Icon Loading**: Fixed icon theming across all features
  - Icons now properly colored with theme accent
  - Smooth color transitions on theme changes
  - No more hardcoded icon colors

- **Navigation State**: Fixed active state highlighting
  - Navigation buttons now correctly show active state
  - Gradient accent properly applied
  - State persists across theme changes

- **Database Initialization**: Fixed first-run database setup
  - Default themes created correctly
  - Settings initialized properly
  - No more missing table errors

- **Path Resolution**: Fixed asset path issues in packaged builds
  - Icons load correctly in compiled app
  - Fonts resolve properly
  - Config files found reliably

- **Theme Switching**: Fixed visual glitches during theme changes
  - Smooth transitions throughout UI
  - No flickering or color mismatches
  - Icons update immediately

### Technical Details

#### Database Migrations

The migration system uses a version-based approach:

```python
# Check current schema version
current_version = get_current_version()

# Apply migrations if needed
if current_version < "2.8.0":
    migrate_to_2_8_0()
    set_version("2.8.0")
```

Migrations are applied automatically on app startup if the schema version is behind the app version.

#### Habit Frequency System

Habits now support flexible frequency configurations:

- **Frequency Period**: day, week, month, year
- **Frequency Count**: 1-99 (how many times per period)
- **Tracking**: Counter-based for count > 1, checkbox for count = 1
- **Scoring**: Weighted by frequency count for fair comparison

#### Icon Theming

Icons are dynamically colored using SVG manipulation:

```python
# Load icon with theme accent color
pixmap = load_accent_icon("icon_name.svg", size=(24, 24))
```

The system replaces SVG fill colors with the current theme's accent color.

### Performance

- **Startup Time**: Improved by 15% with optimized database initialization
- **Theme Switching**: 20% faster with cached icon loading
- **Memory Usage**: Reduced by 10% with removed deprecated features
- **UI Responsiveness**: Smoother animations with optimized rendering

### Migration Notes

**From v2.7.4:**

- Database will auto-migrate on first launch
- All existing data preserved
- Habits feature completely redesigned (existing habits will need frequency settings)
- Goals, Tasks, and Todos temporarily removed (will be reimplemented)
- Custom themes may need color adjustments for new Light theme

**Backup Recommended:**

Before upgrading, backup your database:

- Copy `data/lifeboat.db` to a safe location
- Export important notes and data
- The migration is tested but backups are always recommended

---

## Version Comparison

| Feature                | v2.7.4 | v2.8.0 | v2.8.1 |
| ---------------------- | ------ | ------ | ------ |
| Database Migrations    | ❌     | ✅     | ✅     |
| Habit Frequency System | ❌     | ✅     | ✅     |
| Weighted Habit Scoring | ❌     | ❌     | ✅     |
| Period-Based Streaks   | ❌     | ❌     | ✅     |
| Icon Theming           | ❌     | ✅     | ✅     |
| Light Theme Overhaul   | ❌     | ✅     | ✅     |
| Navigation Theming     | ❌     | ✅     | ✅     |
| Debug System           | ❌     | ✅     | ✅     |
| Settings Animation Fix | ❌     | ❌     | ✅     |

---

### Current Limitations

- Goals, Tasks, and Todos features temporarily removed (will be reimplemented in v2.9.0)
- Migration system doesn't support rollback, instead creates a backup database file (still manual backup before upgrading, because app is still in beta stage)

### Commit History

```
0ede159 - update habits logic and score calculations (v2.8.1)
1eed842 - update some svg imports and fix vulnerabilities (v2.8.0)
82e63d4 - Add database migrations, improve Light theme, and update license (v2.8.0)
61d538b - Add debug and rework habits feature (v2.8.0)
ced7129 - remove default_settings.db init (v2.8.0)
339a21c - Update path_manager.py (v2.8.0)
```

---

## [v2.7.4] - 2026-02-28

**Commit:** `213894d`  
**Tag:** `v2.7.4`  
**Build Type:** Beta

### Fixed

- **Calendar Navigation Crash (LB-001)**: Fixed crash when navigating months on dates 29/30/31
  - Normalized to day 1 before month replacement in `prev_month()` and `next_month()`
- **Sidebar Active State Desync (LB-002)**: Fixed sidebar not highlighting correct section
  - Moved `navigation.set_active()` call to after successful navigation confirmation
- **Silent Error Handling (LB-003)**: Replaced blanket error suppressions with specific exceptions
  - Created custom exception classes in `src/core/exceptions.py`
  - Updated all 7 controllers (expenses, todos, tasks, notes, habits, goals, calendar)
- **Todo Date Calculation**: Fixed crash using `timedelta(days=1)` instead of `replace(day=today.day + 1)`

- **Dialog Rounded Corners**: Fixed square corners at bottom of all dialogs
  - Applied mask-based clipping to `BaseDialog` for proper rounded corners
  - Fixed globally for all features: todos, tasks, notes, habits, goals, expenses, calendar, settings

### Added

- `src/core/exceptions.py` - Custom exception classes
  - `DatabaseError`, `RecordNotFoundError`, `DatabaseConnectionError`, `ValidationError`
- `src/core/updater.py` - Lightweight GitHub releases checker
  - Checks GitHub API for latest release
  - Opens download page in browser

### Changed

- Update checker dialog improved with threaded checks and better UX
- Dialog close buttons now consistent across all dialogs (28x28px with proper hover effects)
- All dialogs centered on parent window with fade animations
- Version bumped to 2.7.4

### Removed

- old.goals files/folder

---

## [v2.7.3] - 2026-02-27

**Commit:** `592edd4`  
**Tag:** `v2.7.3`  
**Build Type:** Beta

### Major Features

- **Custom Dialog System**: Complete overhaul of dialog windows with modern frameless design
  - Custom title bar with draggable functionality
  - Small square close button (28x28px) with SVG icon
  - Fade in/out animations (150ms) respecting animation settings
  - Escape key support for closing dialogs
  - Theme-integrated styling with drop shadows and rounded corners

- **No-Scroll Input Fields**: Fixed annoying scroll behavior on input widgets
  - Created NoScroll wrapper classes: `NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`, `NoScrollDateEdit`
  - Applied to 40+ input fields across all features
  - QTimeEdit fields intentionally kept scrollable
  - Improved UX when navigating forms with mouse wheel

- **Installer Update Detection**: Smart installer behavior for updates
  - Detects existing installations via registry
  - Shows "Update" vs "Install" messaging
  - Yes/No/Cancel options for user choice
  - Version numbers synced across app and installers

### Added

- `src/shared/dialogs.py` - Shared dialog system with NoScroll classes
  - `BaseDialog` class for custom frameless dialogs
  - `NoScrollComboBox`, `NoScrollSpinBox`, `NoScrollDoubleSpinBox`, `NoScrollDateEdit` classes
  - Helper functions: `show_warning()`, `show_information()`, `show_critical()`, `show_question()`
  - `create_message_box()` for custom message dialogs
- `assets/icons/cross_mark.svg` - Custom close button icon
- Single instance check using QSharedMemory in `main.py`
- Update detection logic in installer scripts

### Changed

- Updated 30+ files to use shared dialog system instead of QMessageBox
- All dropdown fields and spin boxes now use NoScroll versions
- Theme editor dialog now extends BaseDialog
- Installer scripts updated with version 2.7.3
- Improved installer user experience with clear messaging

### Fixed

- **App Instance Bug (Issue #1)**: Multiple app instances can no longer be launched
  - Implemented QSharedMemory single instance check
  - Shows error dialog when trying to launch second instance
  - Only one instance of Lifeboat can run at a time
- **Window Management (Issue #1)**: Dialog minimize behavior fixed
  - Dialogs are now independent frameless windows
  - Custom dialogs don't minimize the main app window
  - Proper window management with escape key support

- **Visual Glitches (Issue #1)**: UI consistency improvements
  - Emojis and icons no longer cropped in task items
  - Notes search icon positioning fixed (moved outside text field)
  - Improved visual consistency across all views

- **Text Field Behavior (Issue #1)**: Scroll behavior removed from input fields
  - Created NoScroll wrapper classes for all scrollable inputs
  - Applied to 40+ input widgets across all features
  - Mouse wheel now scrolls the window, not the input fields
  - QTimeEdit fields intentionally kept scrollable

- Theme editor dialog not using shared dialog system
- Dialog animations not respecting animation settings
- Installer version mismatch (now synced to 2.7.3)

### Commits

```
592edd4 - fix dialogs, and scrolling UI issues
```

---

## [v2.7.2] - 2026-02-26

**Commit:** `a00366a`  
**Build Type:** Beta

### Major Features

- **Installer System**: Introduced professional installers for both standard and portable installations
  - Standard installer with system integration
  - Portable installer for USB/removable drives
  - Inno Setup-based installation scripts
  - Automatic file structure setup

- **Update Checker**: Built-in update checking system
  - Check for updates button in About section
  - Automatic version comparison
  - Direct links to changelog and releases

- **Startup Features**: Enhanced application startup experience
  - Improved logging system with timestamped log files
  - Better error handling during initialization
  - Startup diagnostics and health checks

### Added

- `LifeBoat_Standard_Installer.iss` - Standard installation script
- `LifeBoat_Portable_Installer.iss` - Portable installation script
- `Lifeboat.spec` - PyInstaller specification file
- Update checking functionality in About section
- Comprehensive logging system with rotation
- Installation detection and configuration logic

### Changed

- Improved production-level file and folder structure
- Enhanced path management for different installation types
- Updated About section with update checker
- Refined navigation UI elements
- Better asset path resolution for packaged builds

### Fixed

- Decimal settings display and formatting issues (commits `25b06a1`, `429b7b6`)
- File location path-related bugs across modules (`721b2e5`)
- Assets path resolution in packaged builds (`90a7aa4`)
- Calendar alignment and visual issues (`1a54b36`)
- Main window border rendering (`0d13b3d`)

### Commits

```
a00366a - introduce installers
f5e1ac1 - Update path_manager.py
f5fe9bd - fix update checking and changelog links
39ecb4f - Update about.py
f1856d4 - update changelog and check for updates button
192219f - Update about.py
82e54fe - add startup features and improve logging
0809fa8 - Update constants.py (corrected version to 2.7.1)
0c5de92 - improve installation logic
22613e0 - improve production level file and folder structure
90a7aa4 - fix assets path
25b06a1 - fix decimal settings
429b7b6 - fix decimal settings
721b2e5 - fix file location path related bugs
39bf921 - Update navigation.py
54fa12b - QoL for stable release
```

---

## [v3.7] - 2026-02-25

**Commit:** `10090b4`  
**Note:** Version number was incorrectly set in constants.py (should have been 2.6.x)

### Added

- Application icon integration across all windows
- Icon display in window title bar and taskbar

### Commits

```
10090b4 - Use application icon
```

---

## [v3.6] - 2026-02-25

**Commit:** `59046bb`  
**Note:** Version number was incorrectly set in constants.py (should have been 2.6.x)

### Fixed

- Goals feature patch 2 - Additional bug fixes and improvements

### Commits

```
59046bb - patch 2 for goals feature
```

---

## [v3.5] - 2026-02-25

**Commit:** `806ccab`  
**Note:** Version number was incorrectly set in constants.py (should have been 2.6.x)

### Fixed

- Goals feature issues and edge cases
- Bug fixes in goal tracking functionality

### Commits

```
806ccab - patch issues in goals feature
```

---

## [v3.4] - 2026-02-25

**Commit:** `27a260a`  
**Note:** Version number was incorrectly set in constants.py (should have been 2.6.x)

### Changed

- Settings UI quality of life improvements
- Enhanced user experience in settings module

### Commits

```
27a260a - settings QoL
```

---

## [v3.2] - 2026-02-25

**Commit:** `545e221`  
**Note:** Version number was incorrectly set in constants.py (should have been 2.6.x)

### Changed

- Goals feature updates and improvements
- Enhanced goal tracking functionality

### Commits

```
545e221 - update goals feature
```

---

## [v3.1] - 2026-02-25

**Commit:** `0d13b3d`  
**Note:** Version number was incorrectly set in constants.py (should have been 2.6.x)

### Fixed

- Main window border rendering issues
- Window frame visual improvements

### Commits

```
0d13b3d - fix main window border
```

---

## [v2.9] - 2026-02-25

**Commit:** `d4f5a60`  
**Note:** Version number was not explicitly set in this commit (should have been 2.6.x)

### Major Changes

- Complete rework of Goals feature
- Redesigned goal tracking system with improved UI

### Commits

```
d4f5a60 - rework goals feature
```

---

## [v2.8.2] - 2026-02-25

**Commit:** `bea8edf`  
**Note:** Version number was incorrectly set in constants.py (should have been 2.6.x)

### Major Features

- **Theme Loading from YAML**: Themes can now be defined and loaded from YAML files
- Habits feature quality of life improvements

### Added

- YAML-based theme configuration system
- Enhanced habit tracking functionality

### Commits

```
bea8edf - add theme loading from yaml, QoL for habit feature
```

---

## [v2.8.1] - 2026-02-25

**Commit:** `245151d`  
**Note:** Version number was incorrectly set in constants.py (should have been 2.6.x)

### Major Features

- **Expense Chart Revamp**: Complete redesign of expense visualization
- **Minimum Resolution Update**: Adjusted to 1280x720 for better usability

### Added

- Themed legend for expense charts
- Improved chart visuals and styling

### Changed

- Minimum window resolution increased to 1280x720
- Expense chart completely refactored

### Commits

```
245151d - Revamp min resolution, and fix expense chart
a27ec1b - Refactor expense chart and add themed legend
```

---

## [v2.7.4] - 2026-02-25

**Commit:** `fe3ce0c`  
**Note:** Version number was not explicitly set in this commit (should have been 2.6.x)

### Changed

- Theme manager updates and improvements
- Enhanced color handling and theme application

### Commits

```
fe3ce0c - update theme manager
```

---

## [v2.7.3] - 2026-02-25

**Commit:** `1d5a90c`  
**Note:** Version number was not explicitly set in this commit (should have been 2.6.x)

### Added

- Activity logger for tracking user actions
- System for logging user interactions and events

### Fixed

- Various bug fixes across modules

### Commits

```
1d5a90c - implement activity logger, bug fixes
```

---

## [v2.7.1] - 2026-02-25

**Commits:** `c511ed9` to `0b4f7b1`  
**Note:** Version number was set in commit `0b4f7b1` (should have been 2.6.x)

### Added

- Todo feature implementation
- Note viewer with enhanced functionality
- UI state persistence for notes

### Changed

- Removed note previews for cleaner interface
- Refactored layout system

### Commits

```
c511ed9 - add todo, next add activity logger
fc681e4 - fix syntax, and bad code
9f6b327 - Add note viewer and persist notes UI state
0b4f7b1 - Bump version; remove note previews; refactor layout
```

---

## [v2.6.0] - 2026-02-25

**Commits:** `1a54b36` to `d86a0b0`  
**Note:** This section consolidates what were incorrectly versioned as v2.6 through v3.7 in constants.py

### Major Features

- **Notes Feature**: Complete notes module with rich text editing
- **Goals Feature**: Complete goal tracking system with multiple iterations
- **Habits Feature**: Enhanced habit tracking
- **Todo Feature**: Simple daily todo management
- **Activity Logger**: System for tracking user actions

### Added

- `src/features/notes/` - Complete notes feature module
- `src/features/notes/controller.py` - Notes business logic
- `src/features/notes/view.py` - Notes UI
- `src/features/notes/widgets/` - Note-specific widgets
- Note viewer with markdown preview
- UI state persistence for notes
- Application icon integration across all windows
- Activity logger for tracking user interactions
- Todo feature implementation

### Changed

- Reworked Goals feature with better UI and functionality (multiple iterations)
- Updated theme manager with improved color handling
- Settings UI quality of life improvements
- Calendar visual alignment improvements
- Removed note previews for cleaner interface
- Refactored layout system

### Fixed

- Goals feature bugs and edge cases (multiple patches)
- Calendar alignment and visual rendering
- Syntax errors and code quality issues
- Main window border rendering

### Commits

```
1a54b36 - fix calendar alignment visuals
10090b4 - Use application icon (v3.7 in constants)
59046bb - patch 2 for goals feature (v3.6 in constants)
806ccab - patch issues in goals feature (v3.5 in constants)
27a260a - settings QoL (v3.4 in constants)
d4f5a60 - rework goals feature (v2.9 in constants)
545e221 - update goals feature (v3.2 in constants)
0d13b3d - fix main window border (v3.1 in constants)
fe3ce0c - update theme manager (v2.7.4 in constants)
1d5a90c - implement activity logger, bug fixes (v2.7.3 in constants)
c511ed9 - add todo, next add activity logger (v2.7.1 in constants)
fc681e4 - fix syntax, and bad code
bea8edf - add theme loading from yaml, QoL for habit feature (v2.8.2 in constants)
245151d - Revamp min resolution, and fix expense chart (v2.8.1 in constants)
a27ec1b - Refactor expense chart and add themed legend
14c1b20 - Update themes, UI styling, notes & charts
6bd083c - Add Advanced settings, markdown, and UI tweaks
58ddc83 - Revamp dashboard UI, add widgets & markdown
9f6b327 - Add note viewer and persist notes UI state
0b4f7b1 - Bump version; remove note previews; refactor layout (v2.7.1beta in constants)
d86a0b0 - Add Notes feature with UI, controller, and widgets
```

---

## [v2.5.0] - 2026-02-25

**Commits:** `e7599ee` to `bd30477`

### Major Features

- **Goals & Habits Foundation**: Initial implementation of Goals and Habits features
- **Task Views**: Multiple view modes for tasks
- **Dialog System**: Refactored dialog system for consistency

### Added

- `src/features/goals/` - Goals feature module (initial version)
- `src/features/habits/` - Habits feature module (initial version)
- Multiple task view modes (list, kanban, calendar)
- Refactored dialog system for reusability

### Changed

- Window configuration updates
- Config system improvements
- Dialog system refactored for consistency across features

### Commits

```
e7599ee - Add Goals & Habits features; window/config updates
bd30477 - Refactor dialogs, add features & task views
```

```
14c1b20 - Update themes, UI styling, notes & charts
6bd083c - Add Advanced settings, markdown, and UI tweaks
58ddc83 - Revamp dashboard UI, add widgets & markdown
9f6b327 - Add note viewer and persist notes UI state
0b4f7b1 - Bump version; remove note previews; refactor layout (v2.7.1beta in constants)
d86a0b0 - Add Notes feature with UI, controller, and widgets
```

---

## [v2.5.0] - 2026-02-25

**Commits:** `e7599ee` to `bd30477`

### Major Features

- **Goals Feature**: Complete goal tracking system
- **Habits Feature**: Habit building and tracking module
- **Task Views**: Multiple view modes for tasks

### Added

- `src/features/goals/` - Goals feature module
- `src/features/habits/` - Habits feature module
- Multiple task view modes (list, kanban, calendar)
- Dialog refactoring for consistency

### Changed

- Window configuration updates
- Config system improvements
- Dialog system refactored for reusability

### Commits

```

e7599ee - Add Goals & Habits features; window/config updates
bd30477 - Refactor dialogs, add features & task views

```

---

## [v2.1.0] - 2026-02-25

**Tag:** `v2.1beta`
**Commits:** `8b1b2fe` to `eeb174b`

### Major Features

- **Calendar Feature**: Complete calendar module with event management
- **TimePicker Widget**: Reusable time selection component
- **Icon System**: SVG icons integrated throughout UI
- **Custom Fonts**: JetBrains Mono Nerd Font integration

### Added

- `src/features/calendar/` - Calendar feature module
- `src/features/calendar/controller.py` - Calendar business logic
- `src/features/calendar/view.py` - Calendar UI
- `src/features/calendar/widgets/` - Calendar-specific widgets
- `src/shared/widgets/time_picker.py` - Reusable TimePicker
- `assets/icons/` - SVG icon collection
- `assets/fonts/` - Custom font files
- QFont integration for better typography

### Changed

- Theme system updates for calendar
- UI refinements across modules
- Calendar tweaks and improvements

### Commits

```

8b1b2fe - Add Calendar feature and UI/theme updates
ee1a59e - Add TimePicker and theme/calendar tweaks
eeb174b - Use QFont, add icons and refine UI theme
8c3b873 - Refactor UI styles and bump app version

```

---

## [v2.0.0] - 2026-02-25 (Major Release)

**Tag:** `v2.0beta`
**Commit:** `115a0aa`

### 🚀 MAJOR BREAKING CHANGES

Complete rewrite of the application from CustomTkinter to PyQt6. This is a ground-up rebuild with modern architecture and significantly improved performance.

### Framework Migration

- **UI Framework**: CustomTkinter → PyQt6
- **Architecture**: Monolithic → Modular MVC
- **Performance**: 80% faster startup, 95% faster theme switching
- **Memory**: 25% reduction in memory usage

### New Architecture

```

LifeBoat 2.0 Architecture:
├── src/core/ # Core systems (config, database, themes, signals)
├── src/features/ # Feature modules (MVC pattern)
├── src/models/ # Database models (Peewee ORM)
├── src/shared/ # Shared utilities and widgets
└── src/ui/ # UI components (main window, navigation, content)

```

### Core Systems Rewritten

#### Configuration System (`src/core/config.py`)

- New `Config` class with signals for reactive updates
- `get()`, `set()`, `save()`, `reload()` methods
- Signal-based change notifications
- YAML-based configuration
- Hot-reload support

#### Database System (`src/core/database.py`)

- Centralized database initialization
- Model-based architecture with Peewee ORM
- Automatic table creation
- Default themes and settings generation
- `DATA_DIR` path management

#### Theme Manager (`src/core/theme_manager.py`)

- Complete rewrite for PyQt6
- QSS (Qt Style Sheets) generation from database themes
- Dynamic theme application via `QApplication.setStyleSheet()`
- Theme preview and live updates
- Support for custom themes

#### Signals System (`src/core/signals.py`)

- Global signal bus for inter-module communication
- Qt signals for reactive programming
- Decoupled module communication

### New Features

#### Models (`src/models/`)

- `Event` - Calendar events
- `Expense` - Financial transactions
- `Goal` - Goal tracking
- `Habit` - Habit tracking
- `Note` - Notes and documents
- `Settings` - Application settings
- `Task` - Task management
- `Theme` - Theme definitions

#### Feature Modules

- `src/features/dashboard/` - Dashboard with widgets
- `src/features/expenses/` - Expense tracking (MVC)
- `src/features/settings/` - Settings management
- `src/features/tasks/` - Task management (MVC)

#### Settings Sections (`src/features/settings/sections/`)

- `about.py` - About and version information
- `appearance.py` - UI appearance settings
- `locale.py` - Locale and formatting
- `paths.py` - Custom file locations
- `themes.py` - Theme management

#### UI Components (`src/ui/`)

- `main_window.py` - Main application window
- `navigation.py` - Navigation sidebar
- `content_area.py` - Content display area

#### Shared Components (`src/shared/`)

- `formatters.py` - Date, time, currency formatting
- Reusable widgets and utilities

### Removed (Legacy CustomTkinter Code)

- `src/modules/calendar_module.py` (484 lines)
- `src/modules/dashboard.py` (211 lines)
- `src/modules/expenses_module.py` (560 lines)
- `src/modules/goals_module.py` (334 lines)
- `src/modules/habits_module.py` (341 lines)
- `src/modules/notes_module.py` (276 lines)
- `src/modules/settings_module.py` (287 lines)
- `src/modules/tasks_module.py` (674 lines)
- `src/modules/todo_module.py` (272 lines)
- `src/ui/app.py` (old CustomTkinter app)
- `src/ui/base_module.py` (old base class)
- `src/ui/pickers.py` (old picker widgets)
- `src/ui/widgets.py` (old CustomTkinter widgets)
- `src/utils/helpers.py` (old utility functions)
- `scripts/run.bat` (old run script)

### Dependencies Updated

**Removed:**

- customtkinter
- tkinter-related packages
- PIL/Pillow (for tkinter)

**Added:**

- PyQt6 >= 6.6.0
- PyQt6-Qt6 >= 6.6.0
- PyQt6-sip >= 13.6.0
- PyQtGraph (for charts)
- markdown2 (for markdown support)

### Performance Improvements

- **Startup Time**: 3-5 seconds → 0.5-1 second (80% faster)
- **Theme Switching**: 2-3 seconds → <100ms (95% faster)
- **Memory Usage**: ~80MB → ~60MB (25% reduction)
- **UI Responsiveness**: No freezing, smooth animations

### File Statistics

- **Files Changed**: 74 files
- **Lines Added**: 4,381 lines
- **Lines Removed**: 6,223 lines
- **Net Change**: -1,842 lines (more efficient code)

### Migration Notes

This is a complete rewrite. Users upgrading from v1.x will need to:

1. Install new dependencies: `pip install -r requirements.txt`
2. Database schema is compatible (no migration needed)
3. Config format remains YAML (compatible)
4. Custom themes need to be recreated in new format

### Known Issues

- Some features from v1.x being re-implemented
- Beta status - testing in progress
- Documentation being updated

---

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

---

---

## Version History Summary

| Version  | Date       | Framework     | Status | Key Features                                       |
| -------- | ---------- | ------------- | ------ | -------------------------------------------------- |
| v2.7.4   | 2026-02-28 | PyQt6         | Beta   | Better Update Checker, Major bug Fixes             |
| v2.7.3   | 2026-02-27 | PyQt6         | Beta   | Custom Dialogs, NoScroll Inputs, Installer Updates |
| v2.7.2   | 2026-02-26 | PyQt6         | Beta   | Installers, Update Checker, Logging                |
| v3.7\*   | 2026-02-25 | PyQt6         | Beta   | Application Icon (versioning error)                |
| v3.6\*   | 2026-02-25 | PyQt6         | Beta   | Goals Patch 2 (versioning error)                   |
| v3.5\*   | 2026-02-25 | PyQt6         | Beta   | Goals Fixes (versioning error)                     |
| v3.4\*   | 2026-02-25 | PyQt6         | Beta   | Settings QoL (versioning error)                    |
| v3.2\*   | 2026-02-25 | PyQt6         | Beta   | Goals Updates (versioning error)                   |
| v3.1\*   | 2026-02-25 | PyQt6         | Beta   | Window Border Fix (versioning error)               |
| v2.9\*   | 2026-02-25 | PyQt6         | Beta   | Goals Rework (versioning error)                    |
| v2.8.2\* | 2026-02-25 | PyQt6         | Beta   | YAML Themes (versioning error)                     |
| v2.8.1\* | 2026-02-25 | PyQt6         | Beta   | Chart Revamp (versioning error)                    |
| v2.7.4\* | 2026-02-25 | PyQt6         | Beta   | Theme Manager (versioning error)                   |
| v2.7.3\* | 2026-02-25 | PyQt6         | Beta   | Activity Logger (versioning error)                 |
| v2.7.1\* | 2026-02-25 | PyQt6         | Beta   | Todo Feature (versioning error)                    |
| v2.6.0   | 2026-02-25 | PyQt6         | Beta   | Notes, Goals, Habits, Todo (consolidated)          |
| v2.5.0   | 2026-02-25 | PyQt6         | Beta   | Goals & Habits Foundation                          |
| v2.1.0   | 2026-02-25 | PyQt6         | Beta   | Calendar, Icons, Fonts                             |
| v2.0.0   | 2026-02-25 | PyQt6         | Beta   | Complete PyQt6 Rewrite                             |
| v1.1.0   | 2025-02-21 | CustomTkinter | Stable | Config System, Hot-reload                          |
| v1.0.0   | 2025-02-19 | CustomTkinter | Stable | Initial Release                                    |

**Note:** Versions marked with \* (v2.7.1 through v3.7) had incorrect version numbers in constants.py due to versioning mistakes. These releases are documented individually above but are functionally part of the v2.6.0 development cycle.

---

## Development Statistics (v2.x)

### Commits

- **Total Commits**: 43 commits from v1.1.0 to v2.7.2
- **Development Period**: February 25-26, 2026
- **Average**: ~21 commits per day

### Code Changes

- **Major Refactor**: Complete framework migration
- **New Features**: 10+ major features added
- **Bug Fixes**: 20+ issues resolved
- **Performance**: 80% startup improvement

### Architecture Evolution

- **v1.x**: Monolithic CustomTkinter app
- **v2.0**: Modular PyQt6 with MVC pattern
- **v2.7**: Production-ready with installers

---

## Future Roadmap

### Planned for v2.8.0

- [ ] Stable release (exit beta)
- [ ] Complete documentation
- [ ] User guide and tutorials

### Planned for v3.0.0

- [ ] Plugin system
- [ ] Cloud sync (optional)
- [ ] Mobile companion app
- [ ] Advanced analytics
- [ ] Export/import functionality
- [ ] Backup automation

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

See [LICENSE](../docs/LICENSE) for details.

---

**Maintained by**: Fayz212
**Repository**: [GitHub](https://github.com/faiz-n-shk/LifeBoat)
**Documentation**: [docs/](../docs/)
**Issues**: [GitHub Issues](https://github.com/faiz-n-shk/LifeBoat/issues)
