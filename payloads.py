# -*- coding: utf-8 -*-
"""
payloads.py
-----------
Chua cac mau test CHUAN CONG NGHIEP, HOAN TOAN VO HAI, duoc moi hang
antivirus (bao gom Trend Micro) cong nhan de kiem tra chuc nang phat hien.

- EICAR : file test antivirus chuan (KHONG phai virus that).
          Tham khao: https://www.eicar.org/download-anti-malware-testfile/
- GTUBE : chuoi test spam chuan cua SpamAssassin (KHONG phai spam that).
          Tham khao: https://spamassassin.apache.org/gtube/

Cac mau nay chi dung de xac nhan he thong CO phat hien hay khong,
KHONG gay bat ky rui ro thuc su nao.
"""

# ---------------------------------------------------------------------
# GTUBE - Generic Test for Unsolicited Bulk Email (test SPAM)
# ---------------------------------------------------------------------
GTUBE = (
    "XJS*C4JDBQADN1.NSBN3*2IDNEN*"
    "GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X"
)

# ---------------------------------------------------------------------
# EICAR - Standard Anti-Virus Test File (test VIRUS / MALWARE)
# Chuoi 68 byte duoi day la file test AV chuan.
# ---------------------------------------------------------------------
EICAR = (
    r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR"
    r"-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
)


def get_eicar_bytes() -> bytes:
    """Tra ve noi dung file EICAR dang bytes de dinh kem."""
    return EICAR.encode("ascii")


# ---------------------------------------------------------------------
# Noi dung mau cho email PHISHING (mo phong - KHONG chua link doc that)
# ---------------------------------------------------------------------
PHISHING_BODY = """\
Kinh gui Quy khach,

Tai khoan ngan hang cua ban DA BI KHOA do phat hien dang nhap bat thuong.
De MO KHOA ngay lap tuc, vui long xac minh thong tin tai lien ket ben duoi
trong vong 24 gio, neu khong tai khoan se bi xoa vinh vien:

    http://secure-verify-login.example-phishing-test.com/verify?id=victim

Tran trong,
Bo phan An ninh - Ngan hang [Gia mao]
"""

# ---------------------------------------------------------------------
# URL mau dung cho test Time-of-Click (an toan, khong doc that)
# example.com la domain danh rieng cho muc dich test/tai lieu.
# ---------------------------------------------------------------------
TIME_OF_CLICK_URL = "http://malware-test.example.com/suspicious-link"
