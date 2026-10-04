# ClawScreen

ClawScreen lässt eine KI den Bildschirm **deines eigenen Android-Smartphones**
sehen und bedienen — ohne Root, ohne dass du jeden Schritt freigibst.

Gesteuert wird ein Samsung Galaxy A56 5G. Die KI läuft **auf dem Telefon selbst**
(Termux mit Debian), das Telefon ist also gleichzeitig Rechner und Zielgerät.

> **Wichtig:** Es besteht keine Verbindung zu Anthropic. Das Wort „Claude" steht
> nur als Name des Assistenten, mit dem ClawScreen zusammenarbeitet.

## Inhaltsverzeichnis

- [Was ClawScreen tut](#was-clawscreen-tut)
- [Funktionsstand](#funktionsstand)
- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [Wie es funktioniert](#wie-es-funktioniert)
- [Sicherheit](#sicherheit)
- [Bekannte Einschränkungen](#bekannte-einschränkungen)
- [Problembehebung](#problembehebung)
- [Mitwirken](#mitwirken)
- [Lizenz](#lizenz)

## Was ClawScreen tut

Ein Beispiel aus dem Alltag. Du sagst:

> `/screen` — Baue mir in Cubasis ein Projekt mit Schlagzeug und Bass, Tempo 100.

ClawScreen sieht den Bildschirm, plant, tippt, wischt, tippt Text, **prüft jeden
Schritt anhand eines frischen Bildes** und berichtet am Ende, was es getan hat.
Das funktioniert nicht nur mit Musik-Apps — mit allem, was auf dem Bildschirm
passiert: Einstellungen, andere Apps, jede Bedienung.

Die Bedienung läuft über Android Debugging (ADB). Das ist eine offizielle
Schnittstelle von Android und braucht keine Superuser-Rechte.

## Funktionsstand

Dieses Projekt wird gerade gebaut. Der Stand steht in
[`progress/BUILD-STATE.md`](progress/BUILD-STATE.md), der Fortschritt in klarer
Sprache in [`docs/fortschritt.md`](docs/fortschritt.md).

| Bereich | Stand |
|---|---|
| Verbindung und Steuerung | wird gebaut |
| Werkzeuge (sehen, tippen, Text eingeben) | wird gebaut |
| Begleit-App (Android) | geplant |
| Sicherheit und Notbremse | geplant |
| Bedienung von Cubasis und FL Studio | geplant |

## Installation

ClawScreen wird auf einem Android-Handy mit Termux aufgebaut. Es gibt keine
fertige App im Play Store.

Voraussetzungen:

- Android 11 oder neuer (getestet mit Android 15)
- [Termux](https://f-droid.org/packages/com.termux/)
- eine Debian-Umgebung darin (`proot-distro install debian`)
- Node.js für den MCP-Server

Die vollständige Anleitung steht in der Spezifikation (`clawscreen-spec.md`,
Abschnitt 16). Der Schnellstart unten gilt, sobald der Bau abgeschlossen ist.

## Schnellstart

```bash
# Repository holen
git clone https://github.com/mertgoevse-wq/clawscreen.git
cd clawscreen

# Verbindung einmalig herstellen (zeigt genau an, was zu tun ist)
./cli/clawscreen pair

# Prüfen, ob alles bereit ist
./cli/clawscreen status
```

## Wie es funktioniert

Kurz erklärt, damit klar ist, was passiert — die technischen Einzelheiten stehen
in der Spezifikation.

**ADB (Android Debug Bridge)** ist die offizielle Schnittstelle von Android.
Über sie lassen sich Bildschirmfotos machen, tippen, wischen und Texte senden.

**MCP** ist ein Standard-Format für Werkzeuge: ClawScreen stellt seine
Werkzeuge als einen MCP-Server bereit, damit die KI sie wie eingebaute Werkzeuge
benutzen kann.

**Der Begleit-Dienst** (ClawScreen Companion) ist eine kleine App, die nur das
kann, was ADB nicht kann: geschützte Bildschirme lesen, den Bildschirm wach
halten, eine Notbremse als schwebenden Knopf anzeigen und Umlaute eingeben.

**Das Gedächtnis** merkt sich pro App, wo die wichtigen Stellen auf dem
Bildschirm sind. Jedes Mal, wenn es eine App steuert, wird dieser Ort zuverlässiger.

**Der Bildschirmstream** (scrcpy) überträgt den Bildschirm als schnelles Bild
und verarbeitet Tippen sehr zügig. Er läuft nur, solange wirklich geschaut wird,
damit der Akku nicht leidet.

## Sicherheit

Drei Dinge sind fest eingebaut:

1. **Geld-Apps bleiben gesperrt** — Bank-, Zahlungs- und Shopping-Apps, auch der
   Play Store. Kaufbestätigungs-Dialoge werden nie bestätigt.
2. **Drei Notbremsen** — `stop` im Chat, ein schwebender roter Knopf auf dem
   Bildschirm, und zweimal schnell „Lautstärke runter".
3. **Nichts wird gelöscht** — keine App, keine Datei. Das ist eine feste Regel
   des Projekts, im Code erzwungen.

Alle Daten bleiben auf dem Telefon. Der Begleit-Dienst hört nur auf der
Rückseite des eigenen Geräts (`127.0.0.1`).

## Bekannte Einschränkungen

Ehrlich benannt, statt zu beschönigen:

- **Der spezielle KI-Chip des Telefons (NPU) ist für Apps nicht erreichbar.**
  ClawScreen nutzt daher den Grafikchip (GPU) und die CPU für lokale Helfer.
  Alles funktioniert auch ohne sie — sie machen nur schneller.
- **Bilder von Apps, die selbst zeichnen** (Cubasis, FL Studio Mobile), geben
  über ADB wenig Text preis. Dort arbeitet ClawScreen mit Bildern allein.
- **Die Portnummer der Funkverbindung ändert sich** nach einem Neustart des
  Telefons und muss neu gefunden werden.
- **Ein Neustart des Assistenten setzt die Sitzung zurück** — einfach neu
  starten, es geht nichts verloren.

## Problembehebung

**Die Verbindung klappt nicht mehr** (nach einem Neustart des Telefons):

```bash
./cli/clawscreen connect
```

Reicht das nicht, einmal neu koppeln:

```bash
./cli/clawscreen pair
```

**Der Begleit-Dienst reagiert nicht:**

```bash
./cli/clawscreen status
```

Der Befehl sagt, welcher Schritt fehlt.

**Der Bildschirm geht aus** — während einer Sitzung bleibt er an. Nach dem
Beenden wird er wieder normal aus.

**Ein Text mit Umlauten kommt nicht an** — dafür braucht ClawScreen den
Begleit-Dienst. Ohne ihn wird Umlaut-ersatz geschrieben (`ue` statt `ü`).

## Mitwirken

ClawScreen wird autonom gebaut. Die Arbeitsweise steht in
[`CLAUDE.md`](CLAUDE.md) und in der Spezifikation, Abschnitt 14. Beiträge laufen
über die dort beschriebenen Aufgaben (`tasks/`).

## Lizenz

Noch nicht festgelegt. Wird mit der Freigabe der ersten Version entschieden.