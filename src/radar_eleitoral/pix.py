"""Módulo utilitário para geração de BR Code Pix (EMVCo) e QR Code vetorial (SVG)."""

import unicodedata

import segno


def sanitize_text(text: str, max_length: int) -> str:
    """Remove acentos, caracteres especiais e trunca o texto para o padrão EMVCo."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(c for c in normalized if not unicodedata.combining(c) and ord(c) < 128)
    return ascii_only[:max_length].strip()


def format_tlv(tag: str, value: str) -> str:
    """Formata um campo no padrão Tag-Length-Value (TLV) do EMVCo."""
    length = len(value.encode("utf-8"))
    return f"{tag}{length:02d}{value}"


def calculate_crc16(payload: str) -> str:
    """Calcula o checksum CRC16-CCITT (polinômio 0x1021, init 0xFFFF) do EMVCo."""
    data = payload.encode("utf-8")
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def generate_pix_payload(
    key: str,
    name: str,
    city: str,
    txid: str = "***",
    amount: float | None = None,
) -> str:
    """Monta a string oficial do Pix Copia-e-Cola (BR Code padrão Banco Central)."""
    sanitized_name = sanitize_text(name, max_length=25)
    sanitized_city = sanitize_text(city, max_length=15)
    sanitized_txid = sanitize_text(txid, max_length=25) or "***"

    pfi = format_tlv("00", "01")
    pim = format_tlv("01", "11")  # Point of Initiation Method: Static QR Code
    gui = format_tlv("00", "br.gov.bcb.pix")
    pix_key_field = format_tlv("01", key)
    account_info = format_tlv("26", f"{gui}{pix_key_field}")
    mcc = format_tlv("52", "0000")
    currency = format_tlv("53", "986")

    amount_field = ""
    if amount is not None and amount > 0:
        amount_field = format_tlv("54", f"{amount:.2f}")

    country = format_tlv("58", "BR")
    merchant_name = format_tlv("59", sanitized_name)
    merchant_city = format_tlv("60", sanitized_city)

    txid_field = format_tlv("05", sanitized_txid)
    additional_data = format_tlv("62", txid_field)

    partial = (
        f"{pfi}{pim}{account_info}{mcc}{currency}{amount_field}"
        f"{country}{merchant_name}{merchant_city}{additional_data}6304"
    )

    crc = calculate_crc16(partial)
    return f"{partial}{crc}"


def generate_pix_qr_svg(payload: str, scale: int = 5, border: int = 2) -> str:
    """Gera o código SVG do QR Code a partir do payload Pix garantindo namespace."""
    qr = segno.make(payload, error="m")
    svg = qr.svg_inline(scale=scale, border=border)
    if "xmlns=" not in svg:
        svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    return svg


def generate_pix_qr_data_uri(
    payload: str,
    scale: int = 6,
    border: int = 2,
    dark: str = "#000000",
    light: str = "#ffffff",
) -> str:
    """Gera um Data URI em formato SVG pronto para uso em tags img do HTML/Dash."""
    qr = segno.make(payload, error="m")
    return qr.svg_data_uri(scale=scale, border=border, dark=dark, light=light)
