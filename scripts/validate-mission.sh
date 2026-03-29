#!/usr/bin/env bash
# Mission Forge — Validierungsscript
# Prueft eine .mission-forge/ Struktur auf Vollstaendigkeit und Konsistenz
#
# Usage: bash scripts/validate-mission.sh [path-to-.mission-forge]
# Exit codes: 0 = OK, 1 = Fehler gefunden

set -uo pipefail

MISSION_DIR="${1:-.mission-forge}"
ERRORS=0
WARNINGS=0

# Farben nur im Terminal
if [ -t 1 ]; then
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    GREEN='\033[0;32m'
    NC='\033[0m'
else
    RED='' YELLOW='' GREEN='' NC=''
fi

error() { echo -e "${RED}[FEHLER]${NC} $1"; ERRORS=$((ERRORS + 1)); }
warn()  { echo -e "${YELLOW}[WARNUNG]${NC} $1"; WARNINGS=$((WARNINGS + 1)); }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }

# Extrahiert nur den Frontmatter-Block (zwischen erstem und zweitem ---)
extract_frontmatter() {
    sed -n '1{/^---$/!q}; 1,/^---$/{/^---$/d;p}' "$1" 2>/dev/null
}

echo "============================================"
echo "  Mission Forge — Struktur-Validierung"
echo "  Verzeichnis: $MISSION_DIR"
echo "============================================"
echo ""

# 1. Verzeichnisstruktur
echo "--- 1. Verzeichnisstruktur ---"

if [ ! -d "$MISSION_DIR" ]; then
    error "Verzeichnis $MISSION_DIR existiert nicht"
    exit 1
fi

if [ -f "$MISSION_DIR/COMPANY.md" ]; then
    ok "COMPANY.md vorhanden"
else
    error "COMPANY.md fehlt — Root-Manifest der Company"
fi

if [ -f "$MISSION_DIR/STATE.md" ]; then
    ok "STATE.md vorhanden"
else
    error "STATE.md fehlt — Single Source of Truth"
fi

for dir in teams agents tasks skills results projects; do
    if [ -d "$MISSION_DIR/$dir" ]; then
        ok "Verzeichnis $dir/ vorhanden"
    else
        warn "Verzeichnis $dir/ fehlt"
    fi
done

# 2. Manifest-Frontmatter (nur im Frontmatter-Block suchen)
echo ""
echo "--- 2. Manifest-Validierung ---"

check_frontmatter() {
    local file="$1"
    local required_fields="$2"

    if [ ! -f "$file" ]; then
        return
    fi

    # Pruefe ob Frontmatter existiert (erste UND zweite --- Zeile)
    local fm_lines
    fm_lines=$(grep -c "^---$" "$file" 2>/dev/null || echo "0")
    if [ "$fm_lines" -lt 2 ]; then
        error "$file: Kein vollstaendiges YAML-Frontmatter (braucht oeffnendes und schliessendes ---)"
        return
    fi

    local frontmatter
    frontmatter=$(extract_frontmatter "$file")

    for field in $required_fields; do
        if echo "$frontmatter" | grep -q "^${field}:"; then
            : # vorhanden
        else
            error "$file: Pflichtfeld '$field' fehlt im Frontmatter"
        fi
    done
}

# Alle Manifeste in einem find-Durchlauf sammeln
while IFS= read -r f; do
    basename_f=$(basename "$f")
    case "$basename_f" in
        COMPANY.md)
            check_frontmatter "$f" "schema kind slug name description"
            ;;
        TEAM.md)
            check_frontmatter "$f" "schema kind slug name description manager"
            ;;
        AGENTS.md)
            check_frontmatter "$f" "schema kind slug name description reports-to"
            ;;
        TASK.md)
            check_frontmatter "$f" "schema kind slug name description assigned-to status wave requirements"
            ;;
        PROJECT.md)
            check_frontmatter "$f" "schema kind slug name description"
            ;;
    esac
done < <(find "$MISSION_DIR" -maxdepth 4 -name "*.md" -not -path "*/.git/*" -not -path "*/node_modules/*" 2>/dev/null)

# 3. Traceability
echo ""
echo "--- 3. Traceability-Pruefung ---"

if [ -f "$MISSION_DIR/STATE.md" ]; then
    REQ_COUNT=$(grep -c "REQ-[0-9]" "$MISSION_DIR/STATE.md" 2>/dev/null || echo "0")
    WP_COUNT=$(grep -c "WP-[0-9]" "$MISSION_DIR/STATE.md" 2>/dev/null || echo "0")

    if [ "$REQ_COUNT" -gt 0 ]; then
        ok "Traceability-Matrix enthaelt $REQ_COUNT Anforderungen"
    else
        warn "Keine REQ-IDs in STATE.md gefunden"
    fi

    if [ "$WP_COUNT" -gt 0 ]; then
        ok "Arbeitspaket-Status enthaelt $WP_COUNT Eintraege"
    else
        warn "Keine WP-IDs in STATE.md gefunden"
    fi

    OPEN_COUNT=$(grep -c "| OPEN" "$MISSION_DIR/STATE.md" 2>/dev/null || echo "0")
    if [ "$OPEN_COUNT" -gt 0 ]; then
        warn "$OPEN_COUNT offene Eintraege in STATE.md"
    fi
fi

# 4. Ergebnisse
echo ""
echo "--- 4. Ergebnis-Dateien ---"

if [ -d "$MISSION_DIR/results" ]; then
    RESULT_COUNT=0
    while IFS= read -r _; do
        RESULT_COUNT=$((RESULT_COUNT + 1))
    done < <(find "$MISSION_DIR/results" -name "SUMMARY.md" 2>/dev/null)
    ok "$RESULT_COUNT Ergebnis-Dateien (SUMMARY.md) gefunden"
else
    warn "Kein results/ Verzeichnis — noch keine Ausfuehrung?"
fi

# 5. Verifikation
echo ""
echo "--- 5. Verifikation ---"

if [ -f "$MISSION_DIR/VERIFICATION.md" ]; then
    ok "VERIFICATION.md vorhanden"
    local_fm=$(extract_frontmatter "$MISSION_DIR/VERIFICATION.md")
    if echo "$local_fm" | grep -q "result: PASSED"; then
        ok "Verifikation: PASSED"
    elif echo "$local_fm" | grep -q "result: PARTIAL"; then
        warn "Verifikation: PARTIAL — Nacharbeit empfohlen"
    elif echo "$local_fm" | grep -q "result: FAILED"; then
        error "Verifikation: FAILED"
    fi
else
    warn "VERIFICATION.md fehlt — noch nicht verifiziert?"
fi

# 6. Cross-Referenz
echo ""
echo "--- 6. Cross-Referenz-Pruefung ---"

if [ -f "$MISSION_DIR/COMPANY.md" ]; then
    while IFS= read -r ref; do
        if [ -f "$MISSION_DIR/$ref" ]; then
            ok "Referenz $ref existiert"
        else
            error "COMPANY.md referenziert $ref — Datei fehlt"
        fi
    done < <(grep -oE "(teams|agents)/[a-z0-9_-]+/(TEAM|AGENTS)\.md" "$MISSION_DIR/COMPANY.md" 2>/dev/null)
fi

# 7. .skill Dateien in packages/
echo ""
echo "--- 7. Exportierte .skill Dateien ---"

PACKAGES_DIR="$(dirname "$MISSION_DIR")/packages"
if [ -d "$PACKAGES_DIR" ]; then
    SKILL_COUNT=0
    while IFS= read -r sf; do
        SKILL_COUNT=$((SKILL_COUNT + 1))
        check_frontmatter "$sf" "name description"
    done < <(find "$PACKAGES_DIR" -name "*.skill" 2>/dev/null)
    ok "$SKILL_COUNT exportierte .skill Dateien gefunden"
else
    warn "Kein packages/ Verzeichnis — noch keine Exports"
fi

# Zusammenfassung
echo ""
echo "============================================"
echo "  Zusammenfassung"
echo "============================================"
echo -e "  Fehler:    ${RED}$ERRORS${NC}"
echo -e "  Warnungen: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}Mission-Struktur ist valide.${NC}"
    exit 0
else
    echo -e "${RED}$ERRORS Fehler gefunden. Bitte beheben.${NC}"
    exit 1
fi
