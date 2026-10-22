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

Idea: **jeden** alarm z etykietą `Vultron`. Skrót co wieczór kasuje poprzedni alarm `Vultron` i tworzy nowy na wyliczoną godzinę (albo żadnego, gdy jutro wolne). Nic nie trzeba sprzątać ręcznie.

Wymagania: **iOS 18+** (akcje Zegara *Find Alarms* / *Delete Alarms* / *Add Alarm*) oraz aplikacja **Home Assistant Companion** połączona z Twoim HA.

### 0. Jednorazowo: pozwól kasować bez pytania

*Ustawienia → Skróty → Zaawansowane → Pozwól na usuwanie bez potwierdzania* (*Allow Deleting Without Confirmation*) → **włącz**. Bez tego *Delete Alarms* pyta o potwierdzenie przy każdym uruchomieniu.

### 1. Skrót (Shortcut)

Aplikacja **Skróty** → **+** → nazwa np. `Vultron budzik`. Dodaj akcje po kolei:

1. **Home Assistant → Render Template** (akcja z aplikacji HA), szablon:
   ```
   {{ state_attr('sensor.vultron_alarm_clock_budzik_na_jutro', 'alarm_time') or '' }}
   ```
   Wynik to `HH:MM` (np. `06:45`) albo pusty tekst.
2. **Find Alarms** (*Znajdź alarmy*) → filtr **Label** (*Etykieta*) **zawiera** `Vultron`.
3. **Delete Alarms** (*Usuń alarmy*) → wejście: *Alarms* z kroku 2. (Kasuje stary budzik `Vultron`; zwykłych alarmów bez tej etykiety nie rusza.)
4. **Jeśli** *Wynik szablonu* (krok 1) **ma dowolną wartość** (*has any value*):
   1. **Add Alarm** (*Dodaj alarm*): **Time** = *Wynik szablonu*, etykieta `Vultron`, **Powtarzaj: nigdy**.
5. **Koniec Jeśli**.

> Gdy jutro jest wolne, szablon zwraca pusty tekst → krok 4 nic nie tworzy, a stary alarm i tak został skasowany w kroku 3. Jeśli *Add Alarm* nie przyjmie tekstu `HH:MM` w Twojej wersji iOS, wstaw przed nim **Pobierz daty z danych wejściowych** (*Get Dates from Input*) na wyniku szablonu i podaj tę datę w polu *Time*.

Uruchom skrót **raz ręcznie** i przy *Delete Alarms* wybierz **Usuwaj zawsze** (*Delete Always*).

### 2. Automatyzacja osobista

1. Skróty → zakładka **Automatyzacje** → **+** → **Utwórz automatyzację osobistą** → **Pora dnia**.
2. Godzina **22:30**, powtarzaj **Codziennie** → *Dalej*.
3. Akcja **Uruchom skrót** → wybierz `Vultron budzik` → *Dalej*.
4. Ustaw **Uruchom natychmiast** (*Run Immediately*) i wyłącz **Powiadom po uruchomieniu** → *Gotowe*.

### Uwagi

- iPhone musi mieć o 22:30 dostęp do HA (Wi-Fi w domu lub zdalny URL/Nabu Casa).
- *Delete Alarms* nie działa na Apple Watch — czyszczenie rób na iPhonie (automatyzacja i tak jest na nim).
- Sensor przelicza się przy każdej zmianie planu oraz o 00:00:05 (wtedy „jutro” przeskakuje na kolejny dzień), więc wyzwalaj skrót wieczorem, nie po północy.

## Testy

`python tests/test_logic.py` – sprawdza logikę (weekendy, dni wolne, odwołane lekcje, offsety).
