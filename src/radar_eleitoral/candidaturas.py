"""Módulo de domínio para ingestão, validação Pydantic e fornecimento de candidaturas."""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel, Field, ValidationError, field_validator

# Relação canônica de UFs e nomes oficiais
UF_NAMES: Final[dict[str, str]] = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# Cargos exibidos no seletor da interface do usuário
CARGOS: Final[list[str]] = [
    "Presidente",
    "Governador",
    "Senador",
    "Deputado Federal",
    "Deputado Estadual",
]

# Conjunto completo de cargos válidos no domínio eleitoral 2026
VALID_CARGOS: Final[set[str]] = {
    "Presidente",
    "Governador",
    "Senador",
    "Deputado Federal",
    "Deputado Estadual",
    "Deputado Distrital",
}

VALID_UFS: Final[set[str]] = set(UF_NAMES.keys()) | {"BR"}


class CandidaturaRecord(BaseModel):
    """Modelo Pydantic para validação do contrato tabular de candidaturas.csv."""

    uf: str
    cargo: str
    url_g1: str
    resumo: str = Field(min_length=1)
    candidaturas: int = Field(ge=1)

    @field_validator("uf")
    @classmethod
    def validate_uf(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if v_upper not in VALID_UFS:
            raise ValueError(f"UF inválida: '{v}'. Deve ser uma das 27 UFs ou 'BR'.")
        return v_upper

    @field_validator("cargo")
    @classmethod
    def validate_cargo(cls, v: str) -> str:
        v_clean = v.strip()
        if v_clean not in VALID_CARGOS:
            raise ValueError(f"Cargo inválido: '{v}'. Deve ser um de {sorted(VALID_CARGOS)}.")
        return v_clean

    @field_validator("url_g1")
    @classmethod
    def validate_url_g1(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean.startswith("https://g1.globo.com/"):
            raise ValueError(
                f"URL deve ser segura (HTTPS) e canônica do G1 (https://g1.globo.com/...). Valor: '{v}'"
            )

        parsed = urlparse(v_clean)
        # Rejeita credenciais embutidas na URL (ex: user:pass@g1.globo.com)
        if parsed.username or parsed.password:
            raise ValueError("URL não pode conter credenciais de autenticação.")

        # Rejeita URLs sem caminho de notícia canônica
        clean_path = parsed.path.rstrip("/")
        if not clean_path or not clean_path.endswith(".ghtml"):
            raise ValueError("URL do G1 deve apontar para uma matéria canônica (.ghtml).")

        # Rejeita parâmetros de segredos industriais ou tokens em query string
        query_lower = parsed.query.lower()
        forbidden_terms = ("api_key", "secret", "token", "password", "auth")
        for term in forbidden_terms:
            if term in query_lower:
                raise ValueError(f"Exposição acidental de chave ou segredo na URL ({term}).")

        return v_clean


@dataclass(frozen=True)
class HeroData:
    """Informações exibidas no Hero Card da interface."""

    uf: str
    uf_nome: str
    cargo: str
    titulo: str
    resumo: str
    candidaturas: int
    url_g1: str
    is_nacional: bool = False


def _build_hero_title(cargo: str, uf_nome: str) -> str:
    """Gera o título editorial apropriado para o par (uf, cargo)."""
    titles: dict[str, str] = {
        "Presidente": "Presidência da República",
        "Governador": f"Governo de {uf_nome}",
        "Senador": f"Senado Federal em {uf_nome}",
        "Deputado Distrital": "Deputados Distritais no Distrito Federal",
        "Deputado Federal": f"Deputados Federais em {uf_nome}",
        "Deputado Estadual": f"Deputados Estaduais em {uf_nome}",
    }
    return titles.get(cargo, f"{cargo} - {uf_nome}")


def create_hero_data(
    uf: str,
    cargo: str,
    url_g1: str,
    resumo: str,
    candidaturas: int = 1,
) -> HeroData:
    """Função utilitária canônica para construir uma instância de HeroData."""
    is_nacional = uf == "BR" or cargo == "Presidente"
    uf_nome = "Brasil" if is_nacional else UF_NAMES.get(uf, uf)
    titulo = _build_hero_title(cargo, uf_nome)

    return HeroData(
        uf=uf,
        uf_nome=uf_nome,
        cargo=cargo,
        titulo=titulo,
        resumo=resumo,
        candidaturas=max(1, candidaturas),
        url_g1=url_g1,
        is_nacional=is_nacional,
    )


def load_candidaturas(csv_path: Path | str | None = None) -> dict[tuple[str, str], HeroData]:
    """Lê, valida via Pydantic e indexa o arquivo data/candidaturas.csv em memória."""
    if csv_path is None:
        # Resolve data/candidaturas.csv relativo à raiz do repositório
        csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "candidaturas.csv"
    else:
        csv_path = Path(csv_path)

    if not csv_path.exists():
        logger.warning(f"Arquivo de candidaturas não encontrado em '{csv_path}'. Usando fallback.")
        return {}

    store: dict[tuple[str, str], HeroData] = {}
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            try:
                # Tratamento resiliente de dados faltantes
                raw_uf = (row.get("uf") or "").strip().upper()
                raw_cargo = (row.get("cargo") or "").strip()
                raw_url = (row.get("url_g1") or "").strip()
                raw_resumo = (
                    row.get("resumo") or ""
                ).strip() or f"Cobertura de {raw_cargo} em {raw_uf}."

                raw_cand_str = (row.get("candidaturas") or "").strip()
                try:
                    raw_cand = int(raw_cand_str) if raw_cand_str else 1
                except ValueError:
                    logger.warning(f"Linha {idx}: contagem inválida '{raw_cand_str}'. Imputando 1.")
                    raw_cand = 1

                record = CandidaturaRecord(
                    uf=raw_uf,
                    cargo=raw_cargo,
                    url_g1=raw_url,
                    resumo=raw_resumo,
                    candidaturas=max(1, raw_cand),
                )

                hero = create_hero_data(
                    uf=record.uf,
                    cargo=record.cargo,
                    url_g1=record.url_g1,
                    resumo=record.resumo,
                    candidaturas=record.candidaturas,
                )
                store[(record.uf, record.cargo)] = hero

            except (ValidationError, ValueError, KeyError) as err:
                logger.warning(f"Linha {idx}: registro inválido ignorado. Erro: {err}")
                continue

    logger.info(f"Carregadas e validadas {len(store)} candidaturas de '{csv_path}'.")
    return store


# Repositório de candidaturas carregado no ciclo de vida do módulo
CANDIDATURAS_STORE: Final[dict[tuple[str, str], HeroData]] = load_candidaturas()


def get_hero_data(uf: str, cargo: str) -> HeroData:
    """Retorna os dados do Hero Card para o par (uf, cargo), com mapeamento DF e fallback."""
    # Presidente é de abrangência nacional exclusiva
    if cargo == "Presidente":
        uf = "BR"

    # Mapeamento de domínio: no DF o cargo proporcional estadual é Deputado Distrital
    if uf == "DF" and cargo == "Deputado Estadual":
        cargo = "Deputado Distrital"

    # Busca no repositório persistido e validado
    hero = CANDIDATURAS_STORE.get((uf, cargo))
    if hero is not None:
        return hero

    # Fallback defensivo e gracioso se par não estiver no repositório
    default_url = (
        "https://g1.globo.com/politica/eleicoes/2026/noticia/2026/08/28/"
        "eleicoes-2026-veja-todos-os-candidatos-a-presidencia-da-republica.ghtml"
    )
    uf_nome = "Brasil" if uf == "BR" else UF_NAMES.get(uf, uf)

    return create_hero_data(
        uf=uf,
        cargo=cargo,
        url_g1=default_url,
        resumo=f"Cobertura oficial e relação de concorrentes a {cargo} em {uf_nome}.",
        candidaturas=1,
    )
