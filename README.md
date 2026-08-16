# ============================================================
#  ██████╗ ██████╗     ██████╗ ███████╗███╗   ██╗
#  ██╔══██╗╚════██╗    ╚════██╗██╔════╝████╗  ██║
#  ██████╔╝ ███████║     █████╔╝█████╗  ██╔██╗ ██║
#  ██╔═══╝  ██╔══██║    ██╔═══╝ ██╔══╝  ██║╚██╗██║
#  ██║     ██████╔╝    ███████╗███████╗██║ ╚████║
#  ╚═╝     ╚═════╝     ╚══════╝╚══════╝╚═╝  ╚═══╝
#
#              PROCEDURAL FORGE X
#          ADVANCED 3D GENERATION SYSTEM
# ============================================================

**Procedural Forge X** é um sistema avançado e modular em Python para o **Blender**, projetado para a geração totalmente procedural de modelos 3D sci-fi complexos (reatores industriais, estruturas sci-fi e componentes mecânicos).

---

## 🌟 Principais Funcionalidades

- 🎲 **Geração Procedural Determinística por Semente (Seed)**: Todo o modelo é gerado através de um número de semente configurável. Uma mesma semente produz sempre o modelo exatamente idêntico.
- 🎨 **Shader Engine Procedural (Nodes)**: Criação automática de nós de textura de ruído (*ShaderNodeTexNoise*) e mapeamento de relevo (*ShaderNodeBump*) para micro-imperfeições realistas em superfícies metálicas.
- 💎 **Biblioteca Integrada de Materiais PBR**: Materiais PBR de metais (aço escuro, titânio, ouro, cobre), borracha, vidro e núcleos de energia emissivos (azul, ciano, roxo, vermelho).
- ⚙️ **Detalhamento Industrial Automático**: Painéis, parafusos em anel, módulos externos, antenas com luzes indicadoras e redes de cabos dinâmicos.
- 📐 **Suporte a LOD (Level of Detail)**: Gera automaticamente versões otimizadas dos modelos (LOD1, LOD2, LOD3) utilizando modificadores de decimação.
- 💡 **Estúdio Virtual Integrado**: Configuração automática de piso/cenário, câmera e iluminação de 3 pontos (Key, Fill, Rim) com temperatura de cor e contraste calibrados.
- 📊 **Exportação de Metadados JSON**: Salva relatórios detalhados com informações da geração, semente utilizada, contagem e lista de objetos gerados.
- 🔁 **Modo Batch (Geração em Lote)**: Capacidade de gerar dezenas ou centenas de modelos sequenciais e renderizá-los automaticamente.
- ⚡ **Compatibilidade Blender 3.x e 4.x+**: Código adaptado com *type hints* e verificações nativas para lidar com diferenças de API do Principled BSDF e sombreamento suave (*Smooth Shading*).

---

## 📁 Estrutura do Repositório

```text
.
├── procedural_forge.py    # Script principal do gerador procedural em Python/Blender
├── tests/                 # Suite de testes unitários e validações de sintaxe
│   └── test_generator.py  # Testes unitários com interface mock do Blender
├── procedural_output/     # Diretório padrão para exportação de renders, .blend e JSON (criado na execução)
├── .gitignore             # Arquivos ignorados pelo controle de versão
└── README.md              # Documentação oficial do projeto
```

---

## 🚀 Como Executar

### Pré-requisitos
- **Blender 3.0** ou superior instalado no sistema (compatível com Blender 4.x).

---

### Método 1: Via Interface Gráfica do Blender (GUI)

1. Abra o Blender.
2. Vá para o espaço de trabalho **Scripting** (aba *Scripting* no topo da tela).
3. Clique em **Open** e selecione o arquivo `procedural_forge.py`.
4. Clique em **Run Script** (ou pressione `Alt + P`).
5. O modelo procedural será gerado na cena 3D atual e exportado para a pasta `procedural_output/`.

---

### Método 2: Execução Headless via Linha de Comando (CLI)

Para gerar modelos e renderizar sem abrir a interface gráfica do Blender:

```bash
blender --background --python procedural_forge.py
```

---

## ⚙️ Configuração (`CONFIG`)

O comportamento da geração é controlado pelo dicionário `CONFIG` no início do arquivo `procedural_forge.py`:

```python
CONFIG = {
    "seed": 928371,                     # Semente aleatória para geração determinística
    "project_name": "PROCEDURAL_FORGE",
    "object_type": "SCIFI_REACTOR",      # Tipo do objeto a ser gerado
    "complexity": 5,                    # Nível de complexidade (1 a 10)
    "detail_density": 0.75,             # Densidade de pequenos detalhes industriais
    "generate_lights": True,            # Criar iluminação de estúdio
    "generate_camera": True,           # Criar e posicionar câmera
    "generate_floor": True,            # Criar piso de estúdio
    "render": True,                     # Executar renderização automática
    "save_blend": True,                 # Salvar arquivo .blend gerado
    "save_render": True,                # Salvar imagem renderizada (PNG)
    "resolution": 900,                  # Resolução do render (900x900 px)
    "batch_mode": False,                # Ativar geração em lote de múltiplos modelos
    "batch_count": 5,                   # Quantidade de modelos no modo batch
    "output_folder": "//procedural_output", # Diretório de saída
    "enable_lod": True,                 # Gerar níveis de detalhe (LOD1, LOD2, LOD3)
    "enable_metadata": True,            # Exportar arquivo metadata_seed.json
    "procedural_noise_materials": True, # Ativar nós de ruído/bump procedural nos materiais PBR
}
```

---

## 🧪 Executando os Testes

Para validar a sintaxe, nós de materiais e estrutura do script fora do ambiente do Blender (utilizando uma interface mock):

```bash
python3 -m unittest discover -s tests
```

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Sinta-se à vontade para utilizar, modificar e expandir para seus projetos 3D.
