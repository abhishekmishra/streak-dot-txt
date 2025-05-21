# Product Requirements Document (PRD): Streak.txt

## 1. Overview

**Streak.txt** is a simple, extensible tool and file format for tracking personal streaks, habits, or recurring activities. It uses plain text files for maximum portability and transparency, with optional metadata for richer tracking. The tool will provide both a reference implementation and a user-friendly command-line interface.

---

## 2. Goals

- **Track one streak per file** in a human-readable, append-only format.
- **Support metadata** (YAML front matter) for naming, period, tick, frequency, etc.
- **Allow flexible entry**: only record when the task is done; missing entries mean "not done".
- **Enable optional quantity and comments** per entry.
- **Provide a CLI tool** for managing, viewing, and analyzing streaks.
- **Support extensibility** for future features (e.g., reminders, integrations).

---

## 3. User Stories

### 3.1. As a user, I want to:
- Create a new streak file with a custom name and tick type (daily, weekly, etc.).
- Add a tick for today (or the current period) with optional quantity and comment.
- List all my streaks and see their current status, streak length, and averages.
- View detailed stats and a calendar visualization for a specific streak.
- Edit streak files manually in any text editor if desired.
- Store all streak files in a configurable directory.

---

## 4. File Format

### 4.1. Metadata (YAML Front Matter)
```yaml
---
name: Jumping Jacks
tick: Daily
period: Weekly   # Optional
frequency: 5     # Optional, e.g., 5 times per period
---
```

### 4.2. Entries
- Each line after metadata is an entry (ISO 8601 date).
- Optionally, entries can include quantity and comment:
  ```
  2025-01-05 20 reps # Felt great!
  2025-01-06 # Missed, was sick
  ```

---

## 5. Technical Requirements

- Written in Python 3, using standard libraries and `rich` for terminal output.
- Cross-platform (macOS, Linux, Windows).
- Configurable streaks directory (default: `~/streaks`).
- **The Data Access Layer (DAL) will be implemented as a FastAPI application, providing a clear API for both the CLI and potential future web services.**
- **The CLI program will consume this FastAPI application for all streak operations.**
- Append-only file operations; never delete user data.
- Modular codebase for future extensibility.

---

## 6. High Level Design

### 6.1. Data Access Layer (FastAPI)

The Data Access Layer (DAL) will be implemented as a FastAPI application. This API will serve as the single source of truth for all streak data, handling file I/O, data validation, and business logic. The CLI tool will interact with this FastAPI application. The underlying storage will remain plain text files as defined in Section 4, with the FastAPI layer managing reading from and writing to these files.

#### 6.1.1. Core Entities & Pydantic Models

We'll use Pydantic models for request/response validation and serialization.

**1. Streak:** Represents a single streak.
   - `id`: (str, e.g., `streak-jumping-jacks`) - Unique identifier, often derived from the filename.
   - `name`: (str) - Name of the streak.
   - `tick_type`: (str, e.g., "Daily", "Weekly") - The frequency of the tick.
   - `period`: (str, optional, e.g., "Weekly", "Monthly") - The overall period for the streak.
   - `frequency_in_period`: (int, optional) - Expected number of ticks within the period.
   - `created_at`: (datetime) - Timestamp of creation.
   - `updated_at`: (datetime) - Timestamp of last update.

   *Pydantic Models for Streak:*
     - `StreakBase(BaseModel)`: `name`, `tick_type`, `period` (optional), `frequency_in_period` (optional)
     - `StreakCreate(StreakBase)`: For creating new streaks.
     - `StreakUpdate(BaseModel)`: `name` (optional), `tick_type` (optional), `period` (optional), `frequency_in_period` (optional)
     - `StreakResponse(StreakBase)`: Includes `id`, `created_at`, `updated_at`.
     - `StreakDetailResponse(StreakResponse)`: Includes a list of `EntryResponse` and `StreakStatsResponse`.

**2. Entry (Tick):** Represents a single recorded instance of the activity.
   - `id`: (str, e.g., `2025-01-05`) - Unique identifier for the entry, typically the date.
   - `streak_id`: (str) - Identifier of the parent streak.
   - `date`: (date) - ISO 8601 date of the entry.
   - `quantity`: (float, optional) - Optional quantity associated with the entry.
   - `comment`: (str, optional) - Optional comment for the entry.
   - `recorded_at`: (datetime) - Timestamp of recording.

   *Pydantic Models for Entry:*
     - `EntryBase(BaseModel)`: `date`, `quantity` (optional), `comment` (optional)
     - `EntryCreate(EntryBase)`: For creating new entries.
     - `EntryUpdate(BaseModel)`: `quantity` (optional), `comment` (optional)
     - `EntryResponse(EntryBase)`: Includes `id`, `streak_id`, `recorded_at`.

**3. StreakStats:** Calculated statistics for a streak.
   - `total_days`: (int)
   - `ticked_days`: (int)
   - `unticked_days`: (int)
   - `current_streak`: (int)
   - `longest_streak`: (int)
   - `tick_average`: (float)

   *Pydantic Model for StreakStats:*
     - `StreakStatsResponse(BaseModel)`: Contains all stat fields.

#### 6.1.2. FastAPI Endpoints

**Streak Endpoints:**
- `POST /streaks/` -> `StreakResponse`: Create a new streak.
  - Request Body: `StreakCreate`
- `GET /streaks/` -> `list[StreakResponse]`: List all streaks (summary view).
- `GET /streaks/{streak_id}/` -> `StreakDetailResponse`: Get detailed information for a specific streak, including its entries and stats.
- `PUT /streaks/{streak_id}/` -> `StreakResponse`: Update an existing streak's metadata.
  - Request Body: `StreakUpdate`
- `DELETE /streaks/{streak_id}/` -> `{"message": "Streak deleted"}`: Delete a streak.

**Entry (Tick) Endpoints:**
- `POST /streaks/{streak_id}/entries/` -> `EntryResponse`: Add a new entry to a specific streak.
  - Request Body: `EntryCreate` (date will likely be part of the path or auto-set to today)
- `GET /streaks/{streak_id}/entries/` -> `list[EntryResponse]`: List all entries for a specific streak.
  - Query Params: `start_date` (optional, date), `end_date` (optional, date)
- `GET /streaks/{streak_id}/entries/{entry_date}/` -> `EntryResponse`: Get a specific entry for a streak.
- `PUT /streaks/{streak_id}/entries/{entry_date}/` -> `EntryResponse`: Update an existing entry.
  - Request Body: `EntryUpdate`
- `DELETE /streaks/{streak_id}/entries/{entry_date}/` -> `{"message": "Entry deleted"}`: Delete an entry.

**Stats Endpoints:**
- `GET /streaks/{streak_id}/stats/` -> `StreakStatsResponse`: Get calculated statistics for a specific streak.

This structure ensures that all data manipulation and business logic are centralized within the FastAPI application, promoting consistency and maintainability.

### 6.2. CLI Layer
- The CLI is a thin wrapper that calls the API for all operations.
- No direct file access in CLI code.

#### 6.2.1. Commands
- `list`: List all streaks with summary (name, tick, current streak, today's status, etc.).
- `new --name <name> [--tick <type>]`: Create a new streak file.
- `tick --name <name> [--quantity <n>] [--comment <text>]`: Add a tick for today.
- `view --name <name>`: Show detailed stats and calendar for a streak.
- `edit --name <name>`: Open the streak file in the default editor.
- `config --dir <path>`: Set or show the streaks directory.

#### 6.2.2. Output
- Rich terminal tables for summaries and stats.
- Calendar view for visualizing streaks.
- Clear error messages for ambiguous or missing streaks.

### 6.3. Web Service Layer (Future)
- A RESTful API (e.g., using Flask or FastAPI) will use the same data access API.
- Enables web, mobile, or other integrations.

---

## 7. Non-Goals

- No web or mobile UI in the initial version.
- No cloud sync or account system.
- No notifications/reminders (may be considered later).

---

## 8. Future Considerations

- Support for additional tick types (monthly, custom intervals).
- Integration with calendar apps or notification systems.
- Import/export to other formats (CSV, JSON).
- Web or GUI front-end.

---

## 9. References

- [streak-dot-txt GitHub](https://github.com/abhishekmishra/streak-dot-txt)
- [index.html documentation](docs/index.html)

---

Let me know if you want to expand any section or add more technical details!
