import json
import sys
from pathlib import Path
import difflib

# Garante suporte a caracteres especiais e emojis no Windows
if sys.platform == "win32":
    try:
        if sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def carregar_magias():
    """Carrega as magias a partir do arquivo JSON no diretório do projeto."""
    diretorio_base = Path(__file__).resolve().parent
    
    # Arquivos possíveis (5.2 ou 5.3)
    arquivos_candidatos = [
        diretorio_base / "srd-5.2-spells.json",
        diretorio_base / "srd-5.3-spells.json",
        diretorio_base / "magias.json"
    ]
    
    for caminho in arquivos_candidatos:
        if caminho.exists() and caminho.stat().st_size > 0:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
                
    # Caso tenha outro nome com 'spell' no diretório
    for arquivo in diretorio_base.glob("*.json"):
        if arquivo.stat().st_size > 0:
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list) and len(dados) > 0 and "name" in dados[0]:
                    return dados

    raise FileNotFoundError("Não foi possível encontrar o arquivo de magias JSON.")

def formatar_magia(magia: dict) -> str:
    """Retorna os dados da magia formatados para exibição no terminal."""
    linhas = []
    linhas.append("=" * 65)
    linhas.append(f"🔮 Nome: {magia.get('name', 'Sem nome')}")
    
    # Nível e Escola
    nivel = magia.get("level", 0)
    nivel_str = "Truque (Nível 0)" if nivel == 0 else f"Nível {nivel}"
    escola = magia.get("school", "").capitalize()
    linhas.append(f"📖 Nível & Escola: {nivel_str} - {escola}")
    
    # Classes
    classes = magia.get("classes", [])
    if classes:
        linhas.append(f"🧙 Classes: {', '.join(classes)}")
        
    # Tempo de Conjuração / Ação
    tempo = magia.get("castingTime") or magia.get("actionType", "")
    trigger = magia.get("castingTrigger")
    if trigger:
        linhas.append(f"⏱️ Tempo de Conjuração: {tempo} ({trigger})")
    elif tempo:
        linhas.append(f"⏱️ Tempo de Conjuração: {tempo}")
        
    # Alcance
    alcance = magia.get("range", "")
    if alcance:
        linhas.append(f"🎯 Alcance: {alcance}")
        
    # Componentes
    componentes = [c.upper() for c in magia.get("components", [])]
    comp_str = ", ".join(componentes)
    material = magia.get("material")
    if material:
        comp_str += f" ({material})"
    if comp_str:
        linhas.append(f"✨ Componentes: {comp_str}")
        
    # Duração / Concentração / Ritual
    duracao = magia.get("duration", "")
    conc = "Sim" if magia.get("concentration") else "Não"
    ritual = "Sim" if magia.get("ritual") else "Não"
    linhas.append(f"⏳ Duração: {duracao} | Concentração: {conc} | Ritual: {ritual}")
    
    linhas.append("-" * 65)
    
    # Descrição
    desc = magia.get("description", "")
    linhas.append(f"📜 Descrição:\n{desc}")
    
    # Upgrade / Nível superior
    if magia.get("higherLevelSlot"):
        linhas.append("\n📈 Em Níveis Superiores:")
        linhas.append(magia["higherLevelSlot"])
    elif magia.get("cantripUpgrade"):
        linhas.append("\n📈 Evolução do Truque:")
        linhas.append(magia["cantripUpgrade"])
        
    linhas.append("=" * 65)
    return "\n".join(linhas)

def buscar_magia(nome_busca: str, magias: list):
    """Busca uma magia por nome (exato ou parcial)."""
    termo = nome_busca.strip().lower()
    if not termo:
        return None, []
        
    # 1. Busca exata (ignorando maiúsculas/minúsculas)
    for m in magias:
        if m.get("name", "").strip().lower() == termo:
            return m, []
            
    # 2. Busca parcial (termo contido no nome)
    parciais = [m for m in magias if termo in m.get("name", "").lower()]
    if len(parciais) == 1:
        return parciais[0], []
    elif len(parciais) > 1:
        return None, parciais
        
    # 3. Busca por aproximação (sugestões de digitação)
    nomes_magias = [m.get("name", "") for m in magias]
    sugestoes = difflib.get_close_matches(nome_busca, nomes_magias, n=3, cutoff=0.6)
    sugestoes_magias = [m for m in magias if m.get("name") in sugestoes]
    return None, sugestoes_magias

def main():
    try:
        magias = carregar_magias()
    except Exception as e:
        print(f"Erro ao carregar magias: {e}")
        return

    print("=" * 65)
    print(f"✨ Grimório 5.5 - {len(magias)} magias carregadas do SRD com sucesso!")
    print("=" * 65)
    print("Dica: Digite o nome da magia em inglês (ex: 'Acid Arrow', 'Fireball', 'Wish').")
    print("Digite 'sair' a qualquer momento para encerrar.\n")

    while True:
        try:
            entrada = input("🔍 Digite o nome da magia: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando o Grimório. Até a próxima!")
            break

        if not entrada:
            continue

        if entrada.lower() in ("sair", "exit", "quit"):
            print("Encerrando o Grimório. Até a próxima!")
            break

        magia_encontrada, alternativas = buscar_magia(entrada, magias)

        if magia_encontrada:
            print()
            print(formatar_magia(magia_encontrada))
            print()
        elif alternativas:
            print(f"\nNenhuma magia encontrada com o nome exato '{entrada}'.")
            print("Magias semelhantes encontradas:")
            for idx, alt in enumerate(alternativas, 1):
                print(f"  [{idx}] {alt.get('name')} (Nível {alt.get('level')})")
            
            escolha = input("\nDigite o número correspondente (ou Enter para nova busca): ").strip()
            if escolha.isdigit():
                num = int(escolha)
                if 1 <= num <= len(alternativas):
                    print()
                    print(formatar_magia(alternativas[num - 1]))
                    print()
                else:
                    print("Número inválido.")
            else:
                print()
        else:
            print(f"\n❌ Nenhuma magia encontrada com '{entrada}'. Tente outro nome!\n")

if __name__ == "__main__":
    main()