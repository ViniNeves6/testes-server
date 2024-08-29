var plot; //variável global para descobrir o plot usado no closePopupResult
var currentRequestId = null; // Identificador único para cada coleta

function submitdata(data, url_dataview) {
    var requestId = Date.now(); // Cria um novo identificador único com a data/hora atual
    currentRequestId = requestId; // Atualiza o identificador global com o novo identificador

    $("#resultModal").modal('show');

    //criando um spinner geral
    showSpinnerModal();

    $.post(url_dataview, { dir: data }, function (result) {

        if (currentRequestId !== requestId) {
            return; // Ignora a resposta se não for a mais recente
        }

        plot = result.plot;
        if (result) {
            if (result.plot === "heatmap") {
                var images = JSON.parse(result.images);
                var df_trace = JSON.parse(result.trace);
                var df_voice = JSON.parse(result.voice);

                //removendo o spinner e aparecendo o gráfico
                removeSpinnerModal();
                document.getElementById("modal-heatmap").style.display = "block";

                // Call the graph_heatmap function and handle it asynchronously
                graph_heatmap(images, df_trace, df_voice)
                    .catch((error) => {
                        console.error("Error generating heatmap:", error);
                        $('#resultplot').html('Erro ao processar o heatmap');
                    });
            } else if (result.plot === "recording") {
                var images = JSON.parse(result.images);
                var icons = JSON.parse(result.icons);
                var df_trace = JSON.parse(result.trace);

                // aparece o plotly novamente após de ser ocultado
                document.getElementById("plotGroup").style.display = "block";
                document.getElementById("sitesHeading").style.display = "block";

                //removendo o spinner
                removeSpinnerModal();

                // Call the graph_heatmap function and handle it asynchronously
                graph_recording(images, icons, df_trace)
                    .then(result => {
                        botaoSites(result); // Passar o resultado para a função de criação de botões
                    })
                    .catch(error => {
                        console.error("Error processing recording:", error);
                        $('#resultplot').html('Erro ao processar o recording');
                    });

            } else {
                removeSpinnerModal();
                $('#resultplot').html('Invalid or not implemented plot');
            }

        } else {
            removeSpinnerModal();
            $('#resultplot').html('No results returned');
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        // Trata erros de solicitação AJAX para coleta atual
        if (currentRequestId === requestId) {
            removeSpinnerModal();
            console.error("Error submitting data:", errorThrown);
            $('#resultPlot').html('Erro ao processar os dados');
        }
    });
}

function closePopupResult() {
    // Atualiza o identificador único para cancelar a coleta atual
    currentRequestId = null;

    //verificando se o plot é recording ou heatmap para as devidas configurações de fechamento
    if (plot === "recording") {
        clearRecordingElements();
    } else if (plot === "heatmap") {
        document.getElementById("modal-heatmap").style.display = "none";
    }

    //verificando a existência de um modalBody para evitar duplicações
    removeSpinnerModal();

    //criando novamente o modal-body do spinner para fechamento
    showSpinnerModal();

    //limpando o plotly
    $('#resultPlot').html('');

    //definimos um atraso de 500 milissegundos antes de remover o modal-body do spinner
    setTimeout(function () {
        modalBody.remove();
    }, 500);
}

function showSpinnerModal() {
    var modalBody = createSpinnerModalBody();
    var modalContent = document.querySelector('#modalContent');
    modalContent.appendChild(modalBody);
}

function removeSpinnerModal() {
    var modalBody = document.getElementById("modalBody");
    if (modalBody) {
        modalBody.remove();
    }
}

function clearRecordingElements() {
    var nameSites = document.getElementById("dropdown-list");
    nameSites.innerHTML = '';

    document.getElementById("plotGroup").style.display = "none";
    document.getElementById("sitesContainer").style.display = "none";
    document.getElementById("sitesHeading").style.display = "none";
}

// Função para a lista de botões
function botaoSites(result) {
    var nameSites = document.getElementById("dropdown-list");

    // Verificação para expor automaticamente o hover do primeiro site
    var firstItem = true;

    for (const site of Object.keys(result)) {
        var link = document.createElement("a");
        link.setAttribute("class", "list-group-item border border-0 botoes-site");
        link.setAttribute("href", "#");
        link.textContent = site;
        nameSites.appendChild(link);

        // Atribui o evento de clique corretamente
        link.addEventListener("click", handleClick(site, result));

        if (firstItem) {
            link.click();
            firstItem = false;
        }
    }

    // Define a função de clique
    function handleClick(key, result) {
        return function (event) {
            event.preventDefault(); // Evitar o comportamento padrão do link
            // Remove a classe "clicked" de todos os botões
            var buttons = document.querySelectorAll('.list-group-item');
            buttons.forEach(function (button) {
                button.classList.remove("clicked");
            });
            // Adiciona a classe para alterar a cor de fundo quando o botão é clicado
            this.classList.add("clicked");

            // Atualiza o gráfico Plotly sem destruir o elemento
            var plotDiv = document.getElementById('resultPlot');
            var plotData = result[key].data;  // Supondo que `result[key]` contenha os dados e layout do gráfico
            var plotLayout = result[key].layout;

            Plotly.react(plotDiv, plotData, plotLayout)
                .catch((error) => {
                    console.error("Plotly error:", error);
                });
        };
    }
}

// cria o elemento modal-body do spinner
function createSpinnerModalBody() {
    var modalBody = document.createElement('div');
    modalBody.className = 'modal-body h-100 d-flex align-items-center justify-content-center gap-3';
    modalBody.id = 'modalBody';

    // Criação do elemento list-group
    var listGroup = document.createElement('div');
    listGroup.className = 'list-group';

    // Criação do elemento list-group-item
    var listGroupItem = document.createElement('div');
    listGroupItem.className = 'list-group-item';

    // Criação do elemento spinner
    var spinner = document.createElement('div');
    spinner.className = 'spinner-border text-secondary';
    spinner.id = 'spinner';
    spinner.setAttribute('role', 'status');

    var resultText = document.createElement('div');
    resultText.id = 'resultText';

    // Adicionando o spinner e o resultText ao list-group-item
    listGroupItem.appendChild(spinner);
    listGroupItem.appendChild(resultText);

    // Adicionando o list-group-item ao list-group
    listGroup.appendChild(listGroupItem);

    // Adicionando o list-group ao modal-body
    modalBody.appendChild(listGroup);

    // Retorna o modal-body para ser usado posteriormente
    return modalBody;
}

async function graph_recording(full_ims, type_icon, df_trace) {
    var dict_site = {}; // Objeto para armazenar os gráficos gerados para cada site

    // Cria uma lista de promessas para processar cada site
    const promises = Object.keys(full_ims).map(site => {
        return new Promise((resolve, reject) => {
            const img = new Image(); // Cria um novo objeto de imagem
            img.src = full_ims[site]; // Define a fonte da imagem

            // Define a função de callback que será executada quando a imagem for carregada
            img.onload = () => {
                const width = img.naturalWidth; // Obtém a largura natural da imagem
                const height = img.naturalHeight; // Obtém a altura natural da imagem

                // Filtra os dados de interação para o site atual
                const filtered_df = df_trace.filter(trace => trace.site === site);
                const traces = []; // Array para armazenar os traces do gráfico

                // Agrupa os dados de interação por tipo
                const groupedData = filtered_df.reduce((acc, trace) => {
                    if (!acc[trace.type]) {
                        acc[trace.type] = [];
                    }
                    acc[trace.type].push(trace);
                    return acc;
                }, {});

                // Cria traces para cada tipo de interação
                for (const type of Object.keys(groupedData)) {
                    const group = groupedData[type];
                    if (type_icon[type]) {
                        const x = group.map(item => item.x);
                        const y = group.map(item => type === 'eye' ? item.y + item.scroll : item.y); // Ajuste condicional de Y
                        const time = group.map(item => item.time);
                        let mode;
                        if (type === 'click' || type === 'freeze' || type === 'wheel') {
                            mode = 'markers';
                        }
                        else {
                            mode = 'lines+markers';
                        }
                        const text = time.map(t => {
                            const hours = String(Math.floor(t / 3600)).padStart(2, '0');
                            const minutes = String(Math.floor((t % 3600) / 60)).padStart(2, '0');
                            const seconds = String(t % 60).padStart(2, '0');
                            return `Time: ${hours}:${minutes}:${seconds}`;
                        });

                        traces.push({
                            x: x,
                            y: y,
                            mode: mode,
                            name: type,
                            text: text,
                            hovertemplate: `Interaction: '${type}<br>Site: ${site}<br>%{text}<br>X: %{x}<br>Y: %{y}</br>'`,
                            marker: {
                                symbol: type_icon[type],
                                size: (type !== 'click' && type !== 'freeze' && type !== 'wheel') ? 8 : 16,
                                angleref: 'previous'
                            }
                        });
                    }
                }

                // Configura o layout do gráfico
                const layout = {
                    xaxis: {
                        range: [0, width],
                        autorange: false,
                        showgrid: false, // Remover linhas de grade
                        zeroline: false, // Remover linha zero
                        visible: false
                    },
                    yaxis: {
                        range: [height, 0],
                        autorange: false,
                        showgrid: false, // Remover linhas de grade
                        zeroline: false, // Remover linha zero
                        visible: false,
                        scaleanchor: 'x',
                        scaleratio: 1
                    },
                    legend: {
                        orientation: 'h',
                        yanchor: 'bottom',
                        y: 1,
                        xanchor: 'left',
                        x: 0,
                        font: { color: 'white', size: 18 }
                    },
                    images: [{
                        source: img.src,
                        xref: 'x',
                        yref: 'y',
                        x: 0,
                        y: 0, // Colocando no topo do eixo Y
                        sizex: width,
                        sizey: height,
                        sizing: 'stretch',
                        opacity: 1,
                        layer: 'below'
                    }],
                    width: width,
                    height: height,
                    margin: { l: 0, r: 0, t: 0, b: 0 },
                    paper_bgcolor: 'rgba(0, 0, 0, 0)',
                    plot_bgcolor: 'rgba(0, 0, 0, 0)'
                };

                // Cria um elemento div e plota o gráfico
                const plotDiv = document.getElementById('resultPlot');
                Plotly.newPlot(plotDiv, traces, layout).then(() => {
                    const containerWidth = plotDiv.clientWidth;
                    Plotly.relayout(plotDiv, {
                        autosize: true,
                        height: height * 0.88, 
                        width: containerWidth * 0.88,
                        margin: { l: 0, r: 0, t: 0, b: 0 },
                        'yaxis.scaleanchor': 'x',
                        'yaxis.scaleratio': 1,
                        'yaxis.range': [height, 0] 
                    });
                    dict_site[site] = {
                        data: traces,
                        layout: layout
                    };
                    resolve(); // Agora, resolve é chamado após a plotagem completa
                }).catch((error) => {
                    console.error("Plotly error:", error);
                    reject(error); // Rejeita a promessa se houver um erro na plotagem
                });
            };

            img.onerror = reject; // Rejeita a promessa se houver um erro ao carregar a imagem
        });
    });

    // Espera que todas as promessas sejam resolvidas antes de retornar dict_site
    return Promise.all(promises).then(() => {
        return dict_site; // Retorna o objeto dict_site contendo os gráficos gerados
    });
}


function gaussianKernel(x, y, sigma) {
    const kernel = [];
    const size = Math.ceil(6 * sigma);
    const halfSize = Math.floor(size / 2);

    for (let i = -halfSize; i <= halfSize; i++) {
        kernel[i + halfSize] = [];
        for (let j = -halfSize; j <= halfSize; j++) {
            kernel[i + halfSize][j + halfSize] = Math.exp(-0.5 * (i ** 2 + j ** 2) / (sigma ** 2));
        }
    }

    const sum = kernel.flat().reduce((acc, val) => acc + val, 0);
    return kernel.map(row => row.map(val => val / sum));
}

function applyGaussianKernelToMatrix(matrix, kernel, x, y) {
    const size = kernel.length;
    const halfSize = Math.floor(size / 2);

    for (let i = -halfSize; i <= halfSize; i++) {
        for (let j = -halfSize; j <= halfSize; j++) {
            const xi = x + i;
            const yj = y + j;
            if (xi >= 0 && xi < matrix.length && yj >= 0 && yj < matrix[0].length) {
                matrix[xi][yj] += kernel[i + halfSize][j + halfSize];
            }
        }
    }
}

async function graph_heatmap(images, df_trace, df_voice, sigma = 60) {
    const firstImageKey = Object.keys(images)[0];
    const firstImageBase64 = images[firstImageKey];

    const img = new Image();
    img.src = firstImageBase64;

    await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
    });

    const width = img.width;
    const height = img.height;
    console.log(width, height);

    const frames = [];
    const colorscale = [
        [0, "rgba(255, 255, 255, 0)"],
        [0.15, "rgba(180, 180, 255, 0.45)"],
        [0.25, "rgba(160, 255, 160, 0.55)"],
        [0.45, "rgba(255, 255, 90, 0.65)"],
        [0.65, "rgba(255, 200, 100, 0.75)"],
        [0.85, "rgba(255, 90, 50, 0.85)"],
        [1, "rgba(255, 1, 0, 1)"]
    ];

    const maxTime = Math.max(...df_trace.map(row => row.time));
    for (let time = 0; time <= maxTime; time++) {
        const filtered_df = df_trace.filter(row => row.time == time);
        const uniqueImages = [...new Set(filtered_df.map(row => row.image))];

        for (const image of uniqueImages) {
            const plot_df = filtered_df.filter(row => row.image == image);

            const densityMatrix = new Array(width).fill().map(() => new Array(height).fill(0));
            const kernel = gaussianKernel(0, 0, sigma);

            for (const point of plot_df) {
                const x = Math.floor(parseFloat(point.x));
                const y = Math.floor(Math.abs(parseFloat(point.y) - parseFloat(point.scroll)));

                if (!isNaN(x) && !isNaN(y)) {
                    applyGaussianKernelToMatrix(densityMatrix, kernel, x, y);
                }
            }

            if (df_voice.some(row => row.time == time)) {
                const audio2text = df_voice.find(row => row.time == time).text;
                frames.push({
                    data: [{
                        z: densityMatrix,
                        type: 'heatmap',
                        colorscale: colorscale,
                        showscale: false,
                        hovertemplate: "Posição X: %{x}<br>Posição Y: %{y}"
                    }],
                    name: `${time}`,
                    layout: {
                        images: [{
                            source: images[image],
                            xref: "x",
                            yref: "y",
                            x: 0,
                            y: height,
                            sizex: width,
                            sizey: height,
                            sizing: "stretch",
                            opacity: 1,
                            layer: "below"
                        }],
                        annotations: [{
                            x: 0.5,
                            y: 0.04,
                            xref: "paper",
                            yref: "paper",
                            text: `Falado: ${audio2text}`,
                            font: {
                                family: "Courier New, monospace",
                                size: 18,
                                color: "#ffffff"
                            },
                            bordercolor: "#c7c7c7",
                            borderwidth: 2,
                            borderpad: 8,
                            bgcolor: "rgb(36, 36, 36)",
                            opacity: 1
                        }]
                    }
                });
            } else {
                frames.push({
                    data: [{
                        z: densityMatrix,
                        type: 'heatmap',
                        colorscale: colorscale,
                        showscale: false,
                        hovertemplate: "Posição X: %{x}<br>Posição Y: %{y}"
                    }],
                    name: `${time}`,
                    layout: {
                        images: [{
                            source: images[image],
                            xref: "x",
                            yref: "y",
                            x: 0,
                            y: height,
                            sizex: width,
                            sizey: height,
                            sizing: "stretch",
                            opacity: 1,
                            layer: "below"
                        }]
                    }
                });
            }
        }
    }

    const layout = {
        autosize: true,  // Permite que o gráfico se ajuste automaticamente ao contêiner
        margin: {  // Remover margens para permitir que a imagem se expanda completamente
            l: 0,
            r: 0,
            t: 40,
            b: 0,
            pad: 0
        },
        xaxis: {
            range: [0, width],
            autorange: false,
            showgrid: false,
            zeroline: false,
            visible: false,
        },
        yaxis: {
            range: [0, height],
            autorange: false,
            scaleanchor: "x",  // Mantém a proporção da imagem
            scaleratio: 1,
            showgrid: false,
            zeroline: false,
            visible: false,
        },
        images: [{
            source: firstImageBase64,
            xref: "x",
            yref: "y",
            x: 0,
            y: height,
            sizex: width,
            sizey: height,
            sizing: "contain",  // Ajuste para "contain" ou "stretch" conforme necessário
            opacity: 1,
            layer: "below"
        }],
        sliders: [{
            steps: frames.map(f => ({
                args: [[f.name], { frame: { duration: 500, redraw: true }, mode: "afterall" }],
                label: f.name,
                method: "animate"
            })),
            x: 0.12,  // Ajuste para a posição do slider na linha
            len: 0.88,  // Ajuste o comprimento do slider
            y: -0.03,  // Mesma altura dos botões
            pad: { t: 0, b: 10 },
            font: { size: 12 },
            ticklen: 4,
            currentvalue: { prefix: "Time(s):", visible: true, xanchor: "left", offset: 10 },
            xanchor: "left",
        }],

        updatemenus: [{
            buttons: [{
                args: [null, { frame: { duration: 800, redraw: true }, fromcurrent: true, transition: { duration: 300, easing: "quadratic-in-out" } }],
                label: "Play",
                method: "animate"
            }, {
                args: [[null], { frame: { duration: 0, redraw: true }, mode: "immediate", transition: { duration: 0 } }],
                label: "Pause",
                method: "animate"
            }],
            direction: "left",
            pad: { t: 0, b: 0, l: 20, r: 20 },
            showactive: false,
            type: "buttons",
            x: 0,
            xanchor: "left",
            y: -0.07,
            yanchor: "top",
            bgcolor: "rgba(190, 190, 190, 0.7)",
            font: { color: "rgb(0, 0, 0)" }
        }]
    };

    var graphDiv = document.getElementById('resultPlot');

    // Inicie a plotagem com os dados do primeiro frame
    const initialFrame = frames[0];
    Plotly.newPlot(graphDiv, initialFrame.data, layout, { showlink: false });
    Plotly.addFrames(graphDiv, frames); // Adiciona os frames de animação
}
