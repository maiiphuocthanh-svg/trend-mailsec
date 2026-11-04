# -*- coding: utf-8 -*-
"""
send_tests.py
=============
Bo cong cu gui 10 loai email TEST toi mailbox dich de kiem thu
Trend Micro Cloud Email Gateway Protection (CEGP).

Su dung cac mau test CHUAN, VO HAI (EICAR, GTUBE). KHONG tao ma doc that.

Cach chay (Windows):
    python send_tests.py              -> chay TAT CA test case (tru #6/#9/#10)
    python send_tests.py 1 2 4        -> chi chay test case 1, 2, 4
    python send_tests.py --list       -> liet ke danh sach test case
    python send_tests.py --help       -> xem huong dan

Yeu cau: Python 3.8+ (khong can thu vien ben ngoai).
"""

import sys
import ssl
import time
import zipfile
import smtplib
import argparse
import configparser
from io import BytesIO
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate, make_msgid

import payloads

CONFIG_FILE = Path(__file__).parent / "config.ini"


# =====================================================================
#  TIEN ICH
# =====================================================================
def load_config() -> configparser.ConfigParser:
    """Doc file config.ini va kiem tra tinh hop le."""
    if not CONFIG_FILE.exists():
        sys.exit(f"[LOI] Khong tim thay file cau hinh: {CONFIG_FILE}")

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE, encoding="utf-8")

    user = cfg.get("smtp", "username", fallback="")
    pwd = cfg.get("smtp", "app_password", fallback="")
    if "your_gmail" in user or pwd in ("", "xxxxxxxxxxxxxxxx"):
        sys.exit(
            "[LOI] Ban chua cau hinh 'username' va 'app_password' trong "
            "config.ini.\n       Hay mo file config.ini va dien thong tin "
            "Gmail + App Password."
        )
    return cfg


def make_zip(inner_name: str, inner_bytes: bytes,
             password: str | None = None) -> bytes:
    """
    Tao file ZIP trong bo nho.
    Python zipfile chuan chi ho tro GHI zip khong ma hoa. De tao zip CO
    mat khau that su (ma hoa), ta tao thu cong theo chuan ZipCrypto.
    Neu co 'pyzipper' thi dung no de ma hoa AES (manh hon).
    """
    buf = BytesIO()

    if password:
        try:
            import pyzipper  # tuy chon: pip install pyzipper
            with pyzipper.AESZipFile(
                buf, "w",
                compression=pyzipper.ZIP_DEFLATED,
                encryption=pyzipper.WZ_AES,
            ) as zf:
                zf.setpassword(password.encode())
                zf.writestr(inner_name, inner_bytes)
            return buf.getvalue()
        except ImportError:
            print("      [i] Khong co 'pyzipper' -> tao ZIP khong ma hoa.")
            print("          (Cai de test file ma hoa: pip install pyzipper)")

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(inner_name, inner_bytes)
    return buf.getvalue()


def base_message(cfg, subject: str, from_addr: str | None = None
                 ) -> MIMEMultipart:
    """Tao khung email co ban voi header chuan."""
    msg = MIMEMultipart()
    msg["From"] = from_addr or cfg.get("smtp", "username")
    msg["To"] = cfg.get("recipient", "to")
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="mailtest.local")
    return msg


# =====================================================================
#  DINH NGHIA CAC TEST CASE
#  Moi ham tra ve mot doi tuong MIMEMultipart da san sang gui.
# =====================================================================
def tc1_spam(cfg):
    """#1 Spam Filtering - dung chuoi GTUBE chuan."""
    msg = base_message(cfg, "[TEST-01] Spam Filtering - GTUBE")
    body = (
        "Day la email test SPAM su dung chuoi GTUBE chuan.\n\n"
        f"{payloads.GTUBE}\n\n"
        "Ket qua mong doi: bi nhan dien Spam -> Quarantine/Block."
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))
    return msg


def tc2_virus(cfg):
    """#2 Virus Scan - dinh kem file EICAR."""
    msg = base_message(cfg, "[TEST-02] Virus Scan - EICAR attachment")
    msg.attach(MIMEText(
        "Email dinh kem file EICAR (file test antivirus chuan, vo hai).\n"
        "Ket qua mong doi: phat hien ma doc -> loai bo file / cach ly email.",
        "plain", "utf-8"))
    part = MIMEApplication(payloads.get_eicar_bytes(), Name="eicar.com")
    part["Content-Disposition"] = 'attachment; filename="eicar.com"'
    msg.attach(part)
    return msg


def tc3_content_filter(cfg):
    """#3 Content Filtering - file dinh kem lon (vuot nguong dung luong)."""
    msg = base_message(cfg, "[TEST-03] Content Filtering - large attachment")
    msg.attach(MIMEText(
        "Email dinh kem file lon de kiem tra chinh sach gioi han dung luong.\n"
        "Ket qua mong doi: vi pham chinh sach -> Block/Quarantine kem ly do.",
        "plain", "utf-8"))
    # Tao file ~12MB (dieu chinh neu nguong chinh sach cua ban khac)
    big_data = b"A" * (12 * 1024 * 1024)
    part = MIMEApplication(big_data, Name="large_file.bin")
    part["Content-Disposition"] = 'attachment; filename="large_file.bin"'
    msg.attach(part)
    return msg


def tc4_phishing(cfg):
    """#4 Phishing Filtering - gia mao From + noi dung lua dao mau."""
    spoof = cfg.get("options", "spoofed_from",
                    fallback="ceo@fecredit-secure.com")
    msg = base_message(cfg, "[TEST-04] CANH BAO: Tai khoan cua ban bi khoa!",
                       from_addr=spoof)
    msg["Reply-To"] = spoof
    msg.attach(MIMEText(payloads.PHISHING_BODY, "plain", "utf-8"))
    return msg


def tc5_sandboxing(cfg):
    """#5 Sandboxing - gui file high-risk (EICAR dong goi) cho Virtual Analyzer."""
    msg = base_message(cfg, "[TEST-05] Sandboxing - high-risk file")
    msg.attach(MIMEText(
        "Email dinh kem file high-risk de gui cho Virtual Analyzer phan tich.\n"
        "Dung EICAR dong goi trong ZIP de mo phong file nghi van.\n"
        "Ket qua mong doi: file duoc phan tich sandbox -> cach ly neu doc hai.",
        "plain", "utf-8"))
    zip_bytes = make_zip("sample.com", payloads.get_eicar_bytes())
    part = MIMEApplication(zip_bytes, Name="sample.zip")
    part["Content-Disposition"] = 'attachment; filename="sample.zip"'
    msg.attach(part)
    return msg


def tc6_whitelist_blacklist(cfg):
    """#6 Whitelist/Blacklist - huong dan (khong gui tu dong)."""
    return None  # Xem ghi chu ben duoi, test nay can cau hinh thu cong.


def tc7_password_file(cfg):
    """#7 File nen CO mat khau chua EICAR, mat khau ghi trong body."""
    pwd = cfg.get("options", "zip_password", fallback="infected")
    msg = base_message(cfg, "[TEST-07] Password-protected archive")
    body = (
        "Xin chao,\n\n"
        "Toi gui ban file dinh kem. File da duoc nen va dat mat khau.\n"
        f"Mat khau giai nen la: {pwd}\n\n"
        "Ket qua mong doi: he thong doc mat khau trong body, giai nen "
        "va quet file ben trong -> phat hien EICAR."
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))
    zip_bytes = make_zip("eicar.com", payloads.get_eicar_bytes(), password=pwd)
    part = MIMEApplication(zip_bytes, Name="protected.zip")
    part["Content-Disposition"] = 'attachment; filename="protected.zip"'
    msg.attach(part)
    return msg


def tc8_time_of_click(cfg):
    """#8 Time-of-Click Protection - email chua URL de kiem tra URL rewrite."""
    msg = base_message(cfg, "[TEST-08] Time-of-Click Protection - URL test")
    body = (
        "Email chua lien ket de kiem tra tinh nang Time-of-Click Protection.\n"
        "Khi click, URL phai duoc phan tich thoi gian thuc.\n\n"
        f"Lien ket test: {payloads.TIME_OF_CLICK_URL}\n\n"
        "Ket qua mong doi: link duoc viet lai/bao ve; click vao link doc "
        "se hien trang canh bao chan."
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))
    return msg


def tc9_dashboard(cfg):
    """#9 Dashboard - khong can payload, xem tren Console."""
    return None


def tc10_report(cfg):
    """#10 Report - khong can payload, xuat tren Console."""
    return None


# Ban do: so thu tu -> (ten, ham tao mail, co gui duoc tu dong khong)
TEST_CASES = {
    1:  ("Spam Filtering",            tc1_spam,                True),
    2:  ("Virus Scan",                tc2_virus,               True),
    3:  ("Content Filtering",         tc3_content_filter,      True),
    4:  ("Phishing Filtering",        tc4_phishing,            True),
    5:  ("Sandboxing",                tc5_sandboxing,          True),
    6:  ("Whitelist/Blacklist",       tc6_whitelist_blacklist, False),
    7:  ("Password-protected file",   tc7_password_file,       True),
    8:  ("Time-of-Click Protection",  tc8_time_of_click,       True),
    9:  ("Dashboard & Visibility",    tc9_dashboard,           False),
    10: ("Report Generation",         tc10_report,             False),
}


# =====================================================================
#  GUI MAIL
# =====================================================================
def send_via_smtp(cfg, messages):
    """Ket noi Gmail SMTP mot lan va gui tat ca message."""
    host = cfg.get("smtp", "host")
    port = cfg.getint("smtp", "port")
    user = cfg.get("smtp", "username")
    pwd = cfg.get("smtp", "app_password")
    delay = cfg.getint("options", "delay_seconds", fallback=5)

    print(f"\n[*] Ket noi {host}:{port} voi tai khoan {user} ...")
    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(user, pwd)
            print("[+] Dang nhap thanh cong!\n")

            total = len(messages)
            for i, (num, name, msg) in enumerate(messages, 1):
                # Envelope sender luon la tai khoan Gmail that (that bai neu khong)
                server.sendmail(user, [cfg.get("recipient", "to")],
                                msg.as_string())
                print(f"  [OK] ({i}/{total}) Test #{num:<2} {name} -> da gui")
                if i < total:
                    time.sleep(delay)
    except smtplib.SMTPAuthenticationError:
        sys.exit(
            "\n[LOI] Dang nhap that bai! Kiem tra lai:\n"
            "  - Da bat xac thuc 2 buoc (2FA) cho tai khoan Gmail chua?\n"
            "  - Da dung 'App Password' 16 ky tu (KHONG phai mat khau thuong)?\n"
        )
    except Exception as e:
        sys.exit(f"\n[LOI] Gui mail that bai: {e}")


# =====================================================================
#  MAIN
# =====================================================================
def print_list():
    print("\nDANH SACH TEST CASE:")
    print("-" * 60)
    for num, (name, _, auto) in TEST_CASES.items():
        tag = "tu dong" if auto else "thu cong (xem README)"
        print(f"  #{num:<2} {name:<28} [{tag}]")
    print("-" * 60)
    print("Cac test thu cong (#6, #9, #10) khong gui mail - thuc hien tren Console.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Gui email test cho Trend Micro Cloud Email Gateway Protection (CEGP).",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cases", nargs="*", type=int,
                        help="So thu tu test case can chay (vd: 1 2 4). "
                             "Bo trong = chay tat ca test tu dong.")
    parser.add_argument("--list", action="store_true",
                        help="Liet ke danh sach test case.")
    args = parser.parse_args()

    if args.list:
        print_list()
        return

    cfg = load_config()

    # Chon test case can chay
    if args.cases:
        selected = args.cases
    else:
        selected = [n for n, (_, _, auto) in TEST_CASES.items() if auto]

    messages = []
    skipped = []
    for num in selected:
        if num not in TEST_CASES:
            print(f"  [!] Bo qua test #{num}: khong ton tai.")
            continue
        name, builder, auto = TEST_CASES[num]
        if not auto:
            skipped.append((num, name))
            continue
        msg = builder(cfg)
        if msg is not None:
            messages.append((num, name, msg))

    if skipped:
        print("\n[i] Cac test sau can thuc hien THU CONG (xem README.md):")
        for num, name in skipped:
            print(f"    #{num} {name}")

    if not messages:
        print("\n[!] Khong co email nao de gui.")
        return

    print(f"\n[*] Chuan bi gui {len(messages)} email test toi "
          f"{cfg.get('recipient', 'to')}")
    send_via_smtp(cfg, messages)

    print("\n" + "=" * 60)
    print("[HOAN TAT] Da gui xong. Kiem tra ket qua tren CEGP Console:")
    print("  - Quarantine  : menu Quarantine")
    print("  - Log/Tracking: xem log mail trong CEGP (Mail Tracking / Policy Events)")
    print("  - Dashboard   : menu Dashboard")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
