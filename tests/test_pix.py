"""Testes unitários para o gerador de payload Pix e QR Code (EMVCo BR Code)."""

from radar_eleitoral.config import Settings
from radar_eleitoral.pix import (
    calculate_crc16,
    format_tlv,
    generate_pix_payload,
    generate_pix_qr_data_uri,
    generate_pix_qr_svg,
    sanitize_text,
)


def test_format_tlv():
    """Verifica formatação Tag-Length-Value com padding de 2 dígitos."""
    assert format_tlv("00", "01") == "000201"
    assert format_tlv("58", "BR") == "5802BR"
    assert format_tlv("59", "Rodrigo") == "5907Rodrigo"


def test_sanitize_text():
    """Verifica remoção de acentos e truncamento de tamanho para padrão EMVCo."""
    sanitized = sanitize_text("Rodrigo Guimarães Araújo", max_length=25)
    assert sanitized == "Rodrigo Guimaraes Araujo"
    assert len(sanitized) <= 25

    city = sanitize_text("Brasília", max_length=15)
    assert city == "Brasilia"
    assert len(city) <= 15


def test_calculate_crc16():
    """Verifica cálculo do CRC16-CCITT com polinômio 0x1021 e init 0xFFFF."""
    payload_sem_crc = (
        "00020126360014br.gov.bcb.pix0114ratopythonista@noh.pix"
        "5204000053039865802BR5923Rodrigo Guimaraes Araujo"
        "6008Brasilia62070503***6304"
    )
    crc = calculate_crc16(payload_sem_crc)
    assert len(crc) == 4
    assert crc.isupper()
    int(crc, 16)


def test_generate_pix_payload():
    """Valida montagem completa do BR Code conforme padrão do Banco Central."""
    payload = generate_pix_payload(
        key="ratopythonista@noh.pix",
        name="Rodrigo Guimarães Araújo",
        city="Brasília",
        txid="***",
    )

    assert payload.startswith("000201010211")
    assert "br.gov.bcb.pix" in payload
    assert "ratopythonista@noh.pix" in payload
    assert "Rodrigo Guimaraes Araujo" in payload
    assert "Brasilia" in payload
    assert "6304" in payload
    crc_pos = payload.rfind("6304")
    crc_code = payload[crc_pos + 4 :]
    assert len(crc_code) == 4
    assert calculate_crc16(payload[: crc_pos + 4]) == crc_code


def test_generate_pix_qr_svg():
    """Valida renderização do QR Code em formato SVG sem falhas."""
    payload = (
        "00020126360014br.gov.bcb.pix0114ratopythonista@noh.pix"
        "5204000053039865802BR5923Rodrigo Guimaraes Araujo"
        "6008Brasilia62070503***6304ABCD"
    )
    svg = generate_pix_qr_svg(payload)

    assert isinstance(svg, str)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "xmlns" in svg


def test_generate_pix_qr_data_uri():
    """Valida geração do Data URI do QR Code em SVG."""
    payload = "00020126360014br.gov.bcb.pix0114ratopythonista@noh.pix6304ABCD"
    data_uri = generate_pix_qr_data_uri(payload)

    assert isinstance(data_uri, str)
    assert data_uri.startswith("data:image/svg+xml")


def test_settings_pix_defaults():
    """Garante que a classe Settings possui os defaults aprovados na árvore de decisão."""
    settings = Settings()
    assert settings.pix_key == "ratopythonista@noh.pix"
    assert settings.pix_receiver_name == "Rodrigo Guimarães Araújo"
    assert settings.pix_city == "Brasília"
    assert settings.github_url == "https://github.com/ratopythonista"
    assert settings.linkedin_url == "https://www.linkedin.com/in/ratopythonista/"
    assert settings.instagram_url == "https://www.instagram.com/ratopythonista/"
    assert settings.x_url == "https://x.com/ratopythonista"
