"""Testes de contrato, validação Pydantic e integridade de candidaturas.csv (Issue #7)."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from radar_eleitoral.candidaturas import (
    CARGOS,
    UF_NAMES,
    CandidaturaRecord,
    HeroData,
    get_hero_data,
    load_candidaturas,
)


def test_candidatura_record_valid() -> None:
    """Valida que um registro bem formatado passa na validação Pydantic."""
    record = CandidaturaRecord(
        uf="SP",
        cargo="Governador",
        url_g1="https://g1.globo.com/sp/sao-paulo/eleicoes/2026/noticia/2026/08/28/eleicoes-2026-veja-todos-os-candidatos-ao-governo-de-sao-paulo.ghtml",
        resumo="São 7 candidatos registrados na disputa pelo cargo.",
        candidaturas=7,
    )
    assert record.uf == "SP"
    assert record.cargo == "Governador"
    assert record.candidaturas == 7


def test_candidatura_record_invalid_uf() -> None:
    """Valida que UF inexistente ou inválida falha na validação."""
    with pytest.raises(ValidationError):
        CandidaturaRecord(
            uf="ZZ",
            cargo="Governador",
            url_g1="https://g1.globo.com/sp/noticia.ghtml",
            resumo="Resumo teste",
            candidaturas=5,
        )


def test_candidatura_record_invalid_cargo() -> None:
    """Valida que cargo não previsto no domínio falha na validação."""
    with pytest.raises(ValidationError):
        CandidaturaRecord(
            uf="SP",
            cargo="Prefeito",  # Fora do domínio das eleições gerais 2026
            url_g1="https://g1.globo.com/sp/noticia.ghtml",
            resumo="Resumo teste",
            candidaturas=5,
        )


def test_candidatura_record_insecure_or_external_url() -> None:
    """Garante que URLs externas ou sem HTTPS sejam rejeitadas para evitar links quebrados/phishing."""
    with pytest.raises(ValidationError):
        CandidaturaRecord(
            uf="SP",
            cargo="Governador",
            url_g1="https://portal-externo.com/noticia.html",
            resumo="Resumo teste",
            candidaturas=5,
        )

    with pytest.raises(ValidationError):
        CandidaturaRecord(
            uf="SP",
            cargo="Governador",
            url_g1="http://g1.globo.com/noticia.ghtml",  # Requer HTTPS
            resumo="Resumo teste",
            candidaturas=5,
        )


def test_candidatura_record_rejects_credentials_and_secrets() -> None:
    """Garante que URLs com credenciais, tokens ou chaves secretas sejam rejeitadas."""
    with pytest.raises(ValidationError):
        CandidaturaRecord(
            uf="SP",
            cargo="Governador",
            url_g1="https://user:password@g1.globo.com/noticia.ghtml",
            resumo="Resumo teste",
            candidaturas=5,
        )

    with pytest.raises(ValidationError):
        CandidaturaRecord(
            uf="SP",
            cargo="Governador",
            url_g1="https://g1.globo.com/noticia.ghtml?api_key=secret_123456",
            resumo="Resumo teste",
            candidaturas=5,
        )


def test_candidatura_record_invalid_candidaturas_count() -> None:
    """Garante que contagem de candidaturas seja número inteiro positivo."""
    with pytest.raises(ValidationError):
        CandidaturaRecord(
            uf="SP",
            cargo="Governador",
            url_g1="https://g1.globo.com/noticia.ghtml",
            resumo="Resumo teste",
            candidaturas=0,
        )


def test_candidatura_record_rejects_non_ghtml_path() -> None:
    """Garante que URLs sem caminho para matéria .ghtml sejam rejeitadas."""
    with pytest.raises(ValidationError):
        CandidaturaRecord(
            uf="SP",
            cargo="Governador",
            url_g1="https://g1.globo.com/",
            resumo="Resumo teste",
            candidaturas=5,
        )


def test_load_candidaturas_disk_dataset() -> None:
    """Valida a carga completa do arquivo data/candidaturas.csv em disco contra o schema Pydantic."""
    csv_path = Path("data/candidaturas.csv")
    assert csv_path.exists(), "Arquivo data/candidaturas.csv deve existir"

    store = load_candidaturas(csv_path)
    # Esperado: 1 Presidente + 27 Governadores + 27 Senadores + 27 Dep. Federais + 27 Dep. Estaduais/Distrital = 109
    assert len(store) == 109

    # Garante presença de todos os estados e DF
    for uf in UF_NAMES:
        assert (uf, "Governador") in store
        assert (uf, "Senador") in store
        assert (uf, "Deputado Federal") in store
        if uf == "DF":
            assert (uf, "Deputado Distrital") in store
        else:
            assert (uf, "Deputado Estadual") in store

    # Garante presença de Presidente (BR)
    assert ("BR", "Presidente") in store


def test_load_candidaturas_handles_missing_data(tmp_path: Path) -> None:
    """Garante tratamento resiliente de dados faltantes (imputação e descarte de linhas corrompidas)."""
    bad_csv = tmp_path / "candidaturas_bad.csv"
    bad_csv.write_text(
        "uf,cargo,url_g1,resumo,candidaturas\n"
        "SP,Governador,https://g1.globo.com/noticia.ghtml,Resumo teste,\n"  # falta candidaturas -> imputa 1
        "XX,Governador,https://g1.globo.com/noticia.ghtml,Resumo teste,5\n"  # UF inválida -> ignora
        "RJ,Governador,https://g1.globo.com/noticia.ghtml,,10\n",  # falta resumo -> preenche padrão
        encoding="utf-8",
    )
    store = load_candidaturas(bad_csv)
    assert len(store) == 2
    assert ("SP", "Governador") in store
    assert store[("SP", "Governador")].candidaturas == 1
    assert ("RJ", "Governador") in store


def test_get_hero_data_presidente() -> None:
    """Verifica contrato de dados do Hero Card para Presidente."""
    hero = get_hero_data("BR", "Presidente")
    assert isinstance(hero, HeroData)
    assert hero.is_nacional is True
    assert hero.uf == "BR"
    assert hero.cargo == "Presidente"
    assert "Presidência da República" in hero.titulo
    assert hero.candidaturas == 13
    assert hero.url_g1.startswith("https://g1.globo.com/")


@pytest.mark.parametrize("uf", ["SP", "RJ", "MG", "BA", "DF", "RS"])
def test_get_hero_data_governador(uf: str) -> None:
    """Verifica contrato de dados do Hero Card para Governador em estados chave."""
    hero = get_hero_data(uf, "Governador")
    assert isinstance(hero, HeroData)
    assert hero.is_nacional is False
    assert hero.uf == uf
    assert hero.cargo == "Governador"
    assert hero.uf_nome == UF_NAMES[uf]
    assert hero.candidaturas > 0
    assert hero.url_g1.startswith("https://g1.globo.com/")


def test_get_hero_data_df_deputado_distrital_mapping() -> None:
    """Valida que o seletor Deputado Estadual no DF mapeia transparentemente para Deputado Distrital."""
    hero = get_hero_data("DF", "Deputado Estadual")
    assert isinstance(hero, HeroData)
    assert hero.uf == "DF"
    assert hero.cargo == "Deputado Distrital"
    assert "Distrital" in hero.titulo or "Deputados Distritais" in hero.titulo
    assert hero.candidaturas == 423
    assert "distrito-federal" in hero.url_g1


def test_get_hero_data_fallback() -> None:
    """Garante fallback seguro e determinístico para pares não encontrados."""
    hero = get_hero_data("AC", "Deputado Inexistente")
    assert isinstance(hero, HeroData)
    assert hero.uf == "AC"
    assert hero.candidaturas >= 1
    assert hero.url_g1.startswith("https://g1.globo.com/")


def test_constants_contract() -> None:
    """Garante que as constantes de cargos e UFs atendem à interface esperada."""
    assert "Presidente" in CARGOS
    assert "Governador" in CARGOS
    assert "Senador" in CARGOS
    assert "Deputado Federal" in CARGOS
    assert "Deputado Estadual" in CARGOS
    assert len(CARGOS) == 5
    assert len(UF_NAMES) == 27
