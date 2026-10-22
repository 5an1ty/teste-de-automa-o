from dataclasses import dataclass, field, asdict

FIELDS = ("numero", "status", "horas", "minutos", "tipo", "solicitante", "operador_id", "operador_nome", "tecnico_id", "tecnico_nome")

@dataclass(frozen=True)
class Order:
    numero: str
    status: str
    horas: str
    minutos: str
    tipo: str
    solicitante: str
    operador_id: str
    operador_nome: str
    tecnico_id: str
    tecnico_nome: str
    legiveis: frozenset[str] = field(default_factory=lambda: frozenset(FIELDS))

@dataclass
class Result:
    numero: str
    resultado: str = "NAO_PROCESSADA"
    motivos: list[str] = field(default_factory=list)
    verificacoes: dict[str, bool] = field(default_factory=dict)
    impressao: str = "NAO_SOLICITADA"
    solicitada: bool = False
    enviada: bool = False
    confirmada: bool = False
    falha_tecnica: bool = False
    operador: str = ""
    status: str = ""
    horas: str = ""
    minutos: str = ""

    def to_dict(self):
        return asdict(self)
