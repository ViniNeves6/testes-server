//import {graph_sentiment} from './graph_Bertimbau.js';
var valueData;
var url_aud;
function submitdata(data, url_data, url_audio) {
    valueData = data;
    url_aud = url_audio;
    document.getElementById("mybutton").style.display = "none";
    $("#resultModal").modal('show');
    $.post(url_data,
    {
        dir: data
    },
    function(results){

        document.getElementById("spinner").style.display = "none";
        document.getElementById("mybutton").style.display = "inline-block";
        
        var result3 = results.result3;

        if (result3 == false){
            document.getElementById("mybutton").style.display = "none";
            $('#resultplot').html(results.result1);
        }else{
            var result1 = JSON.parse(results.result1); //radar
            var result2 = JSON.parse(results.result2); //sentiment
            $('#resultplot').html(graph_sentiment(result1, result2));
        }
    });
};
function closePopupResult() {
    document.getElementById("spinner").style.display = "inline-flex";
    document.getElementById("mybutton").style.display = "none";
    $('#resultplot').html('')
};
function clickbutton(){
    $.post(url_aud,
    {
        data: valueData
    },
    function(result){
        let csvAudio = result;
        let blob = new Blob([csvAudio], {type: 'text/csv'});

        const link= window.document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = valueData + '/voice.csv';
        link.click()
        window.URL.revokeObjectURL(link.href);
    });
}
function graph_sentiment(df_radar, df_sentiment){
  var trace1 = {
      x: df_sentiment.map(row => row.time),
      y: df_sentiment.map(row => row.raiva),
      type: 'bar',
      name: 'Raiva',
      marker: {
        color: "crimson",
      },
      hovertemplate: "Confiança: %{y} <br>Tempo: %{x}",
      xaxis: 'x1',
      yaxis: 'y1',
  };
    
  var trace2 = {
      x: df_sentiment.map(row => row.time),
      y: df_sentiment.map(row => row.tristeza),
      type: 'bar',
      name: 'Tristeza',
      marker: {
        color: "blue",
      },
      hovertemplate: "Confiança: %{y} <br>Tempo: %{x}",
      xaxis: 'x2',
      yaxis: 'y2',
  };
    
  var trace3 = {
      x: df_sentiment.map(row => row.time),
      y: df_sentiment.map(row => row.alegria),
      type: 'bar',
      name: 'Alegria',
      marker: {
        color: "yellow",
      },
      hovertemplate: "Confiança: %{y} <br>Tempo: %{x}",
      xaxis: 'x3',
      yaxis: 'y3',
  };
    
  var trace4 = {
      x: df_sentiment.map(row => row.time),
      y: df_sentiment.map(row => row.surpresa),
      type: 'bar',
      name: 'Surpresa',
      marker: {
        color: "#EEEE33",
      },
      hovertemplate: "Confiança: %{y} <br>Tempo: %{x}",
      xaxis: 'x4',
      yaxis: 'y4',
  };
  
  var trace5 = {
      x: df_sentiment.map(row => row.time),
      y: df_sentiment.map(row => row.nojo),
      type: 'bar',
      name: 'Nojo',
      marker: {
        color: "#008000",
      },
      hovertemplate: "Confiança: %{y} <br>Tempo: %{x}",
      xaxis: 'x5',
      yaxis: 'y5',
  };
  
  var trace6 = {
      x: df_sentiment.map(row => row.time),
      y: df_sentiment.map(row => row.medo),
      type: 'bar',
      name: 'Medo',
      marker: {
        color: "#800080",
      },
      hovertemplate: "Confiança: %{y} <br>Tempo: %{x}",
      xaxis: 'x6',
      yaxis: 'y6',
  };  
  
  var trace7 = {
    type: 'scatterpolar',
    r: df_radar.map(row => row.Contagem),
    theta: df_radar.map(row => row.Emocao),
    fill: 'toself',
    hovertemplate: "Sentimento: %{theta} <br>Quantidade: %{r}",
    name: 'Sentiment Dominance Chart',
    customdata: df_radar.map(row => row.Contagem),
     marker: {
        color: 'orange',
        line: {
          color: "orange",
        },
      },
  };
  
  var data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7];
  
  var layout = {
    title: "Sentiment Dominance Chart",
    showlegend: false,
    paper_bgcolor: "rgba(33, 37, 41, 1)" ,
    plot_bgcolor: "rgba(0, 0, 0, 0)",
    font: {
      color: "white"
    },
    height: 1200,
    width: 1074.4,
    margin: {
      r: 60,
      t: 60,
      b: 40,
      l: 60,
    },
  
    polar: {
      angularaxis:{
        gridcolor: 'white',
      },
      radialaxis: {
        visible: true,
        //angle: 0,
        //tickangle: -90,
        gridcolor: 'white',
        tickwidth: 5,
        tickcolor: 'yellow',
        tickfont: {
          size: 15,
          //color: 'yellow'
        },
      },
      domain: {
        x: [0, 1],
        y: [0.60, 1],
      },
      bgcolor: "rgba(0, 0, 0, 0)",
    },
    
    xaxis1: {  // Defina o xaxis para especificar o domain do gráfico de barras
      anchor: "y1",
      domain: [0, 0.47],
      color: 'white',
      tickvals: df_sentiment.map(row => row.time),
    },
    yaxis1: {
      anchor: "x1",
      domain: [0.42, 0.55],
      range: [0, 100],
      title: {
        text: 'Confiança',
      },
      color: 'white',
      gridcolor: 'white'
    },
    
     xaxis2: {  // Defina o xaxis para especificar o domain do gráfico de barras
      anchor: "y2",
      domain: [0.53, 1],
      tickvals: df_sentiment.map(row => row.time),
    },
    
    yaxis2: {
      anchor: "x2",
      domain: [0.42, 0.55],
      range: [0, 100],
      color: 'white',
      gridcolor: 'white'
    },
    
     xaxis3: {  // Defina o xaxis para especificar o domain do gráfico de barras
      anchor: "y3",
      domain: [0, 0.47],
      tickvals: df_sentiment.map(row => row.time),
    },
    
    yaxis3: {
      anchor: "x3",
      domain: [0.22, 0.35],
      range: [0, 100],
      title: {
        text: 'Confiança',
      },
      color: 'white',
      gridcolor: 'white'
    },
    
     xaxis4: {  // Defina o xaxis para especificar o domain do gráfico de barras
      anchor: "y4",
      domain: [0.53, 1],
      tickvals: df_sentiment.map(row => row.time),
    },
    
    yaxis4: {
      anchor: "x4",
      domain: [0.22, 0.35],
      range: [0, 100],
      color: 'white',
      gridcolor: 'white'
    },
    
     xaxis5: {  // Defina o xaxis para especificar o domain do gráfico de barras
      anchor: "y5",
      domain: [0, 0.47],
       title: {
        text: 'Tempo (s)',
      },
      tickvals: df_sentiment.map(row => row.time),
    },
    
    yaxis5: {
      anchor: "x5",
      domain: [0.02, 0.15],
      range: [0, 100],
      title: {
        text: 'Confiança',
      },
      color: 'white',
      gridcolor: 'white'
    },
    
    xaxis6: {  // Defina o xaxis para especificar o domain do gráfico de barras
      anchor: "y6",
      domain: [0.53, 1],
      title: {
        text: 'Tempo (s)',
      },
      tickvals: df_sentiment.map(row => row.time),
    },
    
    yaxis6: {
      anchor: "x6",
      domain: [0.02, 0.15],
      range: [0, 100],
      color: 'white',
      gridcolor: 'white',
    },
    
   
    annotations: [{
      text: 'Raiva',
      font: {
            size: 16,
          },
      showarrow: false,
      align: 'center',
      x: 0.215, //position in x domain
      y: 0.56, //position in y domain
      xref: 'paper',
      yref: 'paper',
    },
    {
      text: 'Tristeza',
      font: {
            size: 16,
          },
      showarrow: false,
      align: 'center',
      x: 0.785, //position in x domain
      y: 0.56, //position in y domain
      xref: 'paper',
      yref: 'paper',
    },
    {
      text: 'Alegria',
      font: {
            size: 16,
          },
      showarrow: false,
      align: 'center',
      x: 0.215, //position in x domain
      y: 0.365, //position in y domain
      xref: 'paper',
      yref: 'paper',
    },
    {
      text: 'Surpresa',
      font: {
            size: 16,
          },
      showarrow: false,
      align: 'center',
      x: 0.785, //position in x domain
      y: 0.365, //position in y domain
      xref: 'paper',
      yref: 'paper',
    },
    {
      text: 'Nojo',
      font: {
            size: 16,
          },
      showarrow: false,
      align: 'center',
      x: 0.215, //position in x domain
      y: 0.165, //position in y domain
      xref: 'paper',
      yref: 'paper',
    },
    {
      text: 'Medo',
      font: {
            size: 16,
          },
      showarrow: false,
      align: 'center',
      x: 0.785, //position in x domain
      y: 0.165, //position in y domain
      xref: 'paper',
      yref: 'paper',
    }],
  };

  var graphDiv = document.getElementById('resultplot');
  
  Plotly.newPlot(graphDiv, data, layout, {showLink: false});
  
};
  
