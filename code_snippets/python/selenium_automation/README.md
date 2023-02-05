## Co jest czym w automatach

Core

- templates/mail_summary.html - templatka maila i strony z podsumowaniem testów obsługiwana przez Jinja2, zasilana tablicą przekazywaną w test_summary funkcją get_test_status_data()
- api.py - komunikacja z zewnętrznym API (szczegóły niżej)
- common_locators.py - lokalizatory do wspólnych elementów interfejsu (wyszukiwarki, flashe, moduły itp.)
- common_methods.py - obsługa akcji wspólnych dla elementów, typu wybór wartości w selekcie, wysyłka maila, jakieś gettery do atrybutów itp. (ogólnie reużywalne akcje na pojedynczych elementach interfejsu)
- dictionary.py - słownik ze stałymi wartościami wykorzystywanymi przy testach (dane logowania, routingi, treści komunikatów, requesty)
- fake_data_generator.py - generator fikcyjnych danych testowych (dane teleadresowe)
- *_locators.py - lokalizatory elementów z danego modułu
- settings_dictionary_data_getter.py - klasa obsługująca pobieranie danych z obiektów słownikowych z ustawień, w tej chwili zwraca wszystkie szczegóły z obiektu statusu zlecenia
- test_summary - skrypty stosowane w ostatnim stage, generuje podsumowanie testów i wysyła je do API i mailem

Purchase, Sale, Rcp, ServiceOrders, Lease, Warehouse - moduły z testami z poszczególnych obszarów systemu. Smoke to proste testy sprawdzające czy dane miejsce działa, w Functional są główne skrypty z testami. partial_operations.py to klasa w której znajdują się reużywalne akcje dotyczące poszczególnych obszarów danego modułu (np. dodanie wartości do rozliczeń, zatwierdzanie dokumentu sprzedaży).

Settings - testy słowników i skrypt do sprawdzania czy podgląd niesłownikowej strony z ustawień nie generuje kodu 500.

TestResults - tutaj zapisywane są screeny i inne didaskalia do analiz.

ValueStorage - tutaj przechowywane są generowane w trakcie testów pliki z danymi takie jak m.in.: adresy URL, numery zleceń, które wykorzystywane są wzajemnie przez różne moduły testowe. Są tam też pliki JSON z informacją o tym jakie scenariusze były wykonane i jaki jest ich status. Są one potem wykorzystywane przy generowaniu HTML z podsumowaniem.

## O co chodzi z API?
Po każdym stage generowany i zapisywany w ValueStorage jest plik JSON z informacją o wykonanych scenariuszach i ich rezultacie. Pliki te przekazywane są pomiędzy kolejnymi stage'ami i ich zawartość jest aktualizowana w trakcie trwania pipeline. W ostatnim stage, który obsługuje podsumowania, brana jest treść tych plików i na ich podstawie generowany jest zarówno mail jak i HTML ze szczegółami.

Po każdym stage wysyłane są do API pliki JSON. Pliki te pobierane są w ostatnim stage, dzięki czemu ma on dostęp do pełnej informacji po wykonanych scenariuszach. Pełne podsumowanie testów prezentowane jest potem na odrębnej stronie w wewnętrznej sieci. Całość komunikacji z API po stronie testów ogarnięta jest w klasie ApiCommunications w Core/api.py.

## Uruchomienie skryptu w PyCharm

python -m unittest {{ lokalizacja modułu }} np. python -m uniittest Lease.Smoke.lease_smoke

Wszystkie uruchamianie skrypty użyte są w pliku gitlab-ci.yml

Portfolio zawiera tylko niektóre pliki i funkcje z projektu źródłowego.
