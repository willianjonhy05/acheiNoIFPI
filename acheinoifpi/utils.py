import re
import string
import random
from django.core.paginator import Paginator


def limpar_cpf(cpf):
    return re.sub(r"\D", "", cpf or "")


def limpar_telefone(telefone):
    return re.sub(r"\D", "", telefone or "")


def gerar_codigo_aleatorio(length=6):
    """
    Gera um código aleatório com letras maiúsculas e números.
    Exemplo: 'A4B9C1'
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def buscar_objeto_ativo_por_id(modelo, id_objeto):
    if not id_objeto:
        return None

    try:
        return modelo.objects.filter(id=int(id_objeto), ativa=True).first()
    except (TypeError, ValueError):
        return None
    
    
def paginar_queryset(request, queryset, por_pagina=10):
    """
    Função reutilizável para paginação.
    Exibe 10 registros por página por padrão.
    """
    paginator = Paginator(queryset, por_pagina)
    numero_pagina = request.GET.get("page")
    page_obj = paginator.get_page(numero_pagina)
    return page_obj