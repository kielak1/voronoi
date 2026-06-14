# Voronoi

Generator ograniczonego diagramu Voronoi napisany w Pythonie. Komorki sa
wyznaczane przez przycinanie wielokata kolejnymi polplaszczyznami, dzieki
czemu program obsluguje takze punkty wspolliniowe i zduplikowane.

## Instalacja

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Uruchomienie

Wygenerowanie przykladowego diagramu do pliku `voronoi.png`:

```powershell
python voronoi.py
```

Wlasne punkty i otwarcie obrazu:

```powershell
python voronoi.py --points 0,0 4,0 2,3 --output wynik.png --show
```

Dostepne opcje:

```powershell
python voronoi.py --help
```

## Testy

```powershell
python -m unittest -v
```
