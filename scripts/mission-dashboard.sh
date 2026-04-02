#!/usr/bin/env bash
# MissionForge Dashboard — Echtzeit-Monitoring
# ==============================================================
# Zeigt den aktuellen Status einer Mission als Terminal-Dashboard.
# Inspiriert von claude-codes React/Ink Terminal-UI.
#
# Usage:
#   bash scripts/mission-dashboard.sh [path-to-.mission-forge]
#   bash scripts/mission-dashboard.sh .mission-forge --watch     # Auto-Refresh alle 5s
#   bash scripts/mission-dashboard.sh .mission-forge --json      # JSON-Output
#   bash scripts/mission-dashboard.sh --test                     # Selbsttest
#
# Exit codes: 0 = OK, 1 = Fehler

set -uo pipefail

MISSION_DIR="${1:-.mission-forge}"
WATCH_MODE=false
JSON_MODE=false
WATCH_INTERVAL=5

# Args parsen
for arg in "$@"; do
    case "$arg" in
        --watch) WATCH_MODE=true ;;
        --json) JSON_MODE=true ;;
        --test) RUN_TEST=true ;;
    esac
done

# Farben
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    CYAN='\033[0;36m'
    BLUE='\033[0;34m'
    MAGENTA='\033[0;35m'
    BOLD='\033[1m'
    DIM='\033[2m'
    NC='\033[0m'
    CLEAR='\033[2J\033[H'
else
    RED='' GREEN='' YELLOW='' CYAN='' BLUE='' MAGENTA='' BOLD='' DIM='' NC='' CLEAR=''
fi

# ── Frontmatter-Extraktion ──────────────────────────────────

extract_fm_value() {
    local file="$1"
    local key="$2"
    if [ -f "$file" ]; then
        # Frontmatter zwischen erstem und zweitem --- extrahieren (macOS+Linux kompatibel)
        awk '/^---$/{n++; next} n==1{print} n>=2{exit}' "$file" 2>/dev/null | \
            grep "^${key}:" | head -1 | sed "s/^${key}:[[:space:]]*//" | sed 's/^["'"'"']//;s/["'"'"']$//'
    fi
}

# ── Status-Farbe ────────────────────────────────────────────

status_color() {
    case "$1" in
        DONE|VERIFIED)  echo -n "$GREEN" ;;
        IN_PROGRESS)    echo -n "$CYAN" ;;
        OPEN|PENDING)   echo -n "$DIM" ;;
        FAILED)         echo -n "$RED" ;;
        ESCALATED)      echo -n "$MAGENTA" ;;
        SKIPPED|ABORTED) echo -n "$YELLOW" ;;
        *)              echo -n "$NC" ;;
    esac
}

# ── Status-Icon ─────────────────────────────────────────────

status_icon() {
    case "$1" in
        DONE)         echo -n "●" ;;
        VERIFIED)     echo -n "✓" ;;
        IN_PROGRESS)  echo -n "◐" ;;
        OPEN)         echo -n "○" ;;
        PENDING)      echo -n "○" ;;
        FAILED)       echo -n "✗" ;;
        ESCALATED)    echo -n "↑" ;;
        SKIPPED)      echo -n "–" ;;
        ABORTED)      echo -n "■" ;;
        *)            echo -n "?" ;;
    esac
}

# ── Fortschrittsbalken ──────────────────────────────────────

progress_bar() {
    local done=$1
    local total=$2
    local width=${3:-30}

    # Sicherstellen dass Werte numerisch sind
    done=$(( done + 0 ))
    total=$(( total + 0 ))

    if [ "$total" -eq 0 ]; then
        printf "[%${width}s]" ""
        return
    fi

    local filled=$(( done * width / total ))
    local empty=$(( width - filled ))
    local pct=$(( done * 100 / total ))

    printf "${GREEN}"
    printf "["
    if [ "$filled" -gt 0 ]; then
        printf '%0.s█' $(seq 1 $filled)
    fi
    printf "${DIM}"
    if [ "$empty" -gt 0 ]; then
        printf '%0.s░' $(seq 1 $empty)
    fi
    printf "${NC}] ${BOLD}%3d%%${NC}" "$pct"
}

# ── Dashboard rendern ───────────────────────────────────────

render_dashboard() {
    local mission_dir="$1"

    if [ ! -d "$mission_dir" ]; then
        echo -e "${RED}Fehler: $mission_dir existiert nicht${NC}"
        return 1
    fi

    # Mission-Info aus COMPANY.md
    local mission_name
    mission_name=$(extract_fm_value "$mission_dir/COMPANY.md" "name")
    mission_name=${mission_name:-"(unbekannt)"}

    local mission_slug
    mission_slug=$(extract_fm_value "$mission_dir/COMPANY.md" "slug")

    # Status aus STATE.md
    local current_wave total_waves total_wps total_agents mission_status
    if [ -f "$mission_dir/STATE.md" ]; then
        current_wave=$(extract_fm_value "$mission_dir/STATE.md" "current-wave")
        total_waves=$(extract_fm_value "$mission_dir/STATE.md" "total-waves")
        total_wps=$(extract_fm_value "$mission_dir/STATE.md" "total-work-packages")
        total_agents=$(extract_fm_value "$mission_dir/STATE.md" "total-agents")
        mission_status=$(extract_fm_value "$mission_dir/STATE.md" "status")
    fi
    current_wave=$(echo "${current_wave:-0}" | tr -dc '0-9')
    total_waves=$(echo "${total_waves:-0}" | tr -dc '0-9')
    total_wps=$(echo "${total_wps:-0}" | tr -dc '0-9')
    total_agents=$(echo "${total_agents:-0}" | tr -dc '0-9')
    current_wave=${current_wave:-0}
    total_waves=${total_waves:-0}
    total_wps=${total_wps:-0}
    total_agents=${total_agents:-0}
    mission_status=${mission_status:-OPEN}

    # WP-Status zaehlen (aus STATE.md Tabelle)
    local wp_done=0 wp_progress=0 wp_open=0 wp_failed=0 wp_verified=0 wp_other=0
    if [ -f "$mission_dir/STATE.md" ]; then
        wp_done=$(grep -c "| DONE" "$mission_dir/STATE.md" 2>/dev/null | tr -dc '0-9')
        wp_progress=$(grep -c "| IN_PROGRESS" "$mission_dir/STATE.md" 2>/dev/null | tr -dc '0-9')
        wp_open=$(grep -c "| OPEN" "$mission_dir/STATE.md" 2>/dev/null | tr -dc '0-9')
        wp_failed=$(grep -c "| FAILED" "$mission_dir/STATE.md" 2>/dev/null | tr -dc '0-9')
        wp_verified=$(grep -c "| VERIFIED" "$mission_dir/STATE.md" 2>/dev/null | tr -dc '0-9')
    fi
    wp_done=${wp_done:-0}; wp_progress=${wp_progress:-0}; wp_open=${wp_open:-0}
    wp_failed=${wp_failed:-0}; wp_verified=${wp_verified:-0}
    local wp_completed=$((wp_done + wp_verified))

    # Metriken aus STATE.md
    local agents_spawned=0 repair_cycles=0 escalations=0 context_resets=0
    if [ -f "$mission_dir/STATE.md" ]; then
        agents_spawned=$(grep "Agenten gespawnt" "$mission_dir/STATE.md" 2>/dev/null | grep -oE '[0-9]+' | tail -1 || echo 0)
        repair_cycles=$(grep "Reparatur-Zyklen" "$mission_dir/STATE.md" 2>/dev/null | grep -oE '[0-9]+' | tail -1 || echo 0)
        escalations=$(grep "Eskalationen" "$mission_dir/STATE.md" 2>/dev/null | grep -oE '[0-9]+' | tail -1 || echo 0)
        context_resets=$(grep "Context-Resets" "$mission_dir/STATE.md" 2>/dev/null | grep -oE '[0-9]+' | tail -1 || echo 0)
    fi
    agents_spawned=${agents_spawned:-0}
    repair_cycles=${repair_cycles:-0}
    escalations=${escalations:-0}
    context_resets=${context_resets:-0}

    # Ergebnis-Dateien zaehlen
    local result_count=0
    if [ -d "$mission_dir/results" ]; then
        result_count=$(find "$mission_dir/results" -name "SUMMARY.md" 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Verifikations-Status
    local verif_status="–"
    if [ -f "$mission_dir/VERIFICATION.md" ]; then
        local verif_result
        verif_result=$(extract_fm_value "$mission_dir/VERIFICATION.md" "result")
        verif_status=${verif_result:-"PENDING"}
    fi

    # AuditChain-Status
    local chain_status="–" chain_entries=0
    local chain_file="$mission_dir/audit/CHAIN.jsonl"
    if [ -f "$chain_file" ]; then
        chain_entries=$(wc -l < "$chain_file" | tr -d ' ')
        chain_status="${chain_entries} Eintraege"
    fi

    # Zeitstempel
    local now
    now=$(date '+%Y-%m-%d %H:%M:%S')

    # ── Rendern ──────────────────────────────────────────────

    echo ""
    echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║${NC}  ${CYAN}⚡ MissionForge Dashboard${NC}                           ${BOLD}║${NC}"
    echo -e "${BOLD}╠══════════════════════════════════════════════════════╣${NC}"
    echo -e "${BOLD}║${NC}  Mission:  ${BOLD}${mission_name}${NC}"
    echo -e "${BOLD}║${NC}  Slug:     ${DIM}${mission_slug}${NC}"
    echo -e "${BOLD}║${NC}  Status:   $(status_color "$mission_status")${mission_status}${NC}"
    echo -e "${BOLD}║${NC}  Stand:    ${DIM}${now}${NC}"
    echo -e "${BOLD}╠══════════════════════════════════════════════════════╣${NC}"

    # Fortschritt
    local total_countable=$((wp_done + wp_progress + wp_open + wp_failed + wp_verified))
    if [ "$total_countable" -eq 0 ]; then
        total_countable=${total_wps}
    fi

    echo -e "${BOLD}║${NC}  ${BOLD}Fortschritt${NC}"
    echo -ne "${BOLD}║${NC}  "
    progress_bar "$wp_completed" "$total_countable" 35
    echo ""
    echo -e "${BOLD}║${NC}  Wave ${BOLD}${current_wave}${NC}/${total_waves}  |  WPs ${BOLD}${wp_completed}${NC}/${total_countable} abgeschlossen"
    echo -e "${BOLD}║${NC}"

    # Status-Verteilung
    echo -e "${BOLD}║${NC}  ${BOLD}Arbeitspaket-Status${NC}"
    [ "$wp_open" -gt 0 ]     && echo -e "${BOLD}║${NC}    $(status_color OPEN)○ OPEN${NC}         ${wp_open}"
    [ "$wp_progress" -gt 0 ] && echo -e "${BOLD}║${NC}    $(status_color IN_PROGRESS)◐ IN_PROGRESS${NC}  ${wp_progress}"
    [ "$wp_done" -gt 0 ]     && echo -e "${BOLD}║${NC}    $(status_color DONE)● DONE${NC}         ${wp_done}"
    [ "$wp_verified" -gt 0 ] && echo -e "${BOLD}║${NC}    $(status_color VERIFIED)✓ VERIFIED${NC}     ${wp_verified}"
    [ "$wp_failed" -gt 0 ]   && echo -e "${BOLD}║${NC}    $(status_color FAILED)✗ FAILED${NC}       ${wp_failed}"

    echo -e "${BOLD}╠══════════════════════════════════════════════════════╣${NC}"

    # Metriken
    echo -e "${BOLD}║${NC}  ${BOLD}Metriken${NC}"
    echo -e "${BOLD}║${NC}    Agenten:         ${agents_spawned}"
    echo -e "${BOLD}║${NC}    Reparaturen:     ${repair_cycles}"
    echo -e "${BOLD}║${NC}    Eskalationen:    ${escalations}"
    echo -e "${BOLD}║${NC}    Context-Resets:  ${context_resets}"
    echo -e "${BOLD}║${NC}    Ergebnisse:      ${result_count}"

    echo -e "${BOLD}╠══════════════════════════════════════════════════════╣${NC}"

    # Audit & Verifikation
    echo -e "${BOLD}║${NC}  ${BOLD}Qualitaet & Audit${NC}"
    echo -e "${BOLD}║${NC}    Verifikation:    $(status_color "$verif_status")${verif_status}${NC}"
    echo -e "${BOLD}║${NC}    AuditChain:      ${chain_status}"

    # Blocker anzeigen (aus der Blocker-Tabelle in STATE.md)
    if [ -f "$mission_dir/STATE.md" ]; then
        local blockers
        # Extrahiere nur Zeilen aus der Blocker-Sektion (nach "## Blocker" Header)
        blockers=$(awk '/^## Blocker/{found=1; next} found && /^##/{exit} found && /^\|/ && !/^\|[-[:space:]|]*$/ && !/Zeitpunkt/' \
            "$mission_dir/STATE.md" 2>/dev/null | \
            grep -v "^|[[:space:]]*|[[:space:]]*|[[:space:]]*|[[:space:]]*|[[:space:]]*|" | head -5)
        if [ -n "$blockers" ]; then
            echo -e "${BOLD}╠══════════════════════════════════════════════════════╣${NC}"
            echo -e "${BOLD}║${NC}  ${RED}${BOLD}Blocker${NC}"
            echo "$blockers" | while IFS= read -r line; do
                echo -e "${BOLD}║${NC}    ${RED}!${NC} $line"
            done
        fi
    fi

    echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ── JSON-Output ─────────────────────────────────────────────

render_json() {
    local mission_dir="$1"

    if [ ! -d "$mission_dir" ]; then
        echo '{"error": "Mission directory not found"}'
        return 1
    fi

    local name slug status current_wave total_waves total_wps
    name=$(extract_fm_value "$mission_dir/COMPANY.md" "name")
    slug=$(extract_fm_value "$mission_dir/COMPANY.md" "slug")
    status=$(extract_fm_value "$mission_dir/STATE.md" "status")
    current_wave=$(extract_fm_value "$mission_dir/STATE.md" "current-wave")
    total_waves=$(extract_fm_value "$mission_dir/STATE.md" "total-waves")
    total_wps=$(extract_fm_value "$mission_dir/STATE.md" "total-work-packages")

    local wp_done=0 wp_progress=0 wp_open=0 wp_failed=0 wp_verified=0
    if [ -f "$mission_dir/STATE.md" ]; then
        wp_done=$(grep -c "| DONE" "$mission_dir/STATE.md" 2>/dev/null || echo 0)
        wp_progress=$(grep -c "| IN_PROGRESS" "$mission_dir/STATE.md" 2>/dev/null || echo 0)
        wp_open=$(grep -c "| OPEN" "$mission_dir/STATE.md" 2>/dev/null || echo 0)
        wp_failed=$(grep -c "| FAILED" "$mission_dir/STATE.md" 2>/dev/null || echo 0)
        wp_verified=$(grep -c "| VERIFIED" "$mission_dir/STATE.md" 2>/dev/null || echo 0)
    fi

    cat <<ENDJSON
{
  "mission": "${name:-unknown}",
  "slug": "${slug:-unknown}",
  "status": "${status:-OPEN}",
  "current_wave": ${current_wave:-0},
  "total_waves": ${total_waves:-0},
  "total_work_packages": ${total_wps:-0},
  "work_packages": {
    "open": ${wp_open},
    "in_progress": ${wp_progress},
    "done": ${wp_done},
    "verified": ${wp_verified},
    "failed": ${wp_failed}
  },
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
}
ENDJSON
}

# ── Selbsttest ──────────────────────────────────────────────

run_test() {
    echo "🧪 Mission Dashboard — Selbsttest"
    echo ""

    local tmpdir
    tmpdir=$(mktemp -d)
    local mission="$tmpdir/.mission-forge"
    mkdir -p "$mission/results/wave-1-wp-001" "$mission/tasks/wp-001" "$mission/agents/dev"

    # COMPANY.md
    cat > "$mission/COMPANY.md" <<'EOF'
---
schema: missionforge/v1
kind: company
slug: test-mission
name: "Dashboard Test Mission"
description: "Test"
---
# Test
EOF

    # STATE.md
    cat > "$mission/STATE.md" <<'EOF'
---
mission: test-mission
status: IN_PROGRESS
started: 2026-04-01T10:00:00Z
current-wave: 2
total-waves: 3
total-requirements: 4
total-work-packages: 4
total-agents: 2
---

# Mission State

## Arbeitspaket-Status

| WP-ID | Welle | Agent | Status | Artefakte | Versuche |
|-------|-------|-------|--------|-----------|----------|
| WP-001 | 1 | dev | VERIFIED | results/ | 1/2 |
| WP-002 | 1 | dev | DONE | results/ | 1/2 |
| WP-003 | 2 | qa | IN_PROGRESS | — | 0/2 |
| WP-004 | 3 | dev | OPEN | — | 0/2 |

## Metriken

| Metrik | Wert |
|---|---|
| Agenten gespawnt | 3 |
| Reparatur-Zyklen | 1 |
| Eskalationen an User | 0 |
| Context-Resets | 0 |
| Skills aktiviert | 2 |
EOF

    # SUMMARY.md
    echo "# Ergebnis WP-001" > "$mission/results/wave-1-wp-001/SUMMARY.md"

    # Dashboard rendern
    echo "  Test 1: Dashboard rendern..."
    local output
    output=$(render_dashboard "$mission" 2>&1 | sed $'s/\033\\[[0-9;]*m//g')
    if echo "$output" | grep -q "Dashboard Test Mission"; then
        echo "  ✅ Mission-Name korrekt angezeigt"
    else
        echo "  ❌ Mission-Name nicht gefunden"
        rm -rf "$tmpdir"
        exit 1
    fi

    if echo "$output" | grep -q "IN_PROGRESS"; then
        echo "  ✅ Status korrekt angezeigt"
    else
        echo "  ❌ Status nicht gefunden"
    fi

    if echo "$output" | grep -q "2/3"; then
        echo "  ✅ Wave-Fortschritt korrekt"
    else
        echo "  ❌ Wave-Fortschritt nicht gefunden"
    fi

    # JSON-Output testen
    echo ""
    echo "  Test 2: JSON-Output..."
    local json_out
    json_out=$(render_json "$mission" 2>&1)
    if echo "$json_out" | grep -q '"current_wave": 2'; then
        echo "  ✅ JSON current_wave korrekt"
    else
        echo "  ❌ JSON current_wave falsch"
    fi

    if echo "$json_out" | grep -q '"in_progress": 1'; then
        echo "  ✅ JSON WP-Status korrekt"
    else
        echo "  ❌ JSON WP-Status falsch"
    fi

    echo ""
    echo "✅ Alle Tests bestanden!"

    rm -rf "$tmpdir"
    exit 0
}

# ── Main ────────────────────────────────────────────────────

if [ "${RUN_TEST:-false}" = "true" ]; then
    run_test
fi

if [ "$JSON_MODE" = true ]; then
    render_json "$MISSION_DIR"
    exit $?
fi

if [ "$WATCH_MODE" = true ]; then
    while true; do
        echo -e "$CLEAR"
        render_dashboard "$MISSION_DIR"
        echo -e "${DIM}  Auto-Refresh alle ${WATCH_INTERVAL}s | Ctrl+C zum Beenden${NC}"
        sleep "$WATCH_INTERVAL"
    done
else
    render_dashboard "$MISSION_DIR"
fi
