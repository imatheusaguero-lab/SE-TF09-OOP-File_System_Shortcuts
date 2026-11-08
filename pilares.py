# Os pilares na árvore de arquivos: herança, polimorfismo, abstração e interface.
# Rodar no terminal: python3 pilares.py
#
# O Item da Aula 08 tinha um booleano (eh_pasta) e vários "if eh_pasta".
# Aqui ele vira três classes: Item (o geral), Pasta e Arquivo (os específicos),
# e quem usa a árvore deixa de perguntar "você é pasta?".
from abc import ABC, abstractmethod


# INTERFACE: contrato puro, sem estado e sem implementação.
# Quem assina promete saber dizer o próprio tamanho em bytes.
class Medivel(ABC):
    __slots__ = ()

    @abstractmethod
    def tamanho(self):
        pass


# ABSTRAÇÃO + HERANÇA: o que toda pasta e todo arquivo têm em comum.
# Não dá para criar um Item "solto": ele é só o recorte do essencial.
class Item(Medivel):
    __slots__ = ("__nome", "__pai")

    def __init__(self, nome, pai=None):
        self.__validar_nome(nome)
        self.__nome = nome
        self.__pai = None

        if pai is not None:
            self.mover_para(pai)

    def __validar_nome(self, nome):
        if nome == "" or "/" in nome:
            raise ValueError("nome inválido: " + repr(nome))

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, novo_nome):
        self.__validar_nome(novo_nome)
        self.__nome = novo_nome

    @property
    def pai(self):
        return self.__pai

    def mover_para(self, destino):
        if destino is self.__pai:
            return

        destino._receber(self)          # cada tipo decide se aceita
        if self.__pai is not None:
            self.__pai._soltar(self)
        self.__pai = destino

    # PROTEGIDO: o gancho que as filhas sobrescrevem. Por padrão, recusa.
    def _receber(self, item):
        raise ValueError(self.__nome + " é um arquivo, não pode conter itens")

    def caminho(self):
        if self.__pai is None:
            return self.__nome
        return self.__pai.caminho() + "/" + self.__nome

    def profundidade(self):
        if self.__pai is None:
            return 0
        return self.__pai.profundidade() + 1

    @abstractmethod
    def mostrar(self):
        pass


class Arquivo(Item):
    __slots__ = ("__bytes",)

    def __init__(self, nome, tamanho_bytes, pai=None):
        if tamanho_bytes < 0:
            raise ValueError("tamanho não pode ser negativo")
        self.__bytes = tamanho_bytes
        super().__init__(nome, pai)

    def tamanho(self):
        return self.__bytes

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + " (" + str(self.tamanho()) + " B)")


class Pasta(Item):
    __slots__ = ("__filhos",)

    def __init__(self, nome, pai=None):
        self.__filhos = []
        super().__init__(nome, pai)

    @property
    def filhos(self):
        return tuple(self.__filhos)

    # OVERRIDE do gancho protegido: a pasta aceita, desde que não crie um ciclo.
    def _receber(self, item):
        ancestral = self
        while ancestral is not None:
            if ancestral is item:
                raise ValueError("não dá para mover " + item.nome + " para dentro dela mesma")
            ancestral = ancestral.pai
        self.__filhos.append(item)

    def _soltar(self, item):
        self.__filhos.remove(item)

    # POLIMORFISMO: a pasta soma o que tem dentro; nenhum filho é perguntado
    # se é pasta ou arquivo, cada um responde do seu jeito.
    def tamanho(self):
        total = 0
        for filho in self.__filhos:
            total = total + filho.tamanho()
        return total

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + "/ (" + str(self.tamanho()) + " B)")
        for filho in self.__filhos:
            filho.mostrar()


class Atalho(Item):
    # O Atalho herda os atributos e metodos da classe Item.
    # O unico atributo novo sera o destino.
    __slots__ = ("__destino",)

    def __init__(self, nome, destino, pai=None):
        # Inicializa nome e pai utilizando o construtor de Item.
        super().__init__(nome, pai)

        # Utiliza o metodo de validacao para definir o destino.
        self.redirecionar(destino)

    @property
    def destino(self):
        # Permite consultar o destino, mas nao altera-lo diretamente.
        return self.__destino

    def redirecionar(self, novo_destino):
        # Impede que um atalho aponte para si mesmo.
        if novo_destino is self:
            raise ValueError("O atalho nao pode apontar para si mesmo.")

        # Percorre os pais do atalho para evitar destinos ancestrais.
        # Exemplo: Desktop -> mathe -> Users -> C: -> None
        ancestral = self.pai

        while ancestral is not None:
            if novo_destino is ancestral:
                raise ValueError(
                    "O atalho nao pode apontar para uma pasta ancestral."
                )

            ancestral = ancestral.pai

        # Atualiza o destino somente apos passar pelas validacoes.
        self.__destino = novo_destino

    def tamanho(self):
        # O tamanho do atalho e sempre 1 byte.
        # Exemplo: arquivo com 5000 B -> atalho com 1 B.
        return 1

    def mostrar(self):
        # Calcula o recuo conforme a profundidade na arvore.
        # Exemplo: profundidade 2 -> 8 espacos.
        recuo = "    " * self.profundidade()

        # Exemplo: Notas.lnk -> C:/Users/mathe/notas.txt
        print(f"{recuo}{self.nome} -> {self.destino.caminho()}")

# Outra classe que assina o contrato SEM ser da árvore: a Lixeira.
class Lixeira(Medivel):
    __slots__ = ("__descartados",)

    def __init__(self):
        self.__descartados = []

    def descartar(self, arquivo):
        self.__descartados.append(arquivo)

    def tamanho(self):
        total = 0
        for arquivo in self.__descartados:
            total = total + arquivo.tamanho()
        return total


# Quem usa o contrato não sabe (nem quer saber) quem está do outro lado.
def espaco_total(coisas):
    total = 0
    for coisa in coisas:
        total = total + coisa.tamanho()
    return total


def tentar(rotulo, acao):
    try:
        acao()
        print(rotulo, "-> passou (!)")
    except Exception as erro:
        print(rotulo, "->", type(erro).__name__ + ":", erro)


# Executa os testes somente quando o arquivo for iniciado diretamente.
if __name__ == "__main__":

    # 1. Cria a estrutura de diretorios.
    # C:/Users/mathe/Desktop
    # C:/Users/mathe/Documentos
    disco = Pasta("C:")
    usuarios = Pasta("Users", disco)
    usuario = Pasta("mathe", usuarios)
    desktop = Pasta("Desktop", usuario)
    documentos = Pasta("Documentos", usuario)

    # 2. Cria dois arquivos com tamanhos diferentes.
    arquivo_codigo = Arquivo("projeto.py", 300, desktop)
    arquivo_notas = Arquivo("notas.txt", 120, documentos)

    # 3. Cria um atalho para um arquivo e outro para uma pasta.
    atalho_notas = Atalho("Notas.lnk", arquivo_notas, desktop)
    atalho_documentos = Atalho(
        "Documentos.lnk", documentos, desktop
    )

    # 4. Cria a lixeira e adiciona um arquivo descartado.
    lixeira = Lixeira()
    lixeira.descartar(Arquivo("antigo.txt", 40))

    # 5. Mostra todos os itens da arvore de arquivos.
    print("\n========== ARVORE DE ARQUIVOS ==========")
    disco.mostrar()

    # 6. Calcula o espaco ocupado por diferentes objetos.
    # 120 + (300 + 1 + 1) + 40 = 462 bytes
    print("\n========== ESPACO TOTAL ==========")
    total = espaco_total([arquivo_notas, desktop, lixeira])
    print(f"Espaco total: {total} B")

    # 7. Testa o encapsulamento da propriedade destino.
    # setattr tenta alterar uma propriedade sem setter.
    # Resultado esperado: AttributeError.
    print("\n========== TESTES DE VALIDACAO ==========")

    tentar(
        "Alterar destino diretamente",
        lambda: setattr(atalho_notas, "destino", arquivo_codigo)
    )

    # 8. Testa se um atalho pode apontar para si mesmo.
    # Resultado esperado: ValueError.
    tentar(
        "Atalho apontando para si mesmo",
        lambda: atalho_notas.redirecionar(atalho_notas)
    )

    # 9. Testa se um atalho pode apontar para sua pasta ancestral.
    # Resultado esperado: ValueError.
    tentar(
        "Atalho apontando para Desktop",
        lambda: atalho_notas.redirecionar(desktop)
    )
