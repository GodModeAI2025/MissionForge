# Fehlerbehebung — Mission Forge

| Problem                              | Ursache                                    | Loesung                                        |
|--------------------------------------|--------------------------------------------|-------------------------------------------------|
| Agent liefert kein Ergebnis          | Context-Limit erreicht                     | WP weiter zerlegen, weniger Kontext laden       |
| Zirkulaere Abhaengigkeit             | WP-Graph hat Zyklen                        | Abhaengigkeiten neu analysieren, Zyklus brechen |
| Skill wird nicht aktiviert           | Beschreibung matcht nicht                  | Trigger-Woerter in Skill-Description anpassen   |
| REQ ohne WP nach Zerlegung           | Anforderung vergessen                      | Traceability-Matrix erneut pruefen              |
| Reparatur-Zyklen erschoepft          | Grundlegendes Design-Problem               | An User eskalieren, WP-Scope anpassen           |
| Sub-Orchestrator blockiert           | Wartet auf fehlende Vorbedingung           | STATE.md pruefen, fehlende Welle identifizieren |
| Doppelte Arbeit zwischen Agenten     | Unklare Abgrenzung in AGENTS.md            | Verantwortungsbereiche schaerfen                |
| Qualitaet unter Erwartung            | Falsches Model-Level fuer Komplexitaet     | Model-Preference im AGENTS.md hochstufen        |
| Export-Package funktioniert nicht    | Aufgabenspezifische Werte nicht ersetzt    | Alle Hardcoded-Werte durch Platzhalter ersetzen |
| Re-Spawn findet Package nicht        | Falscher Pfad oder fehlende Registry       | packages/REGISTRY.md pruefen                    |
