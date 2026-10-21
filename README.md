# Vultron Alarm Clock

Integracja Home Assistant (HACS), która wylicza godzinę budzika na **następny dzień** na podstawie najwcześniejszej lekcji wszystkich dzieci z integracji Vultron:

```
budzik = najwcześniejszy start lekcji − czas dojazdu − czas na zebranie się
```

Pomijane: soboty, niedziele, dni wolne (atrybut `dni_wolne` sensorów Vultron) oraz lekcje o statusie z listy pomijanych (domyślnie `ODWOL` – odwołane). Gdy jutro nie ma budzika, encja ma stan `unknown`, a atrybut `reason` mówi dlaczego (`weekend` / `dzien_wolny` / `brak_lekcji`).

## Instalacja (HACS)

1. HACS → ⋮ → *Custom repositories* → wklej URL tego repo, kategoria **Integration**.
2. Zainstaluj *Vultron Alarm Clock*, zrestartuj Home Assistanta.
3. *Ustawienia → Urządzenia i usługi → Dodaj integrację → Vultron Alarm Clock*.

## Konfiguracja

| Pole | Opis | Domyślnie |
|---|---|---|
| Sensory planu Vultron | sensory `sensor.vultron_plan_<dziecko>_curr/_next` (z atrybutem `lekcje`) – wykrywane automatycznie | wszystkie `sensor.vultron_plan_*` |
| Czas dojazdu (min) | | 30 |
| Czas na zebranie się (min) | | 45 |
| Pomijane statusy | po przecinku | `ODWOL` |

Zmiana później: *Konfiguruj* przy integracji (opcje).

## Encja

`sensor.vultron_alarm_clock_budzik_na_jutro` (klasa `timestamp`) – stan to moment budzika. Atrybuty:
`alarm_time` (lokalne `HH:MM`, to czyta iOS), `date`, `first_lesson`, `reason`, `travel_minutes`, `prep_minutes`.

> Dokładne entity_id sprawdź w *Ustawienia → Encje* (zależy od nazwy urządzenia).

## Automatyzacja na iPhonie (codziennie 22:30)

Wymagania: aplikacja **Home Assistant Companion** na iPhonie, połączona z Twoim HA.

### 1. Skrót (Shortcut)

Aplikacja **Skróty** → **+** → nazwa np. `Vultron budzik`. Dodaj akcje po kolei:

1. **Home Assistant → Render Template** (akcja z aplikacji HA), szablon:
   ```
   {{ state_attr('sensor.vultron_alarm_clock_budzik_na_jutro', 'alarm_time') or '' }}
   ```
   Wynik to `HH:MM` (np. `06:45`) albo pusty tekst.
2. **Jeśli** *Wynik szablonu* **ma dowolną wartość** (*has any value*):
   1. **Pobierz daty z danych wejściowych** (*Get Dates from Input*) – wejście: wynik szablonu (wskaże dzisiejszą datę z tą godziną; wystarczy, bo budzik dzwoni o najbliższym wystąpieniu godziny, czyli jutro rano po 22:30).
   2. **Utwórz alarm** (*Create Alarm*): godzina = *Daty* z poprzedniego kroku, etykieta `Vultron`, **Powtarzaj: nigdy**.
3. **W przeciwnym razie**: *Pokaż powiadomienie* „Jutro bez budzika” (opcjonalnie).
4. **Koniec Jeśli**.

> Jeśli akcja *Utwórz alarm* nie przyjmuje daty z kroku 2.1 w Twojej wersji iOS, użyj: **Tekst** → wynik szablonu, **Pobierz daty z danych wejściowych**, i wskaż tę zmienną w polu *Godzina*.

### 2. Automatyzacja osobista

1. Skróty → zakładka **Automatyzacje** → **+** → **Utwórz automatyzację osobistą** → **Pora dnia**.
2. Godzina **22:30**, powtarzaj **Codziennie** → *Dalej*.
3. Akcja **Uruchom skrót** → wybierz `Vultron budzik` → *Dalej*.
4. Ustaw **Uruchom natychmiast** (*Run Immediately*) i wyłącz **Powiadom po uruchomieniu** → *Gotowe*.

### Uwagi

- iPhone musi mieć wtedy dostęp do HA (Wi-Fi w domu lub zdalny URL/Nabu Casa) i nie może być w trybie, który blokuje uruchomienie automatyzacji (np. odblokowany lub z włączonym „Uruchom natychmiast”).
- Alarmy nie-powtarzalne wyłączają się po zadzwonieniu, więc kolejne dni nie nakładają się. iOS nie pozwala skrótom usuwać alarmów – nieaktywne wpisy `Vultron` czyść ręcznie od czasu do czasu.
- Sensor przelicza się przy każdej zmianie planu oraz o 00:00:05 (wtedy „jutro” przeskakuje na kolejny dzień), więc wyzwalaj skrót wieczorem, nie po północy.

## Testy

`python tests/test_logic.py` – sprawdza logikę (weekendy, dni wolne, odwołane lekcje, offsety).
