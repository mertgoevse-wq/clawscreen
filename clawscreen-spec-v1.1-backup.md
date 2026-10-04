# ClawScreen — Produktspezifikation (Spec)

**Version:** 1.1 · **Datum:** 2026-10-04 · **Status:** Baureif (spec-complete, noch nichts gebaut)
**Änderungshistorie:** v1.0 Erstfassung nach Interview. v1.1 Nutzernachtrag: globaler Skill-Betrieb, Git-Disziplin (Commit+Push je Aufgabe), Crash-Recovery („resume"), 50+ Referenz-Repos, Ein-Durchlauf-Bau, Anti-AI-Slop-Standard, UI-Design-Skills → neues Kapitel §14, neue Aufgaben CS-005/CS-006, erweiterte Abnahme-Kriterien.

> **Leseweg für Claude Code (Bau-Verstand):**
> 1) §2 = die 21 verbindlichen Nutzer-Entscheidungen — nicht verhandelbar.
> 2) §14 = dein Baubetrieb (Loop, Skills, Git, Resume, Anti-Slop). CLAUDE.md fasst es zusammen.
> 3) §15 = Bauplan. `tasks/` + `progress/BUILD-STATE.md` sind die **einzige Wahrheit** für den Stand.
> 4) Nach Absturz/Unterbrechung: `/clawscreen-resume` (oder „resume" / „weiter").
> 5) Widersprüche in dieser Spec: zugunsten von §2/§14 auflösen und die Entscheidung im BUILD-STATE vermerken.

**ClawScreen** = „Claude" + „Screen" (englisch für Bildschirm). Ein Werkzeug, mit dem Claude Code den kompletten Android-Bildschirm des Nutzers **selbstständig sieht und bedient** — wie ein Assistent, der dem Nutzer über die Schulter schaut und ihm die Finger ersetzt.

**Zielgerät & Umgebung (fest verdrahtet, kein „irgendein Android"):**

| Bestandteil | Wert |
|---|---|
| Handy | Samsung Galaxy A56 5G (6,7 Zoll, 1080 × 2340 Pixel, 120 Hz, 8 GB RAM) |
| Android-Version | Android 15 mit Samsung-„One UI" 7 |
| Terminal-App | **Termux** (App, die eine Linux-Befehlszeile aufs Handy bringt) |
| Linux-Umgebung | **Debian** innerhalb von Termux (eingerichtet über `proot-distro` — ein „Linux im Linux", ohne das System anzufassen) |
| Assistent | **Claude Code** läuft **in Debian** (Pfad-Konvention wie ClauDroide: `/home/mert/<projekt>`) |
| Ort des neuen Projekts | `/home/mert/clawscreen` |
| GitHub-Konto | `mertgoevse-wq` |
| Root („Superuser"-Zugriff aufs System) | **Nicht vorhanden und nicht nötig** — alles läuft mit normalen Android-Mitteln |

---

## 0. Kleines Wörterbuch (alle Fachbegriffe dieser Spec, einfach erklärt)

Diese Spec ist so geschrieben, dass sie **Nutzer ohne Informatikkenntnisse** versteht **und** Claude Code alle technischen Details liefert, die es zum autonomen Bauen braucht.

| Begriff | Einfache Erklärung |
|---|---|
| **ADB (Android Debug Bridge)** | Androids eingebauter „Wartungszugang". Damit kann man von außen Screenshots machen, tippen, wischen, Texte eintippen und Apps starten. Auf demselben Handy nutzbar über „kabelloses Debugging" (Wireless Debugging) mit `127.0.0.1` (= „dieses Gerät selbst"). Kein Root nötig. |
| **Wireless Debugging** | Der Schalter in den Android-Entwickleroptionen, der den ADB-Zugang freigibt. Muss einmalig mit einem 6-stelligen Kopplungscode aktiviert werden. Der Anschluss („Port", eine 4–5-stellige Zahl) ändert sich nach Neustarts — ClawScreen braucht dafür eine Automatik (siehe §11). |
| **MCP (Model Context Protocol)** | Eine Standardschnittstelle, über die Claude Code zusätzliche „Werkzeuge" benutzen kann, als wären sie eingebaut. ClawScreen stellt sein Werkzeug (screenshot, tippen, wischen …) als MCP-Server bereit. |
| **Zugangshilfe / Accessibility Service** | Eine Sondererlaubnis, die Android an Apps vergibt (z. B. auch an Vorlese-Apps für Blinde). Eine App mit dieser Erlaubnis darf den Bildschirminhalt sehr genau lesen und Systemgesten (Zurück, Startseite) ausführen. |
| **uiautomator dump** | Ein Android-Mitbringsel: macht ein „Inventar" des Bildschirms — Liste aller Knöpfe/Felder mit Text, Kennung und Position (als XML-Datei). Funktioniert nicht bei Apps, die ihre Oberfläche selbst zeichnen (z. B. Musik-Apps). |
| **Vision** | Claude kann Bilder „ansehen" und verstehen. Screenshots sind so Claudes „Augen", wenn das Inventar des Bildschirms nichts hergibt. |
| **Skill** | Eine wiederverwendbare Bau- und Verhaltensanweisung, die Claude Code laden kann — eigene (im Repo) oder aus der Community installierte (global). Claude Code kann Skills selbst suchen (`npx skills find <begriff>`) und installieren (`npx skills add <owner/repo> --skill <name> --yes`). |
| **KI-Müll („AI-Slop")** | Aufgedonnerte, austauschbare KI-Ware: Superlative ohne Beleg, Emoticon-Salat, Buzzword-Absätze, Platzhalter-Funktionen, Fake-Tests. Wird hier gezielt verboten und per Lint-Skript in CI geprüft (§14.5). |
| **Resume (Crash-Recovery)** | Der Befehl („resume"/„weiter"), der nach einem Termux-Absturz den letzten **geprüften** Baustand einsammelt (Dateisystem + Git + Baustand-Protokoll abgleichen) und autonom weiterbaut. |
| **MCP-Tool** | Eine einzelne Fähigkeit, die Claude über MCP aufrufen kann, z. B. `screen_tap`. |
| **Sitzung (Session)** | Ein Zeitraum, in dem ClawScreen aktiv den Bildschirm begleitet (gestartet mit `/screen`, beendet mit `/stop`). |
| **Denylist (Sperrliste)** | Eine Liste von Apps, die Claude **nie** bedienen darf (in der Bauphase: alle Geld-/Kauf-Apps). |
| **APK** | Die Installationsdatei einer Android-App (wie eine .exe unter Windows). |
| **Wellen (Waves)** | Bauphasen-Ordnung wie bei ClauDroide: Aufgaben mit Abhängigkeiten; keine Aufgabe startet, bevor ihre Vorgänger fertig sind. |
| **Checkpoint (Baustand)** | Die Datei `progress/BUILD-STATE.md` hält nach jeder erledigten Aufgabe fest, was fertig ist, wie es getestet wurde und welcher Git-Stand zuletzt gepusht war. Ermöglicht Weiterarbeit nach Unterbrechung. |

---

## 1. Produktvision & Nutzung in einem Satz

> Der Nutzer tippt in Claude Code (in Debian in Termux): **`/screen`** — und sagt danach auf Deutsch oder Englisch, was passieren soll, z. B. *„Bau mir in Cubasis ein neues Projekt mit einer Schlagzeugspur und einem Bass, Tempo 100"* — und Claude sieht den Bildschirm, plant, tippt/wischt/eingibt selbstständig, prüft jeden Schritt und berichtet fortlaufend. Nicht nur Musik: **alles**, was sich am Bildschirm bedienen lässt (Einstellungen, Apps, Bedienungen aller Art).

---

## 2. Was der Nutzer im Interview entschieden hat (verbindliche Entscheidungen)

| # | Thema | Entscheidung |
|---|---|---|
| E1 | Steuerweg | **ADB als Basis PLUS eigene Zusatz-App** („ClawScreen Companion") mit Zugangshilfe — volle Abdeckung, kein Root. |
| E2 | Verhältnis zu ClauDroide | **Eigenständiges Projekt mit Brücke**: eigenes Repo, aber von Anfang an Schnittstellen vorgesehen, damit es später als ClauDroide-Add-on eingebunden werden kann. |
| E3 | Autonomiegrad | **Alles autonom** — kein Schritt-für-Schritt-Nachfragen im Normalbetrieb. Grenze siehe E10. |
| E4 | Erste Bewährungsprobe | **Musik zuerst**: Cubasis 3 und FL Studio Mobile sind die ersten richtungsweisenden Tests. |
| E5 | Sitzungsarten | **Beide Modi**: kurze Einzelbefehle **und** laufende `/screen`-Sitzung mit laufender Beobachtung. |
| E6 | Notbremsen | **Alle drei**: Terminal (`/stop` bzw. Strg+C), schwebender Stopp-Knopf am Bildschirm, Lautstärketasten (Doppel-Druck „Leiser"). |
| E7 | Musik-Apps | **Cubasis 3, FL Studio Mobile und allgemeine Abdeckung** aller anderen Apps. |
| E8 | Bedienungs-Gedächtnis | **Ja, mit Notizen**: pro App gespeicherte Hinweise (Positionen, Abläufe), die bei jedem Einsatz besser werden. |
| E9 | Bildschirm wachhalten | **Erlaubt**: Während einer Sitzung bleibt das Display an (wird automatisch an- und am Ende zurückgeschaltet). |
| E10 | Geld-Apps | **Während der Bauphase komplett gesperrt** (Bank-, Bezahl-, Kauf-Apps). Später evtl. erlaubt — mit vorheriger lauter Ansage (Schalter ab Tag 1 im Code, siehe §9.2). |
| E11 | Sprache | **Deutsch und Englisch frei wählbar** (Konfiguration), später frei wählbar aus allen Sprachen (Ausblick §16). |
| E12 | Aufgabenlisten | **Ja**: Mehrfachaufträge („1. …, 2. …, 3. …") werden als sichtbare Liste abgearbeitet, zwischendurch ergänzbar. |
| E13 | Repo-Erstellung | **Vollautomatisch durch Claude Code**: Ordner, git, privates GitHub-Repo `mertgoevse-wq/clawscreen`, erste Übertragung (§12). |
| E14 | Zukunftskapitel | **Ja**, eigene Ausblick-Sektion (Sprachsteuerung u. a.), damit das Fundament passt (§16). |
| E15 | Globale Skills | **Claude Code sucht, installiert und orchestriert Skills automatisch**: global installierte Community-Skills + eigene Skills, jede Bauaufgabe bekommt ≥ 2 zugewiesene Skills (Skill-Matrix), die im Bau-Loop geladen werden. |
| E16 | Git-Disziplin | **Nach JEDER Aufgabe Commit + Push.** Unaufgeräumte lokale Commits werden vor dem Task-Commit gesquasht oder verworfen — der Nutzer erlaubt das Löschen lokaler Commits ausdrücklich, um Ansammlungen zu vermeiden. GitHub-Remote ist die alleinige Wahrheit. |
| E17 | Crash-Recovery | **Befehl „resume"** (`/clawscreen-resume` oder „weiter"): nach Termux-Absturz automatisch Baustand einsammeln, nachprüfen und autonom weiterbauen. |
| E18 | Referenz-Repos | **50+ GitHub-Repos recherchieren, kuratieren, die besten installieren und aktiv beim Bau nutzen** (Steuerung, Tests, Qualität, README-Vorbilder) — dokumentiert in `docs/reference-repos.md`. |
| E19 | Ein-Durchlauf-Bau | **Meisterbefehl „Baue alles bis zum finalen Produkt"**: ein autonomer Lauf mit Todo-Führung, der erst endet, wenn alle Aufgaben fertig sind (oder ein Sicherheits-Riegel/Blocker es verbietet). Absturzsicher durch E16+E17: logisch bleibt es „ein Lauf" über Abstürze hinweg. |
| E20 | Anti-AI-Slop | **README & Code auf Top-Niveau**: ohne KI-Floskeln, mit funktionierendem Quickstart, ehrlichen Einschränkungen — Lint-geprüft in CI (§14.5). |
| E21 | UI-Design-Skills | **Werden verpflichtend** für alle Companion-App-Oberflächen geladen und angewendet (adaptive Gestaltung, Material 3, Touch-Zielgrößen, Dark Mode) (§14.6). |

---

## 3. Ziele und Nicht-Ziele

### 3.1 Ziele
1. **Zwei Kommandowege** aus Claude Code (Debian):
   - Einzelbefehl: `clawscreen <aufgabe>` (CLI-Werkzeug) bzw. direkter MCP-Tool-Aufruf — führt aus und endet.
   - `/screen` — startet eine Sitzung: Claude beobachtet den Bildschirm laufend, nimmt fortlaufend Wünsche entgegen, bis `/stop`.
2. **Vollständige Bedienfähigkeit**: Apps öffnen/schließen, Tippen, Wischen, langes Drücken, Ziehen (Drag), Texteingaben, Systemtasten (Zurück, Startseite, Übersicht), Lautstärke, Helligkeit, Benachrichtigungen, Einstellungen-App, Tastatureingaben inkl. Sonderzeichen (Deutsch-Fallback: `adb shell input text` beherrscht keine Umlaute — Lösung über Zwischenablage der Zusatz-App oder Taste-für-Taste-Eingabe, siehe §6.4).
3. **Zuverlässiger Arbeitszyklus („Sehen–Denken–Handeln–Prüfen")**: Jede Aktion wird danach mit einem Frisch-Screenshot verifiziert; stimmt das Ergebnis nicht mit der Erwartung überein, **stoppt Claude und berichtet**, statt blind weiterzutippen („Verwunderungs-Regel", §7).
4. **Bedienungs-Gedächtnis** (`~/.clawscreen/memory/`): pro App gespeicherte Hinweise (sichere Koordinaten, Ablaufrezepte), automatisch angereichert; Wiederholungsfälle laufen schneller und genauer (§8).
5. **Musik-Fähigkeit als Aushängeschild**: Cubasis 3 und FL Studio Mobile bekommen eigene „Kochbücher" (bewährte Abläufe: Projekt anlegen, Spur hinzufügen, Instrument wählen, Noten, Tempo, Export) auf dem Gedächtnis aufbauend (§15, W7).
6. **Drei Notbremsen**, jederzeit wirksam (§9.3).
7. **Sperrliste für Geld-Apps** in der Bauphase (§9.2).
8. **Vollautomatische Repo-Erstellung** auf GitHub als **privates** Repository (§12).
9. **ClauDroide-Brücke** (§13).
10. **Ausblick-Kapitel** (§16).
11. **Globaler Skill-Betrieb** (E15): Auto-Discovery, Installation, Skill-Matrix, Orchestrierung im Bau-Loop (§14.2).
12. **Git-Disziplin**: Commit + Push nach jeder Aufgabe, saubere lokale Historie (E16, §14.3).
13. **Crash-Recovery per „resume"** (E17, §14.4).
14. **Referenz-Repo-Beutezug**: 50+ GitHub-Repos kuratiert und genutzt (E18, CS-006).
15. **Ein-Durchlauf-Autonomie** mit Todo-Führung (E19, §14.1).
16. **Anti-AI-Slop-Standard** für README und Code (E20, §14.5).
17. **UI-Design-Skills** für die Companion-Oberflächen (E21, §14.6).

### 3.2 Nicht-Ziele (bewusst raus)
- Kein Root, kein Umflashen, keine Systemveränderung am Handy.
- Keine Cloud-Zwischenschicht: Alles läuft auf dem Gerät zwischen Claude Code, ADB und der Zusatz-App.
- Kein Aufnehmen/Weiterleiten von Bildschirminhalten nach außen (Screenshots bleiben lokal in `~/.clawscreen/`).
- Keine Emulator-/PC-Steuerung — nur dieses eine Gerät, von sich selbst.
- Keine Konkurrenz zu ClauDroide (das ist ein Code-Assistent mit eigener App) — ClawScreen ist ein Bildschirm-Assistent auf CLI-/MCP-Basis und wird später optional von ClauDroide aus bedienbar.
- Keine Blind-Installation beliebigiger Community-Skills ohne Sichtprüfung (Inhalt kurz lesen, dann installieren — §14.2).

---

## 4. Systemarchitektur (Bausteine und wie sie zusammenwirken)

```
┌────────────────────────── Samsung Galaxy A56 ──────────────────────────┐
│                                                                        │
│  ┌────────────────────── Termux ────────────────────┐                  │
│  │  adb-Server (Paket android-tools, Port 5037)     │                  │
│  │  Verbindung zu „sich selbst": 127.0.0.1:<Port>   │                  │
│  └────────────▲─────────────────────────────────────┘                  │
│               │ ADB (Screenshots, Eingaben, App-Start, Inventar)       │
│  ┌────────────┴────────────── Debian (proot) ────────┐                  │
│  │  Claude Code                                      │                  │
│  │   ├─ /screen-Skill  (.claude/skills/screen/…)     │                  │
│  │   ├─ /clawscreen-resume-Skill (Crash-Recovery)    │                  │
│  │   ├─ MCP-Server „clawscreen" (TypeScript/Node)    │                  │
│  │   │    ├─ Werkzeuge: screen_* (siehe §6)          │                  │
│  │   │    └─ Sperrliste, Sitzungs-Protokoll, Gedächtnis                 │
│  │   ├─ CLI „clawscreen" (pair/connect/status/stop/…)│                  │
│  │   └─ Global installierte Skills (~/.agents/skills)│                  │
│  └───────────────────────────────────────────────────┘                  │
│                                                                        │
│  ┌────────────────── ClawScreen Companion (APK) ────┐                  │
│  │  Zugangshilfe: geschützte Bildschirme lesen,     │                  │
│  │    Systemgesten, Lautstärketasten abfangen       │                  │
│  │  Schwebender Stopp-Knopf (immer im Vordergrund)  │                  │
│  │  Display wachhalten während Sitzungen            │                  │
│  │  Mini-Server nur für sich selbst (127.0.0.1:8765)│                  │
│  │    → Zustand/Notbremsen an MCP melden            │                  │
│  │  Umlaut-Eingabe via Zwischenablage               │                  │
│  └───────────────────────────────────────────────────┘                  │
│                                                                        │
│  Beliebige Ziel-App im Vordergrund (Cubasis 3, FL Studio Mobile,        │
│  Einstellungen, …)                                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

**Wichtige Randbedingungen, die Claude Code beim Bauen berücksichtigen muss:**

1. **Wo läuft adb?** In **Termux** (Paket `android-tools`). Der Debian-Teil greift darauf zu, indem der MCP-Server die Umgebungsvariable `ADB_SERVER_SOCKET=tcp:127.0.0.1:5037` setzt — dann redet der adb-Client in Debian mit demselben adb-Server in Termux. (Nur EIN adb-Server im Gerät — zweiten verhindern.)
2. **Verbindung zu sich selbst:** Android 11+ bietet „Kabelloses Debugging" auch für `127.0.0.1`. Ablauf einmalig: Entwickleroptionen → Kabelloses Debugging → „Mit Kopplungscode koppeln" → `adb pair 127.0.0.1:<Kopplungsport>` + 6-stelliger Code → danach `adb connect 127.0.0.1:<Verbindungsport>`. Der Kopplungsdialog muss sichtbar sein, während gekoppelt wird → der Nutzer teilt den Code im Terminal ein (dafür gibt es den geführten Befehl `clawscreen pair`, §11.1).
3. **Ports sind vergänglich:** Der Verbindungsport ändert sich nach Neustart/Zeit. Deshalb: `clawscreen connect`-Routine mit Prüf- und Wiederhol-Logik + Vollautomatik über die Zusatz-App (§11.3).
4. **Screenshots über ADB funktionieren überall**; das UI-Inventar (`uiautomator dump`) dagegen nicht bei selbstgezeichneten Oberflächen (Cubasis/FL Studio Mobile zeichnen selbst → dort ist Claude-Vision der Hauptweg, das Inventar nur Hilfsmittel).
5. **Auflösung & Koordinaten:** Geräteauflösung ist 1080 × 2340. Screenshot-Analyse geschieht auf verkleinertem Bild (Standard: Breite 840 px, JPEG-Qualität 85 — spart Rechenkosten), aber **alle Tipp-Koordinaten werden in echten Gerätepixeln** übergeben (Faktor mitrechnen und im Werkzeug dokumentieren). `wm size` liefert die Wahrheit zur Laufzeit.
6. **Alles lokal:** Keine Daten verlassen das Gerät (außer Claudes eigene Anfragen an Anthropic, die der Nutzer ohnehin über Claude Code zulässt).

---

## 5. Bestandteile des Repos (Lieferliste)

Repo `mertgoevse-wq/clawscreen` (privat), lokal `/home/mert/clawscreen`:

```
clawscreen/
├── clawscreen-spec.md          # Diese Spec (Baueinzquelle)
├── CLAUDE.md                   # Bauregeln: Bau-Loop, Skill-Betrieb, Git-Disziplin,
│                               #   Resume-Verweis, Anti-Slop-Regeln (§14, kompakt)
├── README.md                   # Nutzer-Anleitung Deutsch — Top-Standard, Lint-geprüft (§14.5)
├── mcp/                        # MCP-Server (TypeScript/Node, stdio)
│   ├── src/index.ts            #   Server-Einstieg
│   ├── src/tools/*.ts          #   screen_*-Werkzeuge (§6)
│   ├── src/adb.ts              #   ADB-Anbindung (ADB_SERVER_SOCKET)
│   ├── src/memory.ts           #   Bedienungs-Gedächtnis (§8)
│   ├── src/safety.ts           #   Sperrliste + Verwunderungs-Regel (§9)
│   ├── src/session.ts          #   Sitzungs-Modus, Aufgabenliste, Protokoll
│   └── package.json
├── cli/                        # clawscreen-CLI (Bash oder Node)
│   ├── clawscreen              #   pair | connect | status | stop | setup | memory …
│   └── lib/…
├── companion/                  # Zusatz-App „ClawScreen Companion" (Kotlin, minimal)
│   ├── app/src/main/…
│   │   ├── AccessibilityService (lesen + Systemgesten + Lautstärketasten)
│   │   ├── FloatingStopButton  (schwebender roter STOPP-Kreis)
│   │   ├── KeepAwakeService    (Vordergrund-Dienst mit Benachrichtigung)
│   │   ├── ClipboardBridge     (Umlaut-Eingabe)
│   │   └── LocalStateServer    (127.0.0.1:8765: Zustand/Notbremsen)
│   └── build.gradle.kts
├── skill/
│   └── screen/SKILL.md         # /screen-Sitzungsanweisung (Verhalten, Regeln, Sprache)
├── .claude/skills/
│   └── clawscreen-resume/SKILL.md   # Crash-Recovery (Trigger: /clawscreen-resume, „resume", „weiter")
├── .agents/skills/             # Doku der global installierten Community-Skills (was, wofür, Quelle)
├── memory/                     # Anfangs-Gedächtnis (im Repo versioniert!)
│   ├── cubasis3.json
│   └── flstudio-mobile.json
├── docs/
│   └── reference-repos.md      # 50+ untersuchte GitHub-Repos + Übernahme-Entscheidungen (CS-006)
├── tasks/                      # Aufgaben mit YAML-Kopf (ClauDroide-Konvention)
│   ├── DEPENDENCIES.md
│   ├── skill-matrix.md         #   ≥ 2 Skills pro Aufgabe (E15)
│   └── CS-001 … CS-0xx.md
├── progress/BUILD-STATE.md     # Baustand-Protokoll (Resume-Grundlage)
├── tools/
│   ├── sync_frontmatter.py     # Aufgabenzustand prüfen/heilen
│   ├── anti-slop.py            # README/Docs-Lint gegen KI-Müll-Muster (§14.5)
│   └── e2e-check.sh            # Ende-zu-Ende-Prüfungen (§15, W7)
└── .github/workflows/
    ├── repo-health.yml         # Aufgaben-Konsistenz, Spec-Prüfung, Anti-Slop-Lint
    └── build-apk.yml           # Companion-APK bauen (Muster: ClauDroide)
```

---

## 6. Die MCP-Werkzeuge (Claudes „Hände und Augen")

Alle Werkzeuge heißen `screen_*`, damit es im Werkzeug-Menü von Claude Code ein eigener klarer Block ist. Jede Antwort enthält: `ok`, `screenshot_ref` (Pfad zum Frisch-Bild), `ui_inventar` (falls verfügbar), `notiz` (kurze Klartext-Rückmeldung in der Sitzungssprache).

### 6.1 Sehen
| Tool | Aufgabe | technische Umsetzung |
|---|---|---|
| `screen_look` | Aktuelles Bild + (optional) Inventar liefern | `adb exec-out screencap -p` → PNG; Skalierung auf Analysegröße; parallel `uiautomator dump` mit 3 s Zeitgrenze (fehlertolerant) |
| `screen_look_region` | Ausschnitt scharf ansehen (z. B. kleine Knopfleiste) | Bild zuschneiden um Koordinate/Rechteck, volle Auflösung |
| `screen_apps` | Liste installierter Apps mit Paketnamen | `adb shell pm list packages -3` (+ Systempakete-Option) |
| `screen_foreground` | Welche App ist gerade vorn? | `adb shell dumpsys activity activities` (One-UI-sicher parsen, `topResumedActivity`) |

### 6.2 Handeln
| Tool | Aufgabe | technische Umsetzung |
|---|---|---|
| `screen_tap` | Tippen (x, y in Gerätepixeln) | `adb shell input tap` |
| `screen_long_press` | Langes Drücken | `adb shell input swipe x y x y 800` |
| `screen_swipe` | Wischen (Start, Ziel, Dauer) | `adb shell input swipe` |
| `screen_drag` | Ziehen mit Zwischenpunkten (für Regler/Keyboards) | mehrstufige `input swipe` |
| `screen_text` | Text in fokussiertes Feld eingeben | ASCII: `adb shell input text`; Umlaute/Sonderzeichen: Zwischenablage-Weg der Zusatz-App (§6.4) |
| `screen_key` | Systemtasten: BACK, HOME, RECENTS, ENTER, DEL, VOL_UP/DOWN … | `adb shell input keyevent KEYCODE_*` |
| `screen_open_app` | App starten | `adb shell monkey -p <paket> 1` (robuster als `am start` über Launcher-Auflösung) |
| `screen_wait_change` | Warten bis sich der Bildschirm ändert (max. Timeout) | Screenshot-Vergleich (Differenzmaß) in Schleife |
| `screen_scroll_to` | Solange wischen, bis Suchbegriff im Inventar/Bild auftaucht | Kombination swipe + look |

### 6.3 Denken/Verwalten
| Tool | Aufgabe |
|---|---|
| `session_start` / `session_status` / `session_stop` | Sitzung beginnen (wachhalten an, Stopp-Knopf ein, Protokoll öffnen), Zustand abfragen, sauber beenden (wachhalten zurücksetzen) |
| `tasklist_set` / `tasklist_update` | Aufgabenliste (E12) anlegen/aktualisieren; wird im Protokoll und in jeder Rückmeldung mitgeführt |
| `memory_read` / `memory_write` | Bedienungs-Gedächtnis lesen/schreiben (§8) |
| `safety_check` | Prüft geplante Ziel-App/Aktion gegen Sperrliste (§9.2) — wird von JEDEM Handlungs-Tool automatisch vorab ausgeführt |

### 6.4 Umlaut-Problem und Lösung (wichtig!)
`adb shell input text` kann keine Umlaute (ä ö ü ß) und nur eingeschränkt Sonderzeichen. Lösung über die Zusatz-App:
1. MCP setzt Text in die Android-Zwischenablage über die Zusatz-App (`POST /clipboard` auf `127.0.0.1:8765`).
2. MCP löst „Einfügen" aus: die Zusatz-App führt per Zugangshilfe die Einfüge-Aktion auf dem fokussierten Feld aus.
3. Fallback ohne Zusatz-App: Text Taste-für-Taste über Keycode-Tabelle (langsam) oder der Nutzer wird um englische Schreibweise gebeten.
Die Werkzeuge entscheiden automatisch nach Zeichenbestand.

---

## 7. Ablauf einer `/screen`-Sitzung (Verhaltens-Spec)

Der Befehl `/screen` ist ein Claude-Code-Skill (`skill/screen/SKILL.md`), der Claude verbindlich vorschreibt:

1. **Vorbereitung (automatisch):** `clawscreen status` → Verbindung ok? Zusatz-App erreichbar? Falls nicht: geführte Reparatur (Kopplungsdialog ansagen, `clawscreen pair`/`connect`).
2. **Sitzungsstart:** `session_start` → Display wachhalten an, Stopp-Knopf einblenden (Zusatz-App), Protokolldatei anlegen: `~/.clawscreen/logs/YYYY-MM-DD-HHMM.md`.
3. **Basis-Sicht:** `screen_look` — Claude verschafft sich den Überblick, meldet kurz, was es sieht.
4. **Wunschaufnahme:** Der Nutzer formuliert frei (Deutsch/Englisch). Claude zerlegt den Wunsch in die Aufgabenliste (E12) und zeigt sie nummeriert an.
5. **Arbeitszyklus je Aufgabe:**
   a. Gedächtnis prüfen (`memory_read`) → b. Handeln (Tools) → c. **Prüfen** (`screen_look`, Vergleich mit Erwartung) → d. Ergebnis kurz melden (1–2 Sätze) → e. Gedächtnis fortschreiben, wenn neue verlässliche Erkenntnis.
   **Verwunderungs-Regel:** Weicht der Bildschirm stark ab (unerwarteter Dialog, andere App, Fehlermeldung, Netzwerk-Hinweis) → sofort pausieren, Bild + Beobachtung melden, auf neuen Wunsch oder „mach weiter" warten.
6. **Zwischendurch:** Neue Wünsche ergänzen die Liste; „stop" innerhalb einer Aufgabe bricht sie ab; jede Handlung landet im Protokoll mit Zeitstempel und Screenshot-Pfad.
7. **Sitzungsende:** `/stop` (oder Stopp-Knopf oder Lautstärke-Doppel-Druck) → Aufgabe abbrechen, wachhalten zurücksetzen, Stopp-Knopf aus, Abschlussbericht (was erledigt, was offen, auffällige Beobachtungen).

**Einzelbefehl-Modus** nutzt dieselben Tools ohne Sitzung: z. B. `clawscreen run „Öffne Einstellungen und schalte Bluetooth aus"` → Claude plant, führt aus, berichtet, endet. Auch hier Sperrliste + Verwunderungs-Regel.

---

## 8. Bedienungs-Gedächtnis (E8)

**Ort:** `~/.clawscreen/memory/<paket-name>.json` — zusätzlich versioniert im Repo unter `memory/` für die beiden Musik-Apps (Startwissen).

**Struktur (Beispiel cubasis3.json):**
```json
{
  "app": "com.steinberg.cubasis",
  "zuletzt_geprüft": "2026-10-04",
  "auflösung": [1080, 2340],
  "anker": {
    "projekt_neu": { "koordinaten": [980, 2200], "sicherheitsprüfung": "Dialog 'Neues Projekt' sichtbar", "vertrauen": 0.9 },
    "spur_hinzufügen": { "koordinaten": [540, 2290], "vertrauen": 0.8 }
  },
  "rezepte": {
    "projekt_anlegen": [
      "screen_open_app com.steinberg.cubasis",
      "warten auf Hauptansicht (Titel 'Cubasis' oder Projektliste)",
      "screen_tap anker.projekt_neu",
      "screen_tap 'OK'/Bestätigung",
      "prüfen: leere Timeline sichtbar"
    ]
  },
  "hinweise": [
    "Oberfläche ist selbstgezeichnet: uiautomator liefert fast nichts — Vision nutzen",
    "Nach App-Start 2,5 s Ladezeit einplanen"
  ]
}
```

**Regeln:**
- Koordinaten-Einträge bekommen immer eine **Sicherheitsprüfung** („wie erkenne ich, dass ich richtig bin") und ein **Vertrauens-Niveau**. Unter Schwelle 0,5 wird vor dem Tipp ein Zoom-Blick (`screen_look_region`) verlangt.
- Jede erfolgreiche Bestätigung erhöht Vertrauen, jeder Fehlgriff senkt es und stößt Neubestimmung an.
- Bei Auflösungs-/Layout-Änderung (erkennbar an systematischen Fehlgriffen) verwirft ClawScreen Anker der App und baut sie neu auf.

---

## 9. Sicherheitskonzept

### 9.1 Autonomie (E3)
Kein Schritt-für-Schritt-Nachfragen. Claude handelt im Rahmen dieser Spec selbstständig und **berichtet fortlaufend**, was es tut (Protokoll + kurze Fortschrittsmeldungen).

### 9.2 Sperrliste Geld-Apps (E10) — gilt während der gesamten Bauphase
- Standardliste (vorkonfiguriert, vom Nutzer erweiterbar in `~/.clawscreen/config.json` → `deny_packages`):
  - `com.android.vending` (Google Play — schließt Käufe aus),
  - Pakete, die auf gängige Banking-/Bezahlmuster passen (Name enthält `bank`, `banking`, `paypal`, `klarna`, `payment`, `wallet`) — final entscheidend ist die konfigurierbare Liste;
  - Zusätzliche Block-Regel: **Keine Bestätigung von Kauf-Dialogen**, selbst wenn sie in erlaubten Apps auftauchen (Erkennung: Dialogtext enthält „kaufen", „Kauf", „€", „$", „Preis bestätigen" → Abbruch mit Meldung).
- Verstoß-Versuche werden im Protokoll markiert und dem Nutzer gemeldet. Nach der Bauphase umschaltbar auf `mode: "announce"` (erst laut ansagen, dann handeln) oder `mode: "open"` (Nutzerentscheidung später) — **Schalter existiert im Code ab Tag 1, steht ab Werk auf `blocked`.**

### 9.3 Drei Notbremsen (E6) — jederzeit, in jeder Lage
1. **Terminal:** `/stop` im Chat bzw. Strg+C beendet Sitzung/Aufgabe sofort; `clawscreen stop` als harter Weg (bricht laufende Eingabe-Übertragungen ab + setzt wachhalten zurück).
2. **Stopp-Knopf:** Roter schwebender Kreis der Zusatz-App (immer im Vordergrund, verschiebbar, 64 dp). Antippen → Zusatz-App meldet STOPP an `127.0.0.1:8765`, MCP bricht laufende Aktion ab (Gesten sind über Timeout begrenzt, max. 1,5 s pro Geste, damit nichts „durchläuft"), Sitzung pausiert, Vibration bestätigt.
3. **Lautstärketasten:** Die Zusatz-App fängt über die Zugangshilfe **Doppel-Druck auf „Leiser"** ab (innerhalb 600 ms) → gleiches STOPP-Verhalten. Einzeldruck wird normal durchgereicht.

### 9.4 Weitere harte Regeln (in `safety.ts` erzwungen, nicht nur Absicht)
- Max. 1 Aktion pro 300 ms (Schutz vor Amok-Schleifen).
- Jede Handlungs-Tool-Antwort MUSS ein Frisch-Bild enthalten (keine Aktion „blind auf Speicher").
- Sitzung ohne Antwort des Nutzers länger als 15 min → automatisch pausieren (Display bleibt wach bis Nutzer reagiert; Ende nach weiteren 5 min).
- Protokollgröße begrenzen: Screenshot-Ordner rotiert bei 200 MB (älteste zuerst).

---

## 10. Zusatz-App „ClawScreen Companion" (Detail-Spec)

**Zweck:** Alles, was ADB allein nicht kann oder umständlich macht: geschützte Bildschirme lesen, Systemgesten, Zwischenablage, Lautstärketasten abfangen, Stopp-Knopf, wachhalten, Auto-Wiederverbinden.

**Berechtigungen (jede mit klarer Begründung):**
| Erlaubnis | Wofür |
|---|---|
| Zugangshilfe (Accessibility) | Bildschirminhalt lesen (auch wo Inventar versagt), Systemgesten (Zurück/Start/Übersicht/Einfügen), Lautstärketasten abfangen |
| Über anderen Apps anzeigen | Stopp-Knopf |
| Vordergrund-Dienst + „Wachbleiben" | Sitzungswachhaltung (E9), stabile Verbindung des Mini-Servers |
| Vibrieren | Bestätigung von Notbremsen |
| Internet | **nur** für den `127.0.0.1`-Mini-Server (lokal, kein Netzverkehr) |

**Mini-Server (HTTP auf `127.0.0.1:8765`, nur lokal erreichbar):**
- `GET /health` → Erreichbarkeit/Zustand
- `GET /state` → Stopp gedrückt? Schlafdauer? Letzte Geste?
- `POST /clipboard` {text} → setzt Zwischenablage
- `POST /paste` → löst Einfügen auf fokussiertem Feld aus
- `POST /keepawake` {on|off}
- `POST /stopbutton` {show|hide}
- Kein Passwort nötig (nur localhost); die App prüft zusätzlich, dass der Aufrufer zur Termux/Debian-Umgebung gehört, sofern das zuverlässig möglich ist.

**Kein Play Store:** APK wird von GitHub Actions gebaut (Workflow `build-apk.yml`) und per `adb install` aus Termux aufgespielt. App-Name „ClawScreen Companion", eigenständige Marke, keine Claude-/Android-Marken im Logo (Brand-Trennung wie bei ClauDroide).

**Oberflächen (mit UI-Design-Skills bauen, E21):** Setup-Assistent als Schritt-für-Schritt-Fragefolge mit Statusanzeige (Erlaubnis erteilt? Verbindung? bereit), Stopp-Knopf dauerhaft verschiebbar, im Ruhezustand leicht durchsichtig, bei Gefahr voll deckend; Touch-Ziele ≥ 48 dp; Material 3, Dark Mode, kontraststark.

---

## 11. Verbindungs-Automatik (der heikelste Alltagsteil)

1. **Einmalige Kopplung (Nutzer-Mitwirkung nötig):** `clawscreen pair` führt interaktiv: sagt, wo der Schalter ist (Einstellungen → Entwickleroptionen → Kabelloses Debugging → „Mit Kopplungscode koppeln"), fragt Kopplungsport + 6-stelligen Code ab (Split-Screen-Hinweis geben), ruft `adb pair`, danach `adb connect` mit dem Verbindungsport, speichert letzten funktionierenden Port in `~/.clawscreen/state.json`.
2. **Alltagsverbindung:** `clawscreen connect` probiert: gespeicherten Port → Scan der letzten 5 bekannten Ports → `adb mdns services` (Auto-Entdeckung `_adb-tls-connect._tcp`) → Rückmeldung mit klarer Anleitung, falls alles scheitert.
3. **Vollautomatik (W5):** Zusatz-App erhält per ADB-Einmalkommando `WRITE_SECURE_SETTINGS` (`adb shell pm grant … android.permission.WRITE_SECURE_SETTINGS`) — damit kann sie „Kabelloses Debugging" selbst an-/abschalten und über Androids Netzwerk-Entdeckung (NsdManager) den aktuellen Kopplungs-/Verbindungsport finden und an den MCP melden. Ergebnis: Nach Handy-Neustart genügt `clawscreen connect` ohne Zutun.
4. **Verbindungswächter:** MCP prüft bei jedem Werkzeugaufruf die Erreichbarkeit (adb get-state) und startet bei Verlust die `connect`-Routine, bevor es fehlschlägt.

---

## 12. Automatische GitHub-Repo-Erstellung (E13) — Bauplan-Schritt W0

Claude Code führt beim Projektstart aus (verbindliche Befehle, Ausführung später):

1. Prüfen: `gh auth status` (GitHub-Anmeldung). Falls nicht angemeldet: **stoppen** und den Nutzer auffordern, `gh auth login` auszuführen (einmalig, interaktiv).
2. `mkdir -p /home/mert/clawscreen && cd /home/mert/clawscreen && git init -b main`
3. Diese Spec als `clawscreen-spec.md` einpflegen; `CLAUDE.md`, `README.md` (Deutsch), Aufgaben W0 schreiben; erster Commit.
4. `gh repo create mertgoevse-wq/clawscreen --private --source . --remote origin --push` — **privat**, Beschreibung: „ClawScreen — Claude steuert den Android-Bildschirm autonom (Termux/Debian, Samsung Galaxy A56)".
5. `.github/workflows/repo-health.yml` (Aufgaben-Konsistenz + Spec-Prüfung + **Anti-Slop-Lint**) und `build-apk.yml` (Companion-APK, Artifact-Upload) nach ClauDroides Mustern.
6. Nach jeder erledigten Aufgabe: **Commit + Push** (§14.3). Commit-Format: `CS-0xx: <ein Satz, was erledigt und wie geprüft>`. Kein Force-Push auf gepushte Historie.
7. Direkt danach: **Skill-Beutezug (CS-005)** und **Referenz-Repo-Beutezug (CS-006)** — bevor W1 beginnt, stehen die Skills und Vorbilder bereit.

---

## 13. ClauDroide-Brücke (E2)

- **Schnittstelle ab Tag 1:** Der MCP-Server ist ein eigenständiger Prozess mit klarer Versionierung (`mcp/manifest.json`, SemVer). ClauDroide (oder jeder andere MCP-fähige Assistent) kann ihn später einfach als Werkzeugquelle einbinden — keine ClawScreen-internen Abhängigkeiten nötig.
- **Namens- und Markentrennung:** Eigenständiger Name/Logo (kein „Claude"-Schriftzug im Logo; Wortmarke nur im Text mit Hinweis, dass keine Verbindung zu Anthropic besteht — wie ClauDroides Unabhängigkeitshinweis).
- **Konventionen übernommen:** Aufgaben-YAML, BUILD-STATE, Wellen, Skill-Matrix — damit eine spätere Integration (oder Zusammenführung als ClauDroide-Add-on-Paket „ClauDroide Screen") denkbar einfach ist.
- **Konfig-Brücke:** `~/.clawscreen/config.json` enthält `claude_integration: { enabled: false, expose_mcp: true }`.

---

## 14. Autonomer Baubetrieb für Claude Code (Skills, Todos, Git, Resume, Ein-Durchlauf)

Dieser Abschnitt ist die **Betriebsanleitung für Claude Code selbst**. Er ist verbindlich und wird kompakt in `CLAUDE.md` zusammengefasst.

### 14.1 Meisterbefehl & Ein-Durchlauf-Bau (E19)
- Der Meisterbefehl lautet: **„Baue alles bis zum finalen Produkt."** Claude Code startet dann den autonomen Bau-Loop und endet erst, wenn alle Aufgaben `done` sind oder ein Sicherheits-Riegel das Weiterbauen verbietet.
- **Loop pro Aufgabe:** früheste ausstehende Aufgabe mit erfüllten Abhängigkeiten wählen → zugewiesene Skills laden (Skill-Matrix) → implementieren → Tests ausführen → Aufgabe auf `done` + BUILD-STATE aktualisieren → **Commit + Push** → nächste.
- **Todo-Führung:** Claude Code pflegt durchgehend Todo-Listen (pro Welle und pro Arbeitssitzung) und aktualisiert sie nach jedem Schritt — der Nutzer sieht jederzeit, wo der Bau steht.
- **Blocker-Regel:** Nach 2 vergeblichen Versuchen pro Aufgabe → Blocker in BUILD-STATE notieren, zur nächsten unabhängigen Aufgabe springen, am Laufende gesammelt berichten. Ein Lauf endet nie „stumm".
- **Absturzsicherheit = Ein-Lauf-Garantie über Crashs hinweg:** Weil jede Aufgabe sofort gepusht wird (E16), ist nach einem Termux-Absturz logisch „derselbe Lauf" per `resume` fortsetzbar — kein Fortschritt geht verloren.

### 14.2 Globale Skills: finden, installieren, orchestrieren (E15)
- **Suche** (Aufgabe CS-005, vor W1): mit `npx skills find <begriff>` über mindestens diese Begriffe: `android`, `adb`, `android-testing`, `compose`, `ui design`, `adaptive`, `accessibility`, `mcp`, `git`, `testing`, `performance`, `kotlin`, `release`.
- **Prüfen, dann installieren:** Fundstücke kurz sichten (Beschreibung, Quellrepo, Aktivität, Inhalt), die Passenden **global** installieren: `npx skills add <owner/repo> --skill <name> --yes`. Nichts Unbekanntes blind ausführen. Installierte Skills inkl. Quelle und Zweck in `.agents/skills/` dokumentieren.
- **Skill-Matrix** `tasks/skill-matrix.md` (ClauDroide-Konvention): jede Aufgabe bekommt **≥ 2 Skills** (Haupt-Skill + Prüf-/Nebenskill). Der Bau-Loop lädt sie vor jeder Aufgabe.
- **Orchestrierung:** Mehrere unabhängige Aufgaben dürfen parallel laufen (z. B. `/parallel-task`), sofern Dateien/Wellen getrennt sind — Wellengrenzen sind die Sync-Punkte.
- Eigene Skills (`screen`, `clawscreen-resume`) sind Projekt-Skills; die globalen Community-Skills ergänzen sie. Konflikte: Projekt-Skill gewinnt.

### 14.3 Git-Disziplin: immer Commit + Push, keine lokale Ansammlung (E16)
- **Nach JEDER erledigten Aufgabe:** Commit + Push. Der entfernte Stand auf GitHub ist die alleinige Wahrheit.
- **Vor Beginn einer neuen Aufgabe** muss der Arbeitsordner sauber sein. Experimentier-Commits, die **nicht gepusht** wurden, werden vor dem Task-Commit in einen Squash überführt oder verworfen (`git reset --hard` auf den letzten gepushten Stand). Der Nutzer erlaubt das Löschen lokaler Commits ausdrücklich (E16).
- **Verboten:** lokale Ansammlung unaufgeräumter Commits; Force-Push auf bereits gepushte Historie. **Erlaubt:** Umschreiben/Verwerfen NICHT gepushter lokaler Commits.
- **Commit-Format:** `CS-0xx: <ein Satz, was erledigt und wie geprüft>` + Footer `🤖 Generated with Claude Code` / `Co-Authored-By: Claude <noreply@anthropic.com>`.
- **Auch bei Teil-Erfolg wird gepusht** (geprüfter Stand + Blocker-Notiz), damit ein Absturz nie Fortschritt frisst.

### 14.4 Crash-Recovery: `/clawscreen-resume` (E17)
- **Nutzer-Wörter:** `/clawscreen-resume`, `resume`, „weiter" — nach Termux-Absturz, Neustart oder Unterbrechung.
- **Ablauf des Skills** (`.claude/skills/clawscreen-resume/SKILL.md`):
  1. `progress/BUILD-STATE.md` lesen.
  2. Abgleich mit Dateisystem + `git log` + Aufgaben-Frontmatter — **ohne zu spekulieren**; nur Verifizierbares als Stand anerkennen.
  3. Zuletzt beanspruchte Aufgabe **nachprüfen** (deren Tests erneut ausführen).
  4. Abweichungen heilen (Status korrigieren, sync_frontmatter).
  5. Bau-Loop an frühester offener Aufgabe mit erfüllten Abhängigkeiten fortsetzen.
- **Katastrophenfall:** Da jede Aufgabe gepusht wird, enthält das Remote-Repo stets den vollständigen Stand inkl. BUILD-STATE. Ein frisch aufgesetztes Termux/Debian kann per `git clone` + `resume` vollständig fortfahren.

### 14.5 KI-Müll-Vermeidung (Anti-AI-Slop) & README auf Top-Niveau (E20)
- **Maßstab:** READMEs hochkarätiger Open-Source-Projekte (konkret, nüchtern, code-first) — als Vorbilder im Beutezug CS-006 explizit sammeln.
- **Verboten:** Emoticon-Salat in Überschriften, Superlative ohne Beleg („revolutionär", „blitzschnell"), leere Buzzword-Absätze, generische Floskeln („Beiträge willkommen!" ohne Prozess), Platzhalter-Funktionen, Fake-Tests, TODO-Implementierungen, unverbundene Dateien.
- **Geboten:** funktionierender Quickstart (kopierbar, auf dem Zielgerät getestet), ehrliche „Bekannte Einschränkungen", echte Befehle, Tabellen statt Prosatext, Inhaltsverzeichnis, CI-Badge, Screenshots erst wenn echt vorhanden, Fehlerbehebungs-Kapitel.
- **Werkzeug:** `tools/anti-slop.py` lintet README/Doku gegen eine Verbotsmuster-Liste und läuft in `repo-health.yml`. Befund = rote CI. (Nur Dokument-Lint — keine Inhaltszensur.)
- **Code-Slop-Regeln gelten gleich mit:** jede Funktion im echten Aufrufpfad, jede Behauptung im README mit Befehl/Test belegt.

### 14.6 UI-Design-Skills für die Companion-App (E21)
- Vor allen W4-Oberflächen-Aufgaben lädt Claude Code seine **UI-Design-Skills** (adaptive Gestaltung, Material-3-Richtlinien, Touch-Zielgrößen ≥ 48 dp, Dark Mode, Edge-to-Edge) — per Skill-Matrix zugewiesen.
- **Designvorgaben:** ClawScreen-Marke (Signalrot für STOPP, dunkle neutrale Flächen, Mono-Icons); Stopp-Knopf verschiebbar, im Ruhezustand leicht durchsichtig; Setup-Assistent als Fragefolge mit Statusanzeige; kontraststark, blendarm, einhändig bedienbar.
- Die Benachrichtigung des Wachhalte-Dienstes zeigt Sitzungszustand + direkte Stopp-Aktion.

---

## 15. Bauplan in Wellen (Aufgaben, Abhängigkeiten, Tests)

> Aufgaben-IDs `CS-0xx`, jeweils eine Datei `tasks/CS-0xx.md` mit YAML-Kopf (`status: pending|done`, `depends_on: []`, `wave`, `skills: [ … ]`, `test:`). Checkpoint-Pflicht nach jedem Task (§14.1/§14.3). Skill-Zuweisung je Task in `tasks/skill-matrix.md` (≥ 2 pro Task, E15).

### W0 — Gründung (CS-001 … CS-006)
- CS-001: Repo anlegen wie §12 (privat!), Spec einpflegen. **Test:** `gh repo view mertgoevse-wq/clawscreen --json isPrivate` → true.
- CS-002: CLAUDE.md (Bau-Loop, Skill-Betrieb, Git-Disziplin, Resume-Verweis, Anti-Slop-Regeln kompakt) + README-Gerüst + Aufgaben-Vorlagen. **Test:** Dateien vorhanden, Struktur wie §5.
- CS-003: Workflows `repo-health.yml` (inkl. **Anti-Slop-Lint** aus CS-003a) + `build-apk.yml` (Gerüst). **Test:** CI läuft grün auf leerem Stand.
- CS-004: `tools/sync_frontmatter.py` + `tools/anti-slop.py` + `progress/BUILD-STATE.md`. **Test:** beide Skripte melden Konsistenz.
- **CS-005: Skill-Beutezug (E15):** `npx skills find` über die Suchbegriffe aus §14.2, sichten, die ≥ 4 besten global installieren, `.agents/skills/`-Doku + `tasks/skill-matrix.md` (≥ 2 Skills je Task, alle Tasks eingetragen). **Test:** Matrix vollständig; installierte Skills laden und werden in CS-010+ tatsächlich benutzt.
- **CS-006: Referenz-Repo-Beutezug (E18):** GitHub-Recherche **50+ Repos** in Kategorien: (a) Android-Steuerung per ADB/MCP (z. B. mobile-mcp, scrcpy-mcp, adb-agent-bridge, android-debug-bridge-mcp), (b) Android-App-Tests/CI, (c) Compose/UI-Design-Systeme, (d) ADB-Wrapper-Bibliotheken, (e) README-Qualitätsvorbilder. Ergebnisse mit Sternen/Aktivität/Lizenz/„Was wir übernehmen" in `docs/reference-repos.md`; die nützlichsten als Abhängigkeit/Skill/MCP installieren; Übernahmen in den betroffenen Task-Briefs verlinken. **Test:** ≥ 50 Einträge, ≥ 5 Kategorien, ≥ 5 konkrete Übernahmen dokumentiert.

### W1 — Verbindung (CS-010 … CS-013)
- CS-010: `clawscreen pair` (geführt, §11.1). **Test:** Danach zeigt `adb devices` `127.0.0.1:* device`.
- CS-011: `clawscreen connect` (Wiederverbinden, §11.2). **Test:** Kabelloses Debugging aus/an → reconnect ok.
- CS-012: ADB-Basisschicht `mcp/src/adb.ts` (ADB_SERVER_SOCKET-Logik, Fehlerbehandlung, Zeitgrenzen). **Test:** screenshot/tap aus Debian, während der adb-Server in Termux läuft.
- CS-013: `clawscreen status` (Verbindung, Zusatz-App, Speicher, Konfig). **Test:** Klartext-Bericht.

### W2 — Kern-Werkzeuge (CS-020 … CS-025)
- CS-020: MCP-Server-Gerüst (stdio, Werkzeug-Registrierung, Fehlerformat). **Test:** `claude mcp add` in Debian, Werkzeuge erscheinen.
- CS-021: Sehen-Werkzeuge (§6.1) inkl. Skalierung + Koordinaten-Faktor. **Test:** `screen_look` liefert Bild + Inventar; Zoom-Weg funktioniert.
- CS-022: Handlungs-Werkzeuge (§6.2, ohne Umlaut-Extra). **Test:** E2E: Einstellungen öffnen, Bluetooth-Zeile antippen, Zustand umschalten, per Bild verifiziert.
- CS-023: `screen_wait_change` + Verwunderungs-Erkennung (Differenzmaß). **Test:** Unerwarteter Dialog → Pausierung greift.
- CS-024: Sitzungs-Modus + Protokoll + Aufgabenliste (§7, E12). **Test:** 3-Aufgaben-Liste wird abgearbeitet, Protokoll vollständig.
- CS-025: `/screen`-Skill (SKILL.md) mit Verhaltensregeln + Spracheinstellung (E11: de/en). **Test:** Handsitzung: „Öffne die Uhr-App und stoppe einen Wecker" läuft autonom.

### W3 — Sicherheit (CS-030 … CS-032)
- CS-030: `safety.ts` (§9.2, §9.4) mit Konfig-Datei. **Test:** Play-Store-Öffnungsversuch → Block + Meldung; Kauf-Dialog-Texte → Abbruch.
- CS-031: Notbremse Terminal (`/stop`, `clawscreen stop`). **Test:** laufende Aktion bricht ab, wachhalten zurückgesetzt.
- CS-032: Protokoll-Rotation + 15-min-Pause-Regel. **Test:** Grenzwerte simuliert.

### W4 — Zusatz-App Kern (CS-040 … CS-046) — UI-Design-Skills Pflicht (§14.6)
- CS-040: App-Gerüst (Kotlin, minimal, Brand „ClawScreen Companion"). **Test:** baut in CI.
- CS-041: Zugangshilfe: Bildschirm lesen (Baum als JSON), Systemgesten. **Test:** Auf geschütztem Bildschirm liefert Lese-Zugang mehr als Inventar.
- CS-042: Stopp-Knopf + Mini-Server `/state` (§10). **Test:** Knopf drücken → MCP bemerkt STOPP < 500 ms.
- CS-043: Lautstärke-Doppel-Druck abfangen. **Test:** Doppel-„Leiser" → STOPP, Einzeldruck normal.
- CS-044: Wachhalten-Dienst (E9) mit sauberem Zurücksetzen + Zustands-Benachrichtigung. **Test:** Sitzung an/aus → Zustand korrekt.
- CS-045: Zwischenablage + Einfügen (§6.4). **Test:** „Schreibe ‚Grüße aus Köln' in Nachrichten" — Umlaute korrekt.
- CS-046: `adb install`-Routine + Erst-Einrichtungs-Assistent (`clawscreen setup`: geleitete Erlaubniserteilung, UI nach §14.6). **Test:** Frischzustand → setup führt bis „bereit".

### W5 — Verbindungs-Vollautomatik (CS-050 … CS-051)
- CS-050: `WRITE_SECURE_SETTINGS`-Vergabe + programmatisches An/Aus von Kabellosem Debugging. **Test:** Schalter aus → `clawscreen connect` schaltet an und verbindet ohne Nutzer.
- CS-051: Port-Entdeckung per Netzwerk-Entdeckung (NsdManager) + Meldung an MCP. **Test:** Handy-Neustart → reconnect ohne Zutun.

### W6 — Bedienungs-Gedächtnis (CS-060 … CS-062)
- CS-060: Speicher-Lesen/Schreiben + Vertrauens-Logik (§8). **Test:** zweiter Lauf gleicher Aufgabe deutlich weniger Blick-Aufrufe.
- CS-061: Anker-Neubestimmung (Selbstheilung). **Test:** Koordinate absichtlich verschieben → Weg zurück + Aktualisierung.
- CS-062: Rezept-Format + Recorder (beim Arbeiten mitlernen). **Test:** Ablauf „Projekt anlegen" wird als Rezept gespeichert und wiederverwendet.

### W7 — Musik-Apps (CS-070 … CS-073) — die Aushängeschild-Aufgabe (E4)
- CS-070: Cubasis-3-Kochbuch + Start-Gedächtnis (`memory/cubasis3.json`): Projekt anlegen, Spur + Instrument, Abspielen, Tempo, Speichern, Export. **Abnahme-Szenario:** „Bau in Cubasis ein Projekt: Schlagzeugspur mit 4/4 bei 100 BPM und eine Bassspur, spiel es ab, benenne es ‚ClawTest'." — komplett autonom, Prüfbilder im Protokoll.
- CS-071: FL-Studio-Mobile-Kochbuch analog. **Test:** gleiche Art von Szenario in FL Studio Mobile.
- CS-072: Allgemeine Robustheit: Ladebildschirme, Popups, Werbe-Dialoge ignorieren/schließen, Berechtigungs-Dialoge der Ziel-Apps (Zusatz-App tippt „Zulassen" nur für Apps aus der Erlaubnis-Liste des Nutzers). **Test:** zehn zufällige Alltags-Apps öffnen und Grundnavigation.
- CS-073: E2E-Suite `tools/e2e-check.sh` (W2–W7-Szenarien als Skript, manuell auslösbar). **Test:** Suite berichtet Pass/Fail je Szenario.

### W8 — Alltag & Feinschliff (CS-080 … CS-083)
- CS-080: Einstellungen-Rezepte (WLAN, Bluetooth, Ton, Display, Apps). **Test:** „Schalte bitte Flugmodus ein und wieder aus" autonom.
- CS-081: Berichte & Sprache (E11): Sitzungsberichte Deutsch/Englisch sauber, Fachbegriffe erklärt. **Test:** beide Sprachmodi durchprobiert.
- CS-082: Geschwindigkeit: Screenshot-Pipeline (JPEG, Skalierung) + Gedächtnis-Treffer messen. **Ziel:** typische 5-Schritt-Aufgabe < 90 s.
- CS-083: Doku-Finalisierung: README auf Top-Standard (§14.5) — Quickstart auf dem Gerät getestet, „Bekannte Einschränkungen", Fehlerbehebung (Kopplung verloren, Zusatz-App gestoppt, Speicher voll); Anti-Slop-Lint grün; Vorbild-Abgleich gegen `docs/reference-repos.md` (e-Kategorie). **Test:** CI grün inkl. Lint; Quickstart frisch abgetippt und erfolgreich.

### W9 — Brücke & Abschluss (CS-090 … CS-092)
- CS-090: MCP-Manifest + Einbindungs-Anleitung für ClauDroide (§13). **Test:** Anleitung aus Sicht eines fremden MCP-Clients folgbar.
- CS-091: Sicherheits-Review: Sperrliste-Tests, Notbremsen-Dreifach-Check, Lokal-Bindung des Mini-Servers. **Test:** Checkliste abgearbeitet, Ergebnisse in BUILD-STATE.
- CS-092: Versionsstempel 1.0, Tag `v1.0.0`, Abschlussbericht.

**Reihenfolge-Regel:** Kein Task startet vor seinen `depends_on`. Unabhängige Aufgaben dürfen parallel (§14.2 Orchestrierung); Wellengrenzen sind Sync-Punkte.

---

## 16. Zukunftsausblick (E14) — bewusst eingeplant, jetzt nicht gebaut

Damit das Fundament passt, sind vorbereitet: Konfig-Schalter, Werkzeug-Namensräume, Protokoll-Format.

1. **Sprachsteuerung:** „Reden statt tippen" — Nutzer spricht Wunsch (z. B. über Mikrofon-Aufnahme in Termux oder Zusatz-App); Sprache→Text über Claude selbst oder lokale Erkennung; danach identischer Sitzungsablauf.
2. **Kopfhörer-Tasten als Bedienung:** Play/Pause-Knopf als „weiter/stop"-Fernbedienung (Zusatz-App fängt Medientasten ab — gleiche Technik wie Lautstärketasten).
3. **Geld-Apps freischalten (E10-Lösung):** Umschaltung auf `announce`-Modus mit lauter Ansage vor jeder Geld-Aktion; evtl. separater „Geld-Sitzungs"-Modus (Nutzer bestätigt nur die Geld-Schritte).
4. **Alle Sprachen (E11-Lösung):** Sprachwahl auf beliebige Sprachen erweitern (Konfig-Wert bereits freitextfähig, Berichts-Vorlagen lokalisieren).
5. **Plan-Vorschau-Modus:** Claude zeigt vor langen Aufgaben eine Bild-für-Bild-Vorschau des geplanten Wegs (aus dem Gedächtnis-Rezept), Nutzer nickt ab.
6. **Fremdgeräte:** Steuerung eines zweiten Android-Geräts (z. B. Tablet) über dasselbe MCP (ADB verbindet auch dorthin — Werkzeuge bekommen ein `gerät`-Argument vorbereitet).
7. **ClauDroide-Integration Vertiefung:** Eigene ClauDroide-Task-Kategorie „Screen-Aufträge", die ClawScreen-MCP direkt aufruft.

---

## 17. Annahmen & offene Punkte

| # | Annahme | Falls anders … |
|---|---|---|
| A1 | `gh` (GitHub-Werkzeug) ist in Debian eingerichtet (bei ClauDroide ja). | W0 stoppt mit Anleitung `gh auth login`. |
| A2 | Cubasis 3 ist installiert (Paketname `com.steinberg.cubasis`; wird in W7 verifiziert). | `screen_apps` liefert den echten Namen, Kochbuch passt sich an. |
| A3 | FL Studio Mobile ist installiert. | analog. |
| A4 | Nutzer genehmigt die Zusatz-App-Erlaubnisse einmalig beim `clawscreen setup`. | W4 fällt auf ADB-Modus zurück (eingeschränkt: keine Umlaute, kein Stopp-Knopf, keine Lautstärke-Bremse). |
| A5 | Entwickleroptionen sind aktiviert. | setup-Leitfaden erklärt den 7-mal-auf-Buildnummer-tippen-Weg. |
| A6 | Das lokale Interview-Verzeichnis (diese Spec) wird vor W0 nach `/home/mert/clawscreen` überführt. | CS-001 kopiert die Spec aus dem bestehenden Pfad. |
| A7 | `npx skills` ist in Debian verfügbar (Node vorhanden — Claude Code setzt es ohnehin voraus). | CS-005 installiert Node zuerst oder nutzt `gh`-Klon-Weg für Skills. |
| A8 | Netzwerkzugriff für GitHub-Suche/-Klone ist vorhanden. | CS-006 arbeitet dann mit gekürzter Liste und vermerkt es. |

---

## 18. Abnahme-Kriterien für Version 1.0 (das Projekt ist fertig, wenn …)

1. `clawscreen setup` führt einen Frischzustand (nach Handy-Neustart) bis zur einsatzbereiten Verbindung.
2. `/screen`-Sitzung: „Öffne Cubasis, lege ein Projekt ‚ClawTest' mit Schlagzeug + Bass an (100 BPM), spiele es ab" — **völlig autonom**, mit Protokoll und Prüfbildern.
3. Gleiche Klasse von Aufgabe in FL Studio Mobile.
4. „Schalte WLAN aus und wieder ein" autonom in einer Einzelanweisung.
5. Alle drei Notbremsen in einer laufenden Aktion messbar wirksam (< 1 s Reaktion).
6. Sperrliste: Play-Store-Öffnungsversuch und Kauf-Dialog werden zuverlässig geblockt und gemeldet.
7. Zweiter Lauf derselben Cubasis-Aufgabe nutzt das Gedächtnis (messbar weniger Sichten, schnellere Fertigstellung).
8. Repo `mertgoevse-wq/clawscreen` ist **privat**, CI grün (inkl. Anti-Slop-Lint), APK-Artefakt vorhanden, BUILD-STATE vollständig, **jede Aufgabe gepusht**.
9. Alles ohne Root, ohne Cloud-Zwischendienst; Screenshots verlassen das Gerät nicht.
10. **Resume bewiesen:** BUILD-STATE absichtlich um einen Schritt „zurückgesetzt" → `/clawscreen-resume` erkennt die Abweichung, heilt sie und baut weiter (E17).
11. **Skill-Betrieb bewiesen:** `tasks/skill-matrix.md` weist jeder Aufgabe ≥ 2 Skills zu; mindestens 4 Community-Skills sind global installiert und dokumentiert und wurden im Bau tatsächlich geladen (E15).
12. **Referenz-Beutezug bewiesen:** `docs/reference-repos.md` listet ≥ 50 Repos mit Übernahme-Entscheidungen; ≥ 5 Übernahmen sind im Code/Setup nachvollziehbar (E18).
13. **README-Standard:** Lint grün, Quickstart frisch abgetippt erfolgreich, keine Verbotsmuster (E20).

---

*Ende der Spec. Diese Datei ist die alleinige Baugrundlage für Claude Code. Änderungen nur mit Versions-Sprung und Eintrag in der Änderungshistorie oben.*
