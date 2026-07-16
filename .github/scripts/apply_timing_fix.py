from pathlib import Path
import re

path = Path("index.html")
source = path.read_text(encoding="utf-8")

NEW_STYLE = '''<style>
        :root { color-scheme: dark; }
        * { box-sizing: border-box; }

        html, body {
            margin: 0;
            width: 100%;
            height: 100%;
            min-height: 100%;
            overflow: hidden;
            overscroll-behavior: none;
            background: #000;
        }

        body {
            position: fixed;
            inset: 0;
            color: #fff;
            font-family: sans-serif;
            touch-action: none;
            user-select: none;
            -webkit-user-select: none;
        }

        canvas {
            position: absolute;
            inset: 0;
            display: block;
            width: 100vw;
            height: 100vh;
            height: 100dvh;
            border: 0;
            border-radius: 0;
            box-shadow: none;
            background: #000;
            touch-action: none;
        }

        .controles-touch {
            position: absolute;
            left: max(12px, env(safe-area-inset-left));
            right: max(12px, env(safe-area-inset-right));
            bottom: max(12px, env(safe-area-inset-bottom));
            display: none;
            justify-content: space-between;
            align-items: flex-end;
            z-index: 20;
            pointer-events: none;
        }

        .direcoes-touch {
            display: flex;
            gap: 8px;
            pointer-events: none;
        }

        .controle-btn,
        .btn-fullscreen {
            border: 1px solid rgba(255, 255, 255, 0.38);
            color: rgba(255, 255, 255, 0.9);
            background: rgba(8, 18, 25, 0.27);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.18);
            backdrop-filter: blur(3px);
            -webkit-backdrop-filter: blur(3px);
            font: inherit;
            font-weight: 700;
            cursor: pointer;
            touch-action: none;
            -webkit-tap-highlight-color: transparent;
            transition: opacity 120ms ease, background 120ms ease, transform 80ms ease;
        }

        .controle-btn {
            width: 58px;
            height: 58px;
            padding: 0;
            border-radius: 50%;
            font-size: 24px;
            line-height: 1;
            opacity: 0.58;
            pointer-events: auto;
        }

        .controle-btn.pular {
            width: 66px;
            height: 66px;
            font-size: 24px;
        }

        .controle-btn:active,
        .controle-btn.ativo {
            opacity: 0.95;
            background: rgba(67, 145, 190, 0.66);
            transform: scale(0.94);
        }

        .btn-fullscreen {
            position: absolute;
            top: max(9px, env(safe-area-inset-top));
            right: max(9px, env(safe-area-inset-right));
            width: 38px;
            height: 38px;
            padding: 0;
            border-radius: 10px;
            font-size: 19px;
            line-height: 1;
            opacity: 0.5;
            z-index: 30;
        }

        .btn-fullscreen:hover,
        .btn-fullscreen:focus-visible {
            opacity: 0.95;
        }

        @media (hover: none), (pointer: coarse) {
            .controles-touch { display: flex; }
        }

        @media (max-width: 430px) {
            .controle-btn { width: 54px; height: 54px; }
            .controle-btn.pular { width: 62px; height: 62px; }
        }
    </style>'''

source, count = re.subn(r"<style>.*?</style>", NEW_STYLE, source, count=1, flags=re.S)
assert count == 1, "CSS não encontrado"

NEW_UI = '''
    <button id="btnFullscreen" class="btn-fullscreen" type="button" aria-label="Alternar tela cheia" title="Tela cheia">⛶</button>

    <div class="controles-touch" aria-label="Controles do jogo">
        <div class="direcoes-touch">
            <button id="btnEsquerda" class="controle-btn" type="button" aria-label="Andar para a esquerda">◀</button>
            <button id="btnDireita" class="controle-btn" type="button" aria-label="Andar para a direita">▶</button>
        </div>
        <button id="btnPular" class="controle-btn pular" type="button" aria-label="Pular" title="Pular">▲</button>
    </div>
'''
source, count = re.subn(
    r'\s*<button id="btnFullscreen".*?<script>',
    NEW_UI + "\n    <script>",
    source,
    count=1,
    flags=re.S,
)
assert count == 1, "Interface de controles não encontrada"

source = source.replace(
    "        const ALTURA_MUNDO = 1080;\n",
    "        const ALTURA_MUNDO = 1080;\n"
    "        const PASSO_FIXO_MS = 1000 / 60;\n"
    "        const MAX_PASSOS_POR_QUADRO = 5;\n",
    1,
)
source = source.replace(
    "        let pixelRatio = 1;\n",
    "        let pixelRatio = 1;\n        let resizeRaf = null;\n",
    1,
)
assert "PASSO_FIXO_MS" in source and "resizeRaf" in source

VIEWPORT = '''        function limitarBacillusAoMundo(bac) {
            const margem = 20;
            const larguraBacillus = configBacillus.largura * escalaBacillus;
            const limiteDireito = larguraMundo - larguraBacillus - margem;

            if (limiteDireito <= margem) {
                bac.x = (larguraMundo - larguraBacillus) / 2;
                return;
            }

            if (bac.x <= margem) {
                bac.x = margem;
                bac.velocidadeX = Math.abs(bac.velocidadeX);
                bac.viradoParaEsquerda = false;
            } else if (bac.x >= limiteDireito) {
                bac.x = limiteDireito;
                bac.velocidadeX = -Math.abs(bac.velocidadeX);
                bac.viradoParaEsquerda = true;
            }
        }

        function atualizarViewport() {
            redimensionarCanvas();
            nivelDoChao = ALTURA_MUNDO - 60;
            const configAtual = configDoEstadoAtual();
            const larguraAtual = configAtual.largura * escala;
            const alturaAtual = configAtual.altura * escala;
            xPersonagem = Math.max(-50, Math.min(xPersonagem, larguraMundo - larguraAtual + 50));
            if (noChao) yPersonagem = nivelDoChao - alturaAtual;
            for (const bac of pgpbs) limitarBacillusAoMundo(bac);
        }

        function agendarAtualizacaoViewport() {
            if (resizeRaf !== null) cancelAnimationFrame(resizeRaf);
            resizeRaf = requestAnimationFrame(() => {
                resizeRaf = null;
                atualizarViewport();
            });
        }

        window.addEventListener('resize', agendarAtualizacaoViewport);
        window.addEventListener('orientationchange', () => {
            agendarAtualizacaoViewport();
            setTimeout(atualizarViewport, 180);
        });
        if (window.visualViewport) window.visualViewport.addEventListener('resize', agendarAtualizacaoViewport);
        atualizarViewport();'''
source, count = re.subn(
    r"        function atualizarViewport\(\) \{.*?        atualizarViewport\(\);",
    VIEWPORT,
    source,
    count=1,
    flags=re.S,
)
assert count == 1, "Bloco de viewport não encontrado"

INIT_BAC = '''        function inicializarBacillus() {
            pgpbs.push({
                x: 100,
                yBase: 180,
                yAtual: 180,
                velocidadeX: 2.5,
                viradoParaEsquerda: false,
                tempoParaProximaGota: 120
            });
            for (const bac of pgpbs) limitarBacillusAoMundo(bac);
        }'''
source, count = re.subn(
    r"        function inicializarBacillus\(\) \{.*?\n        \}",
    INIT_BAC,
    source,
    count=1,
    flags=re.S,
)
assert count == 1, "Inicialização do Bacillus não encontrada"

source = re.sub(r"\n\s*setInterval\(spawnPatogeno, 4000\);\s*", "\n", source, count=1)

FULLSCREEN = '''        function elementoFullscreenAtual() {
            return document.fullscreenElement || document.webkitFullscreenElement || null;
        }

        btnFullscreen.addEventListener('click', async () => {
            try {
                const elemento = document.documentElement;
                const solicitarFullscreen = elemento.requestFullscreen || elemento.webkitRequestFullscreen;
                const sairFullscreen = document.exitFullscreen || document.webkitExitFullscreen;

                if (!elementoFullscreenAtual() && solicitarFullscreen) {
                    await solicitarFullscreen.call(elemento);
                } else if (elementoFullscreenAtual() && sairFullscreen) {
                    await sairFullscreen.call(document);
                }
            } catch (erro) {
                console.debug('Tela cheia não disponível neste navegador.', erro);
            }
        });

        function tratarMudancaFullscreen() {
            btnFullscreen.textContent = elementoFullscreenAtual() ? '×' : '⛶';
            btnFullscreen.title = elementoFullscreenAtual() ? 'Sair da tela cheia' : 'Tela cheia';
            agendarAtualizacaoViewport();
            setTimeout(atualizarViewport, 120);
            setTimeout(atualizarViewport, 320);
        }

        document.addEventListener('fullscreenchange', tratarMudancaFullscreen);
        document.addEventListener('webkitfullscreenchange', tratarMudancaFullscreen);

        function atualizar() {'''
source, count = re.subn(
    r"        btnFullscreen\.addEventListener\('click'.*?        function atualizar\(\) \{",
    FULLSCREEN,
    source,
    count=1,
    flags=re.S,
)
assert count == 1, "Bloco de fullscreen não encontrado"

NEW_BAC_MOVE = '''            const agora = performance.now();
            for (const bac of pgpbs) {
                bac.x += bac.velocidadeX;
                limitarBacillusAoMundo(bac);
                bac.yAtual = bac.yBase + Math.sin(agora / 300) * 20;
                bac.tempoParaProximaGota--;
                if (bac.tempoParaProximaGota <= 0) {
                    const larguraRenderizadaBacillus = configBacillus.largura * escalaBacillus;
                    spawnGotaRoxaDoBacillus(
                        bac.x + larguraRenderizadaBacillus / 2,
                        bac.yAtual + configBacillus.altura * escalaBacillus * 0.8
                    );
                    bac.tempoParaProximaGota = 150 + Math.random() * 90;
                }
            }

            if (estado === 'parado')'''
source, count = re.subn(
    r"            for \(const bac of pgpbs\) \{\n                bac\.x \+= bac\.velocidadeX;.*?\n            \}\n\n            if \(estado === 'parado'\)",
    NEW_BAC_MOVE,
    source,
    count=1,
    flags=re.S,
)
assert count == 1, "Movimento do Bacillus não encontrado"

FIXED_LOOP = '''        let instanteAnterior = 0;
        let acumulador = 0;

        function loopDoJogo(instanteAtual) {
            if (!instanteAnterior) instanteAnterior = instanteAtual;
            const tempoDecorrido = Math.min(instanteAtual - instanteAnterior, 100);
            instanteAnterior = instanteAtual;
            acumulador += tempoDecorrido;

            let passosExecutados = 0;
            while (acumulador >= PASSO_FIXO_MS && passosExecutados < MAX_PASSOS_POR_QUADRO) {
                atualizar();
                acumulador -= PASSO_FIXO_MS;
                passosExecutados++;
            }

            if (passosExecutados === MAX_PASSOS_POR_QUADRO) acumulador = 0;
            desenhar();
            requestAnimationFrame(loopDoJogo);
        }

        document.addEventListener('visibilitychange', () => {
            instanteAnterior = 0;
            acumulador = 0;
        });'''
source, count = re.subn(
    r"        function loopDoJogo\(\) \{.*?\n        \}",
    FIXED_LOOP,
    source,
    count=1,
    flags=re.S,
)
assert count == 1, "Loop antigo não encontrado"

source = source.replace(
    "                inicializarBacillus();\n                loopDoJogo();",
    "                inicializarBacillus();\n                setInterval(spawnPatogeno, 4000);\n                requestAnimationFrame(loopDoJogo);",
    1,
)
assert "requestAnimationFrame(loopDoJogo);" in source

path.write_text(source, encoding="utf-8")
