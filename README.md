## Beschreibung
Das Projekt bedient mehrere Typen von Algorithmen aus dem Bereich der Ant Colony Optimization, Algorithmen mit Bezug zu Schwarm-Intelligenz.
Es dient zur Simulation dieser Algorithmen, Manipulation von Parametern und Manipulation des zugrundeliegenden Graphen zur Laufzeit.


## Installation
Um dieses Projekt auszuführen, müssen Sie die folgenden Python-Bibliotheken installieren. Dies können Sie tun, indem Sie die folgenden Befehle in Ihrem Terminal ausführen:

    pip install networkx matplotlib


## Einrichtung der Entwicklungsumgebung
Wenn Sie PyCharm verwenden, wird das Projektverzeichnis automatisch zum `PYTHONPATH` hinzugefügt. Wenn Sie das Projekt jedoch von der Kommandozeile ausführen möchten, müssen Sie sicherstellen, dass das Verzeichnis `aco_routing` im `PYTHONPATH` enthalten ist.

### Schritte zur Einrichtung in der Kommandozeile (CMD)
1. Navigieren Sie zu Ihrem Projektverzeichnis:
    ```cmd
    cd path\to\your\project\minority-ants
    ```

2. Setzen Sie den `PYTHONPATH`:
    ```cmd
    set PYTHONPATH=%PYTHONPATH%;path\to\your\project\minority-ants\aco_routing
    ```

3. Führen Sie das Skript aus:
    ```cmd
    python main.py
    ```

### Schritte zur Einrichtung in der PowerShell
1. Navigieren Sie zu Ihrem Projektverzeichnis:
    ```powershell
    cd path\to\your\project\minority-ants
    ```

2. Setzen Sie den `PYTHONPATH`:
    ```powershell
    $env:PYTHONPATH = "$env:PYTHONPATH;path\to\your\project\minority-ants"
    ```

3. Führen Sie das Skript aus:
    ```powershell
    python .\aco_routing\main.py
    ```

## Projektstruktur
Stellen Sie sicher, dass Ihre Verzeichnisstruktur wie folgt aussieht:

```
minority-ants/
├── aco_routing/
│   ├── __init__.py
│   ├── ant_colony_runner.py
│   ├── graph_tools.py
│   ├── main.py
│   ├── minority_ant.py
│   ├── plot.py
│   ├── random_ant.py
│   ├── routing_ant.py
│   └── wave_config.py
└── configurations/
    └── minority_2d_grid_torus.json
```

Mit diesen Schritten sollte Ihr Skript die notwendigen Module und Dateien korrekt finden und importieren können.

## Start
Einfach die main.py mit Python ausführen

    python .\aco_routing\main.py


