import getpass
import sys
from database import SessionLocal, engine, Base
from models import Auditor, WhistleblowerReport, AccessLog
import crypto_utils as crypto

# Automatyczne tworzenie tabel w bazie przy starcie
Base.metadata.create_all(bind=engine)


def get_db():
    return SessionLocal()


# --- REJESTRACJA AUDYTORA ---
def register_auditor_interactive():
    print("\n--- REJESTRACJA NOWEGO AUDYTORA ---")
    username = input("Podaj nazwę użytkownika: ")
    # getpass ukrywa wpisywane znaki
    password = getpass.getpass("Podaj hasło (nie będzie widoczne): ")

    db = get_db()
    if db.query(Auditor).filter(Auditor.username == username).first():
        print("!!! BŁĄD: Taki użytkownik już istnieje !!!")
        return

    # Haszowanie hasła i generowanie sekretu 2FA
    hashed = crypto.hash_password(password)
    secret = crypto.generate_2fa_secret()

    new_auditor = Auditor(username=username, password_hash=hashed, two_factor_secret=secret)
    db.add(new_auditor)
    db.commit()

    print(f"\n[SUKCES] Utworzono konto.")
    print(f"Twój SEKRET 2FA (wpisz w Google Authenticator): {secret}")
    print("Zapisz go, nie zostanie wyświetlony ponownie!")


# --- ZGŁASZANIE NADUŻYCIA (SYGNALISTA) ---
def submit_report_interactive():
    print("\n--- ZGŁOŚ NADUŻYCIE (ANONIMOWO) ---")
    print("Twoje zgłoszenie zostanie natychmiast zaszyfrowane algorytmem AES-256.")
    category = input("Kategoria (np. Korupcja, Mobbing): ")
    content = input("Treść zgłoszenia: ")

    # Szyfrowanie przed zapisem do bazy
    encrypted = crypto.encrypt_aes(content)

    db = get_db()
    report = WhistleblowerReport(category=category, encrypted_content=encrypted)
    db.add(report)
    db.commit()
    print(f"\n[SUKCES] Zgłoszenie przyjęte. ID zgłoszenia: {report.id}")


# --- PANEL AUDYTORA ---
def auditor_panel():
    print("\n--- LOGOWANIE DO SYSTEMU AUDYTORA ---")
    username = input("Login: ")
    password = getpass.getpass("Hasło: ")

    db = get_db()
    user = db.query(Auditor).filter(Auditor.username == username).first()

    # Weryfikacja Argon2
    if not user or not crypto.verify_password(user.password_hash, password):
        print("!!! BŁĄD: Niepoprawne dane logowania !!!")
        return

    print(f"\nWitaj, {user.username}. Zalogowano pomyślnie.")

    while True:
        print("\n--- PANEL AUDYTORA ---")
        print("1. Lista zgłoszeń (tylko metadane)")
        print("2. ODCZYTAJ zgłoszenie (Wymaga 2FA)")
        print("3. Pokaż logi dostępowe")
        print("4. Wyloguj")

        choice = input("Wybór > ")

        if choice == '1':
            reports = db.query(WhistleblowerReport).all()
            print("\nID | Kategoria | Data | Status")
            print("-" * 40)
            for r in reports:
                print(f"{r.id} | {r.category} | {r.created_at.strftime('%Y-%m-%d %H:%M')} | {r.status}")

        elif choice == '2':
            try:
                r_id = int(input("Podaj ID zgłoszenia do odszyfrowania: "))
                report = db.query(WhistleblowerReport).filter(WhistleblowerReport.id == r_id).first()
                if not report:
                    print("Nie znaleziono zgłoszenia.")
                    continue

                # KRYTYCZNY PUNKT: Weryfikacja 2FA
                code = input("Podaj kod 6-cyfrowy z aplikacji 2FA: ")
                if not crypto.verify_2fa_code(user.two_factor_secret, code):
                    print("!!! ODMOWA DOSTĘPU: Błędny kod 2FA !!!")
                    # Logowanie incydentu bezpieczeństwa
                    db.add(AccessLog(auditor_username=user.username, report_id=r_id, action="DECRYPT_FAILED"))
                    db.commit()
                    continue

                # Odszyfrowanie (tylko jeśli 2FA poprawne)
                decrypted = crypto.decrypt_aes(report.encrypted_content)
                print("\n" + "=" * 20 + " TREŚĆ ZGŁOSZENIA " + "=" * 20)
                print(decrypted)
                print("=" * 60)

                # Logowanie sukcesu
                db.add(AccessLog(auditor_username=user.username, report_id=r_id, action="DECRYPT_SUCCESS"))
                report.status = "READ"
                db.commit()
                input("\nNaciśnij ENTER, aby ukryć dane...")

            except ValueError:
                print("Błędny format ID.")

        elif choice == '3':
            logs = db.query(AccessLog).order_by(AccessLog.timestamp.desc()).limit(10).all()
            print("\n--- OSTATNIE LOGI DOSTĘPOWE ---")
            for log in logs:
                print(f"[{log.timestamp}] User: {log.auditor_username} -> Report: {log.report_id} -> {log.action}")

        elif choice == '4':
            print("Wylogowano.")
            break


def main():
    while True:
        print("\n" + "#" * 40)
        print("   WHISTLEBLOWER SECURE SYSTEM (CLI)")
        print("#" * 40)
        print("1. Zgłoś nadużycie (Dla każdego)")
        print("2. Panel Audytora (Logowanie)")
        print("3. Rejestracja nowego Audytora")
        print("0. Wyjście")

        choice = input("\nWybierz opcję > ")

        if choice == '1':
            submit_report_interactive()
        elif choice == '2':
            auditor_panel()
        elif choice == '3':
            register_auditor_interactive()
        elif choice == '0':
            print("Do widzenia.")
            sys.exit()
        else:
            print("Nieznana opcja.")


if __name__ == "__main__":
    main()