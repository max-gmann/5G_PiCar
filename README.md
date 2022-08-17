<p align="center">
<img src="docs\images\smart-car.png" alt="drawing" width="200"/>
</p>
<center><h1>Project Stanley</h1></center>

___ 

### Übersicht
Der vorliegende Programmcode dient zur Ausführung auf einem Sunfounder Pi Car V mit WEBCAM.
Mit diesem Programm kann das Pi Car einer Linie folgen und Stopschilder erkennen und automatisch anhalten.
Ziel ist es den Latenzunterschied zwischen 4G und 5G zu verdeutlichen.

###### Verwendete Libraries/Pakete:
numpy: https://numpy.org/
OpenCV: https://opencv.org/
mathplotlib: https://matplotlib.org/
PyToch: https://pytorch.org/ 
conda-forge: https://conda-forge.org/
anaconda: https://www.anaconda.com/ 
pip: https://pypi.org/project/pip/

### Installation
Um den Code auf einem Windows Rechner auszuführen zu können müssen folgende Schritte befolgt werden.
Die Installation auf Mac und Linux kann abweichen.

1. Python 3.9 herunterladen und installieren.
 
		https://www.python.org/downloads/release/python-3912/

2. Repository clonen oder ZIP Archiv von 

		https://github.com/max-gmann/5G_PiCar 

herunterladen und am gewünschten Ort entpacken.
3. Im Ordner mit den entpackten Dateien ein Terminal öffnen, beispielsweise per Rechtsklick.
4. Neue virtuelle Umgebung erstellen:

		python -m venv venv

5. Virtuelle Umgebung aktivieren:

		.\venv\Scripts\activate

Sollte die Ausführung in der Windows PowerShell geblockt werden, kann folgendes Kommando helfen:

		Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Wurde die Umgebung erfolgreich aktiviert, wird der Name (venv) am Beginn der Zeile angezeigt (siehe Abbildung).
6. Benötigte Pakete installieren:

		pip install -r requirements.txt

7. Programm starten:

		python main.py

Für zukünftige Starts ist entscheidend, dass das Script aus dem Kontext der virtuellen Umgebung ausgeführt wird. 
Nur so kann der Python Interpreter alle relevanten Bibliotheken finden.
Gegebenenfalls müssen also die Schritte ab Schritt 5. erneut ausgeführt werden.

### Inbetriebnahme:

1. Pi Car anschalten.
2. Terminal im Ordner mit dem Pi Car Code starten.
3. Virtuelle Umgebung analog Schritt 5. aktivieren.
4. Main-Script starten.

        python main.py

5. Um das Programm zu beenden die Taste Q drücken.

Wurde das Fahrzeug erfolgreich gestartet, kann die Steuerung des Fahrzeugs beginnen. Es wird im manuellen Modus gestartet. 
In diesem Modus kann über die Tastatur mit folgender Tastenbelegung gesteuert werden:

<b>W</b>		vorwärts
<b>S</b>		rückwärts
<b>A</b>		links
<b>D</b>		rechts

<b>Q</b>		Programm beenden
<b>C</b>		4G / 5G Verbindungsmodus umschalten 
<b>M</b>		Umschalten manueller/automatischer Modus
<b>H</b>		Umschalten Erkennung heller/dunkler Linie
<b>F</b>		Linienerkennung aktivieren / deaktivieren (nur automatischer Modus)
<b>P</b>		Stoppschilderkennung aktivieren/deaktivieren (nur automatischer Modus)
<b>Leertaste</b>	Automatisches Vorwärtsfahren umschalten (nur automatischer Modus)
<b>Pfeiltasten</b>	Feinjustierung der Kamera
<b>1 bis 9</b>		Geschwindigkeit in 5-Schritten anpassen

In dem automatischen Modus kann die Erkennung von heller und dunkler Linie umgeschaltet werden, sowie in den manuellen Modus
zurück gewechselt werden.

### Dateien 

Im folgenden finden Sie Kurzerklärungen zu den jeweiligen Dateien.

##### main.py:
- Beinhaltet zentrale Steuerungsschleife
- erstellt eine Instanz der "pi_car" Klasse aus der Datei "Pi_Car_Controls.py" --> Stuerung des Autos und der Kamera 
- erstellt Instanz der "video_streamer" Klasse aus der "Streaming_Controls.py" Datei --> Verfügbarmachung jeglichen Bildmaterial
 der Fahrzeugkamera
- Instanz der "stop_sign" Klasse aus der "Object_Detector.py" Datei für die Stopschilderkennung und der "person" Klasse für 
 Personenerkennung
- für Verfolgung der Linien wird eine Instanz der "LineFollower" Klasse aus der "Line_Follower.py" Datei erstellt 

- keymapping, sprich eine Belegung der Tastatur Tasten, damit das Fahrzeug im manuellen Modus mit Tastaturbefehlen gesteuert 
 werden kann
- callback_fnc Funktion wird aufgerufen, wenn eine Taste gedrückt wird. Es wird die Geschwindigkeit des Autos gesetzt und es 
 kann zwischen manuellem und automatischem Modus umgeschaltet werden
- Hauptschleife ruftbenötigten Funktionen für die Linien/Stoppschild/Personen Erkennung auf, sowie die dadurch errechnete 
 Steuerung wird ausgeführt

##### Line_Follower.py: 
- Beinhaltet alle Funktionen die zum Folgen der Linie notwendig sind
- Weitwinkelbilder der Kamera werden auf unteren Teil zurechtgeschnitten --> Vermeidung von Fehlerkennung 
- 2 Kontrastfarbtöne sind einprogrammiert, um helle Linie oder dunkle Linie zu erkennen
- Linienmittelpunkt wird mit einem Kreis und damit X und Y Werten versehen
- Anhand des X Werts wird rechts und links gelenkt.

##### Pi_Car_Controls.py:
- Beinhaltet alle Funktionen zur Steuerung des Fahrzeugs
- Des Weiteren können gradgenaue Lenkwinkel und Kamerawinkel eingestellt werden
- Außerdem kann die Geschwindigkeit des Autos eingestellt werden

##### Streaming_Controls.py:
- Beinhaltet alle Funktionen die dazu dienen das Kamerabild zu erhalten und verwertbar zu machen

##### Object_Detector.py: 
- Basisklasse für die Erkennung von Hindernissen wie Stoppschildern.
