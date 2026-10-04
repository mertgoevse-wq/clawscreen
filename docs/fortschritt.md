# Fortschritt in einfachen Worten

Diese Seite ist für Menschen, die den technischen Aufbau nicht kennen. Hier
steht, was gebaut wurde und wie weit es ist — ohne Fachbegriffe.

## Kurz erklärt: worum es geht

ClawScreen ist ein Werkzeug, das einer KI hilft, den Bildschirm deines eigenen
Telefons zu sehen und zu bedienen. Statt selbst zu tippen, sagt man ihr, was
geschehen soll, und sie macht es. Das Telefon bleibt dabei in deiner Hand: Es
werden keine Apps gelöscht, keine Daten gelöscht, und Geld-Apps bleiben
gesperrt.

## Wie der Bau abläuft

Die Arbeit ist in Wellen aufgeteilt. Jede Welle baut etwas Brauchbares auf, was
die vorige braucht.

| Welle | Inhalt | Stand |
|---|---|---|
| 0 | Grundgerüst: Repository, Regeln, Prüfwerkzeuge, Wissenssammlung | im Bau |
| 1 | Erste funktionierende Vorführung | offen |
| 2 | Alle Werkzeuge vollständig | offen |
| 3 | Sicherheit und Notbremsen | offen |
| 4 | Begleit-App für das Telefon | offen |
| 5 | Verbindung richtet sich selbst ein | offen |
| 6 | Gedächtnis für Apps | offen |
| 7 | Cubasis und FL Studio bedienen | offen |
| 8 | Alltag, Tempo, fertige Dokumentation | offen |
| 9 | Anbindung an andere Systeme, Abschlussprüfung | offen |
| 10 | Optionale Beschleunigung mit Grafikchip | offen |

Welle 1 kommt bewusst zuerst: Du sollst früh etwas Echtes sehen und bestätigen
können, dass der Weg stimmt.

## Stand 2026-10-04

**Fertig:**

- Das Repository ist angelegt und privat. Niemand außer dir sieht es.
- Die Bauanweisungen liegen vor, kompakt und auf Deutsch.
- Die Liste aller Arbeitspakete existiert (47 Stück) mit Abhängigkeiten und
  Prüfungen.
- Zwei Prüfwerkzeuge laufen und melden ehrlich, wenn etwas nicht stimmt.

**Gerade in Arbeit:** die Vorbereitung der Verbindung zum Telefon.

## Wichtige ehrliche Angaben

- Der besondere KI-Chip im Telefon ist für Apps nicht erreichbar. ClawScreen
  nutzt stattdessen den Grafikchip und die CPU. Alles funktioniert auch ohne
  diese Helfer — sie machen nur schneller.
- Manche Apps (Cubasis, FL Studio Mobile) zeichnen ihren Bildschirm selbst. Über
  die Schnittstelle sieht man dort fast keinen Text. ClawScreen erkennt das und
  arbeitet dann mit Bildern allein.
- ClawScreen braucht Verbindung zum Telefon. Ohne sie kann es nichts sehen.

## Wie du den Stand prüfen kannst

```bash
# Womit gerade gebaut wird und was offen ist
python3 tools/sync_frontmatter.py --list

# Ob die Prüfwerkzeuge selbst noch stimmen
python3 tools/sync_frontmatter.py --check
python3 tools/anti-slop.py --self-test
```