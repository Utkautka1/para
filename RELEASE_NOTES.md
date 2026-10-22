# Release Notes: Para v2.9.0

## 🚀 Overview (Commit #300 Milestone)

**Para v2.9.0** celebrates the historic **300th commit milestone** of the Para distributed academic ecosystem for college group **1-КПД-3** (KTMU College). This release introduces full-scale academic gamification: 10 dynamic attendance ranks, a group leaderboard with podium visualization, an automated catalog of **80 achievements across 8 categories**, and an interactive Mini App Student Portal.

This release also establishes **strict UI security isolation**: regular classmates are strictly presented with the Student Portal (Rankings, Achievements, and Personal Profile). Developer tools (`Swagger UI` and `Jaeger Traces`) are permanently hidden by default and appear exclusively for verified administrators and whitelisted testers.

---

## 📊 Summary of Changes: Release v2.8.0 vs Release v2.9.0

| Subsystem / Feature | Release v2.8.0 | Release v2.9.0 (Commit #300) | User & System Impact |
| :--- | :--- | :--- | :--- |
| **Telegram Mini App Portal** | Developer Swagger UI & Jaeger Traces | **Student Portal (Leaderboard, 80 Achievements, Profile)** | Classmates interact with group rankings instead of technical dev views |
| **Developer Menu Visibility** | Exposed to all users | **Strictly hidden for classmates (`display: none !important`)** | Appears only for Admin & whitelisted testers after HMAC validation |
| **Student Ranks** | None | **10 Dynamic Ranks + 80% Cult Meme Rank** | *"Любимчик старосты"*, *"ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!"*, *"Балансир"* |
| **Automated Achievements** | None | **80 Achievements across 8 categories with XP rewards** | 100% automated calculation; 0 manual burden on headman |
| **Telegram Bot Commands** | Basic schedule & attendance | **Added `/profile` and `/leaderboard`** | Student profile status card + podium leaderboard with WebApp button |
| **Alert Routing Topology** | General chat alerts | **Topic-based Forum Routing (Debug 3, Warning 5, Fatal 7)** | Clean separation of system errors by severity in Supergroup forum |
| **API Endpoints** | 11 Routers | **12 Routers: `/gamification/*` (4 public endpoints)** | Fast JSON endpoints for group pulse, leaderboard, and badge lists |
| **Test Suite Coverage** | 629 passing tests | **666 passing tests (+37 new tests)** | 100% test pass rate across all services |

---

## 🎖️ Group 1-КПД-3 Ranks

1. **👑 Любимчик старосты**: 100% посещаемость, 0 пропусков, 0 опозданий
2. **📜 Легальный отличник**: 100% посещаемость (со справками)
3. **💎 Элитный отличник**: 95–99% посещаемости
4. **⚖️ Балансир**: 90–94% посещаемости
5. **☕ Нормис**: 81–89% посещаемости
6. **🔥 ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!**: Ровно 80% посещаемости (культовый мем группы)
7. **⚠️ На грани**: 70–79% посещаемости
8. **🛑 Злостный прогульщик**: 55–69% посещаемости
9. **⚡ Кандидат на отчисление**: 40–54% посещаемости
10. **👻 Призрак КТМУ**: < 40% посещаемости

---

## 🔒 Security Architecture: Developer Menu Isolation

- **Default State**: Buttons `#tab-swagger` and `#tab-jaeger` have `style="display:none !important;"` in HTML and CSS.
- **Client Guard**: `switchTab()` blocks switching to developer tabs unless `isTester === true`.
- **Server Verification**: When Mini App initializes, Telegram `initData` is sent to `POST /miniapp/auth`. If the user is not in the Redis tester whitelist or admin list, the server returns `403 Forbidden` and the buttons remain hidden.
- **Backend Gate**: Direct HTTP requests to `/openapi.json` and `/jaeger/` require `verify_api_or_tester` dependency, returning `401 Unauthorized` for unauthorized visitors.

---

## 🛠️ Verification & Test Results

```bash
# Full test suite execution
PYTHONPATH=. pytest
# 666 passed in 6.05s (100% success rate)

# Linter and type checks
ruff check . && mypy api services bot
# All checks passed!
```
