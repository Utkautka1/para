# Release Notes: Para v2.7.0

## 🚀 Overview

**Para v2.7.0** delivers a comprehensive architectural code overhaul, strict PEP 8 readability standards, and upstream fail-safe resilience. Every function and method across the entire codebase now adheres to a strict maximum limit of **25 lines**, features structured three-part Russian docstrings, and follows clear vertical spacing. Additionally, the system now automatically mitigates upstream TLS handshake failures from the college timetable endpoint by routing through a secondary mirror.

---

## 📊 Summary of Changes vs v2.6.0

| Dimension | Release v2.6.0 | Release v2.7.0 | Impact |
| :--- | :--- | :--- | :--- |
| **Docstrings** | Partial & English/Russian mixed | **100% Russian 3-Part Standard** | Full developer intent & edge-case visibility |
| **Function Length** | Many methods > 30 lines | **Strictly <= 25 lines** | Clean Single Responsibility & maintainability |
| **Vertical Rhythm** | Dense formatting | **Strict PEP 8 blank line spacing** | Easy to read on any display / IDE |
| **Schedule Upstream** | Fragile against TLS alert errors | **Dual-Endpoint Automated Failover** | Zero downtime when `timetable-ktmu.ru` fails |
| **Files Modified** | 18 files | **78 files** | Complete repository-wide overhaul |
| **Lines Changed** | +1,240 / -480 | **+7,179 / -1,724** | Substantial quality & documentation boost |
| **Tests Passing** | 594 / 594 (100%) | **594 / 594 (100%)** | Zero regression guaranteed |

---

## 🔍 Detailed Comparison with Version 2.6.0

### 1. Architectural Resilience & Upstream Failover
* **Problem in v2.6.0**: When the college timetable endpoint (`timetable-ktmu.ru`) returned `[SSL: TLSV1_ALERT_INTERNAL_ERROR] tlsv1 alert internal error (_ssl.c:1016)`, workers repeatedly logged warnings and relied on decaying Redis cache.
* **Resolution in v2.7.0**: Centralized `DEFAULT_FALLBACK_SCHEDULE_API_URL` (`https://nikkhl0358-max-time-f5e2.twc1.net/api/storage/schedule-data-v2`) in `config.py`. In `services/schedule_parser.py`, failures trigger an immediate seamless fallback to the mirror, resulting in HTTP 200 responses and healthy Redis cache refreshes.

### 2. Method Decomposition (< 25 Lines per Function)
* **Problem in v2.6.0**: Key handlers (`cb_start_attendance`, `cb_mark_student`, `handle_voice_or_video_note`, `cmd_start`, `execute_single_task`, `parse_file_payload`, `run_solver_loop`) mixed validation, business logic, and UI rendering into routines spanning 30 to 50 lines.
* **Resolution in v2.7.0**: Decomposed all routines into single-purpose helpers:
  - `_resolve_lesson_title_for_start`, `_ensure_session_available`, `_init_session_safe` in `bot/handlers/admin/attendance.py`
  - `_send_today_schedule`, `_greet_new_student`, `_show_access_denied`, `_show_tester_cabinet` in `bot/handlers/user/schedule.py`
  - `_check_and_acquire_voice`, `_resolve_temp_audio_dir`, `_determine_audio_extension` in `bot/handlers/user/voice_transcribe.py`
  - `_extract_docx_images`, `_read_code_file_payload`, `_drain_active_tasks` in `solver.py`
  - `_build_compact_topic_header`, `_build_topic_body_lines` in `services/attendance_topic_updater.py`

### 3. Readability & Code Style
* **Problem in v2.6.0**: Code blocks were tightly packed without blank lines between docstrings and implementation, making visual inspection cumbersome.
* **Resolution in v2.7.0**: Standardized formatting rules applied across all 78 files:
  - 1 empty line immediately following closing docstring `"""`.
  - 1 empty line before `return` or `raise`.
  - 2 empty lines between top-level declarations (PEP 8).
  - Logical guard clauses separated from main computational flow.

### 4. Configuration Consolidation
* **Problem in v2.6.0**: Some business modules used raw `os.getenv` with hardcoded defaults.
* **Resolution in v2.7.0**: All environment variables are strictly loaded, validated, and typed in `config.py` using `get_required_env`, `get_env_int`, and `get_env_list`.

---

## 🛠️ Deployment & Verification

```bash
# 1. Update source code
git pull origin main

# 2. Rebuild and launch containers
docker compose up -d --build

# 3. Verify health
docker compose ps
docker compose logs -f para-worker para-api
```
