"""Dados em memória para prototipação interativa do Radar Eleitoral."""

from dataclasses import dataclass
from typing import Final

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

CARGOS: Final[list[str]] = [
    "Presidente",
    "Governador",
    "Senador",
    "Deputado Federal",
    "Deputado Estadual",
]


@dataclass(frozen=True)
class HeroData:
    """Informações exibidas no Hero Card."""

    uf: str
    uf_nome: str
    cargo: str
    titulo: str
    resumo: str
    candidaturas: int
    url_g1: str
    is_nacional: bool = False


# Registros específicos para demonstração realista
MOCK_ENTRIES: Final[dict[tuple[str, str], HeroData]] = {
    ("BR", "Presidente"): HeroData(
        uf="BR",
        uf_nome="Brasil (Nacional)",
        cargo="Presidente",
        titulo="Eleições 2026: veja a lista de candidatos à Presidência da República",
        resumo=(
            "Matéria automatizada do G1 com a relação completa de concorrentes ao Planalto "
            "homologados pelo TSE, composições de chapa com vice e patrimônios declarados."
        ),
        candidaturas=12,
        url_g1="https://g1.globo.com/politica/eleicoes/2026/presidente",
        is_nacional=True,
    ),
    ("SP", "Governador"): HeroData(
        uf="SP",
        uf_nome="São Paulo",
        cargo="Governador",
        titulo="Eleições em SP: veja quem são os candidatos ao governo de São Paulo",
        resumo=(
            "Levantamento editorial com os postulantes ao Palácio dos Bandeirantes, coligações "
            "registradas no TRE-SP e diretrizes prioritárias dos planos de governo."
        ),
        candidaturas=10,
        url_g1="https://g1.globo.com/sp/sao-paulo/eleicoes/2026/governador",
    ),
    ("RJ", "Governador"): HeroData(
        uf="RJ",
        uf_nome="Rio de Janeiro",
        cargo="Governador",
        titulo="Eleições no RJ: confira a lista oficial de concorrentes ao governo do estado",
        resumo=(
            "Cobertura algorítmica do G1 Rio com candidaturas confirmadas no TRE-RJ, histórico "
            "de mandatos e prestação inicial de contas eleitorais."
        ),
        candidaturas=8,
        url_g1="https://g1.globo.com/rj/rio-de-janeiro/eleicoes/2026/governador",
    ),
    ("MG", "Governador"): HeroData(
        uf="MG",
        uf_nome="Minas Gerais",
        cargo="Governador",
        titulo="Eleições em MG: quem disputa o governo de Minas Gerais nas eleições gerais",
        resumo=(
            "Panorama automatizado com todos os candidatos ao governo mineiro no TRE-MG, "
            "declarados aptos pela Justiça Eleitoral."
        ),
        candidaturas=9,
        url_g1="https://g1.globo.com/mg/minas-gerais/eleicoes/2026/governador",
    ),
    ("BA", "Governador"): HeroData(
        uf="BA",
        uf_nome="Bahia",
        cargo="Governador",
        titulo="Eleições na Bahia: veja a lista atualizada de postulantes ao governo",
        resumo=(
            "Acompanhamento automatizado de candidaturas ao Palácio de Ondina registradas no "
            "TRE-BA, coligações partidárias e situação do registro."
        ),
        candidaturas=7,
        url_g1="https://g1.globo.com/ba/bahia/eleicoes/2026/governador",
    ),
    ("RS", "Governador"): HeroData(
        uf="RS",
        uf_nome="Rio Grande do Sul",
        cargo="Governador",
        titulo="Eleições no RS: quem são os candidatos ao governo gaúcho",
        resumo=(
            "Lista em tempo real gerada por inteligência editorial do G1 RS com candidaturas "
            "ao Palácio Piratini."
        ),
        candidaturas=8,
        url_g1="https://g1.globo.com/rs/rio-grande-do-sul/eleicoes/2026/governador",
    ),
}


def get_hero_data(uf: str, cargo: str) -> HeroData:
    """Retorna dados do Hero Card para o par (uf, cargo)."""
    if cargo == "Presidente":
        return MOCK_ENTRIES[("BR", "Presidente")]

    uf_clean = uf.upper()
    if uf_clean not in UF_NAMES:
        uf_clean = "SP"

    key = (uf_clean, cargo)
    if key in MOCK_ENTRIES:
        return MOCK_ENTRIES[key]

    # Gerador dinâmico de alta fidelidade para estados e cargos não pré-configurados
    uf_nome = UF_NAMES[uf_clean]
    candidatos_base = {
        "Governador": 6 + (hash(uf_clean) % 5),
        "Senador": 8 + (hash(uf_clean) % 6),
        "Deputado Federal": 180 + (hash(uf_clean) % 150),
        "Deputado Estadual": 320 + (hash(uf_clean) % 250),
    }.get(cargo, 10)

    slug_cargo = cargo.lower().replace(" ", "-")
    return HeroData(
        uf=uf_clean,
        uf_nome=uf_nome,
        cargo=cargo,
        titulo=f"Eleições em {uf_nome}: veja todos os candidatos a {cargo}",
        resumo=(
            f"Matéria automatizada gerada pelo pipeline editorial do G1 com a relação "
            f"completa de candidaturas a {cargo} homologadas pela Justiça Eleitoral em {uf_nome}."
        ),
        candidaturas=candidatos_base,
        url_g1=f"https://g1.globo.com/{uf_clean.lower()}/eleicoes/2026/{slug_cargo}",
        is_nacional=False,
    )
