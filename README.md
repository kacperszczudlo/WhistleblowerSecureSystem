# 🛡️ Whistleblower Secure System (CLI)

**Whistleblower Secure System** to bezpieczna, konsolowa aplikacja (CLI) służąca do anonimowego zgłaszania nadużyć (sygnalista) oraz ich bezpiecznego przetwarzania przez audytorów.

Projekt został stworzony w ramach zaliczenia przedmiotu **Kryptografia**. Głównym celem systemu jest zapewnienie poufności zgłoszeń poprzez silne szyfrowanie danych ("Data at Rest") oraz wielopoziomową kontrolę dostępu.

## 🚀 Kluczowe Funkcjonalności

1.  **Anonimowe Zgłaszanie:** Każdy użytkownik może wysłać zgłoszenie. Treść jest natychmiast szyfrowana, zanim trafi do bazy danych.
2.  **Szyfrowanie AES-256 (CBC):** Treść donosów jest nieczytelna dla administratorów bazy danych. Do każdego rekordu generowany jest unikalny wektor inicjujący (IV).
3.  **Haszowanie Haseł (Argon2):** Hasła audytorów są zabezpieczone algorytmem odpornym na ataki brute-force (GPU/ASIC).
4.  **Step-up Authentication (2FA):** Zalogowanie się na konto audytora nie wystarczy, aby odczytać zgłoszenie. System wymaga podania jednorazowego kodu TOTP (Google Authenticator) przy każdej próbie deszyfracji.
5.  **Audit Logs:** Każda próba dostępu do danych (udana lub nieudana) jest rejestrowana w niezmienialnym logu systemowym.

## 🛠️ Technologie

* **Język:** Python 3.10+
* **Baza danych:** PostgreSQL
* **ORM:** SQLAlchemy
* **Kryptografia:**
    * `argon2-cffi` (Haszowanie haseł)
    * `cryptography` (Szyfrowanie AES-CBC)
    * `pyotp` (Generowanie kodów 2FA)

## ⚙️ Instalacja i Uruchomienie

1.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/twoj-nick/whistleblower-secure-cli.git](https://github.com/twoj-nick/whistleblower-secure-cli.git)
    cd whistleblower-secure-cli
    ```

2.  **Stwórz i aktywuj środowisko wirtualne (opcjonalnie):**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Zainstaluj zależności:**
    ```bash
    pip install sqlalchemy psycopg2-binary argon2-cffi cryptography pyotp
    ```

4.  **Konfiguracja Bazy Danych:**
    Upewnij się, że plik `database.py` zawiera poprawne dane logowania do instancji PostgreSQL. Tabela zostanie utworzona automatycznie przy pierwszym uruchomieniu.

5.  **Uruchom aplikację:**
    ```bash
    python main.py
    ```

## 📖 Instrukcja Obsługi (Scenariusz Testowy)

### 1. Rejestracja Audytora
* Wybierz opcję **`3`** w menu głównym.
* Utwórz login i hasło.
* **WAŻNE:** Zapisz wyświetlony sekret 2FA i dodaj go do aplikacji Google Authenticator (lub np. [totp.danhersam.com](https://totp.danhersam.com/)).

### 2. Zgłoszenie Nadużycia (Rola Sygnalisty)
* Wybierz opcję **`1`**.
* Wpisz kategorię (np. "Korupcja") i treść zgłoszenia.
* System potwierdzi zapisanie zaszyfrowanego zgłoszenia.

### 3. Panel Audytora (Odczyt Danych)
* Wybierz opcję **`2`** i zaloguj się.
* Wybierz **`1`**, aby zobaczyć listę zgłoszeń (treść jest ukryta).
* Wybierz **`2`**, aby odszyfrować konkretne zgłoszenie.
    * System poprosi o kod **2FA**.
    * Podanie błędnego kodu zablokuje dostęp i zapisze incydent w logach.
    * Podanie poprawnego kodu wyświetli odszyfrowaną treść.

### 4. Weryfikacja Logów
* Wybierz opcję **`3`** w panelu audytora, aby przejrzeć historię dostępów (`DECRYPT_SUCCESS` / `DECRYPT_FAILED`).

## 🔐 Szczegóły Implementacji Bezpieczeństwa

### Szyfrowanie Danych (AES-256)
Wykorzystujemy algorytm **AES** w trybie **CBC** (Cipher Block Chaining).
* Dla każdego zgłoszenia generowany jest losowy, 16-bajtowy **IV (Initialization Vector)**.
* IV jest doklejany do szyfrogramu w bazie danych.
* Zapobiega to atakom statystycznym – dwa identyczne zgłoszenia (np. "Kradzież") będą miały w bazie zupełnie inne ciągi bajtów.

### Bezpieczeństwo Haseł (Argon2id)
Zamiast przestarzałych funkcji skrótu (MD5, SHA256), używamy **Argon2**.
* Parametry: `time_cost=2`, `memory_cost=64MB`, `parallelism=2`.
* Algorytm jest "memory-hard", co drastycznie utrudnia łamanie haseł przy użyciu kart graficznych (GPU) i dedykowanych koparek (ASIC).

### Kontrola Dostępu (2FA)
System implementuje mechanizm **TOTP (Time-based One-Time Password)** zgodny z RFC 6238.
Kod 2FA jest wymagany nie przy logowaniu, ale przy **krytycznej operacji deszyfracji**. Stanowi to ochronę przed przejęciem sesji (Session Hijacking) lub kradzieżą hasła audytora.

---
*Autor: Kacper Szczudło | Projekt na zajęcia z Kryptografii*
