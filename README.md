# Alexa-YouTube-Skill

Dieser Skill ist für deutsche Alexa Nutzer.
This skill is for german Alexa users (english version maybe coming aswell)

### Möglichkeiten

* Direktes Abspielen von Songs
* Suchen und Auswahl von Songs
* Abspielen von Playlists
* Shufflen von Playlists
* Nächstes Lied der Playlist abspielen

### Utterances

* _"Alexa, öffne YouTube und spiele Adele - Someone like you"_
* _"Alexa, öffne YouTube und suche nach Prince - Purple Rain"_ **Alexa bietet jetzt die ersten 3 Treffer als Abspielmöglichkeiten an** _"Alexa, Nummer 2"_
* _"Alexa, öffne YouTube und starte Playlist"_
* _"Alexa, sage YouTube nächstes Lied"_

---

### Einrichtung
1. Skill erstellen auf der [Alexa Console](https://developer.amazon.com/alexa/console/ask)
2. intents.json in den JSON-Editor einfügen
3. Unter *Interfaces* den Audio-Player einschalten
4. Unter *Endpunkte* auf HTTPS schalten, unter *Default Location* Wildcard Zertifikate akzeptieren, und den Server auswählen, auf dem das Script laufen wird
5. *Save Model* und dann *Build Model*
6. Script auf dem Server starten, default Port ist **80**, sollte in der Regel aber geändert werden

#### Optional ####
```Wenn Playlisten verwendet werden sollen, dann muss in der main.py noch die PlaylistId eingetragen werden, so wie der API Key vom Google Konto (Resultate sind sonst auf 50 limitiert). Nicht vergessen in der Goolge Console die YouTube API freizuschalten für den API Key```

#### To Do ####
* Vorheriges Lied
* Code aufräumen
* Abfrage nach dem aktuellen Songnamen
* Hinzufügen des Songs zur eingetragenen Playlist
* und was mir sonst noch so einfällt


**WICHTIG: Dieses Projekt ist rein aus Spaß an der Freude entstanden. Ich mache damit kein Geld, und will keinerlei Lizenz- oder Copyrightrechte verletzen. Sollte mir, trotz großer Vorsicht, doch etwas entgangen sein, was einer Rechteverletzung nahe kommt, kontaktieren Sie mich bitte direkt, damit ich den Umstand umgehend lösen kann**
