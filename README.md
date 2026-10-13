# Project 67

> **A deep Grand Strategy game with tactical warfare, set in a fictional world.**

---

## Long-Term Vision

Project 67 combines the best pillars of classic grand strategy and 4X genres into a unified, modular simulation:

- **Hexagonal World & Societal Evolution** (*Civilization-inspired*): Territorial progression, education, engineering, technology milestones, and ideological development.
- **Deep Tactical Warfare & Logistical Operations** (*Hearts of Iron IV-inspired*): Dynamic frontlines, combat width, terrain modifiers, unit designer, equipment manufacturing, and multi-node supply propagation networks.
- **Deep Macroeconomic Simulation** (*Victoria-inspired*): GDP, monetary inflation, unemployment rates, consumption needs, taxation policies, sovereign debt, and international trade (weapons, food, raw materials).
- **Geopolitical & Modular Diplomacy** (*Stellaris + HOI4-inspired*): Bilateral relations, envoys/delegates, economic and military blocs, open/closed migration laws, lend-lease programs, and proxy wars.
- **Asymmetric & Irregular Warfare**: Covert infiltration units, sabotage of supply routes, guerrilla networks (winning through attrition without massive armies), and systemic corruption as a geopolitical weapon.
- **No Paid DLCs Philosophy**: All gameplay features, expansions, and mechanical evolutions are included in the base game through free rolling updates and major version releases.

---

## Development Philosophy

These ten rules are non-negotiable principles guiding every development decision:

1. **MVP First, OOP Later**: Make it work first, refactor into clean abstractions later.
2. **No Dead Code**: If code is not being executed, it doesn't belong here. Delete it immediately.
3. **Data Model Prepared for the Future**: The foundational schema supports future depth, while keeping current content minimal.
4. **Incremental Modularization**: Extract classes and modules when pain points emerge, not prematurely.
5. **One Commit, One Purpose**: Refactoring means moving and reorganizing code, not rewriting behavior.
6. **Feature Branches**: Never push untested features directly to `main`.
7. **Every Version Is a Complete Game**: No half-baked release states; each version must be fully playable.
8. **Data in JSON, Generic Code**: Avoid hardcoded logic (e.g., no `if terrain == "forest"` in game engines).
9. **Discrete Simulation Ticks**: No variable continuous delta time (`dt`) for simulation logic; ticks are decoupled from visual framerates (FPS).
10. **Play Every Version**: If the developers don't find it engaging, no one else will.

---

## Version Roadmap

| Version | Focus / Milestone | Est. Duration | Target Deliverables / Definition of Done |
| :--- | :--- | :--- | :--- |
| **`v0.1`** | **Technical Prototype** | 5–10 days | Pygame window, axial hex grid coordinates, camera pan/zoom, mouse hex raycast & selection. |
| **`v0.2`** | **Supply Network** | 7–10 days | Node/edge logistics network, BFS/Dijkstra propagation, link toggle/cut mechanics affecting downstream hexes. |
| **`v0.3`** | **Construction & Base Economy** | 7–10 days | JSON-driven terrains & buildings, turn/tick build costs, primary resource (**Gold**) production HUD. |
| **`v0.4`** | **Units & Order Queue** | 10–14 days | JSON unit template, A* hex pathfinding, move/wait/cancel queues, supply consumption & attrition penalties. |
| **`v0.5`** | **Basic Combat & Game Loop** | 10–14 days | 2 factions, adjacent hex combat formulas (terrain & morale factors), win/loss state conditions. |
| **`v1.0`** | **First Playable Release** | 2–4 months | Clean OOP refactor, minimal AI, main menu, save/load system, audio/sprites polish, publishable on Itch/Steam Early Access. |
| **`v1.5`** | **Military Depth** | 4–6 months | Custom unit designer, arms manufacturing, military doctrines, frontline systems, combat reserves. |
| **`v2.0`** | **Deep Economy** | 6–12 months | GDP, inflation dynamics, unemployment, market goods, economic laws, sovereign loans & international trade. |
| **`v2.5`** | **Geopolitics & Diplomacy** | 4–6 months | Diplomatic delegations, defensive pacts, economic customs unions, lend-lease, immigration laws. |
| **`v3.0`** | **Society & Ideology** | 6–12 months | Education & school infrastructure, engineering stat, research tiers, state corruption, societal evolution. |
| **`v3.5`** | **Asymmetric Warfare** | 4–6 months | Sabotage units, supply line cut tactics, guerrilla warfare, intelligence ops, covert destabilization. |
| **`v4.0+`** | **Future Horizons** | Ongoing | Procedural world generation, multiplayer networking, modding API, and map editor. |

---

## Tech Stack & Requirements

- **Language:** Python 3.10+
- **Primary Engine/Library:** Pygame
- **Data Serialization:** JSON
- **Pathfinding & Graph Logic:** Dijkstra / A* over axial hexagonal coordinates

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/<your-org>/67-project.git
cd 67-project
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies & Run
```bash
pip install pygame
python main.py
```

---

## Project Status

- **Current Version:** `v0.1` (Design & Planning Phase)
- **Next Milestone:** Finalize `docs/diseño.md` and start implementation of `v0.1` (Technical Hex Prototype).
- **Core Team:** 2 developers
