(async function() {
  // Importação de dados
  covid_data = await d3.json("https://raw.githubusercontent.com/viniciusAC/Projeto-final-vis/main/base_de_dados/Base_de_dados.json").then(function(data) {
    data.forEach(function(d) {
      d.data = new Date(d.data)
    })
    return data;
  })

  bairros = await d3.json("https://raw.githubusercontent.com/viniciusAC/Projeto-final-vis/main/base_de_dados/FortalezaBairros.geojson").then(function(data) {
    return data  
  })

  // Auxiliares
  function getTops(source_group) {
    return {
      all: () => { return source_group.top(5) }
    }
  }

  function transform_dict(data) {
    let bairrosMap = new Map()
    data.forEach(function(d) {
      bairrosMap.set(d.key, d.value)
    })
    return bairrosMap
  }

  // Graficos simples
  facts =  crossfilter(covid_data)
  dateDim_filter = facts.dimension(d => d.data) //Gráfico de filtro por periodo

  dateDim = facts.dimension(d => d.data) //Gráfico de Linhas
  cases_normalized_by_day = dateDim.group().reduceSum(d => d['casos_confirmados_normalizado']) //Gráfico de filtro por periodo
  death_by_day = dateDim.group().reduceSum(d => d.obitos)  //Gráfico de Linhas de mortes por dia
  cases_by_day = dateDim.group().reduceSum(d => d['casos confirmados']) //Gráfico de Linhas de casos por dia

  ageDim = facts.dimension(d => d.faixa_etaria) //Gráfico de Setor
  cases_by_age = ageDim.group().reduceSum(d => d['casos confirmados']) //Gráfico de Setor de Casos por Idade
  death_by_age = ageDim.group().reduceSum(d => d.obitos) //Gráfico de Setor de Mortes por Idade

  bairroDim = facts.dimension(d => d.bairro).filter(function(d) { return d != "Indeterminado"; }) //Gráfico de Barras e Mapa
  death_by_bairro = bairroDim.group().reduceSum(d => d.obitos) //Gráfico de Barras
  cases_by_bairro = bairroDim.group().reduceSum(d => d['casos confirmados']) //Gráfico de Barras e Mapa

  width = 1100
  async function buildSimpleGrapics() {
    //Geração de Gráficos (exceto o de mapa)
    let periodBarChart = dc.barChart(document.querySelector("#filter-period-graph"))
    let lineChart = dc.lineChart(document.querySelector("#death"))
    let lineChart2 = dc.lineChart(document.querySelector("#cases"))
    let pieChart = dc.pieChart(document.querySelector("#cases-age-group-chart"))
    let pieChart2 = dc.pieChart(document.querySelector("#deaths-age-group-chart"))
    let barChart = dc.barChart(document.querySelector("#death-neighborhood-chart"))
    let barChart2 = dc.barChart(document.querySelector("#cases-neighborhood-chart"))

    let xScale = d3.scaleTime().domain([dateDim.bottom(1)[0].data, dateDim.top(1)[0].data])
    periodBarChart.width(width)
      .height(70)
      .margins({top: 10, right: 20, bottom: 20, left: 30})
      .dimension(dateDim_filter)
      .group(cases_normalized_by_day)
      .gap(70)
      .x(xScale)
      .xUnits(d3.timeDays)
      .elasticY(true)
      .centerBar(true)
      .renderHorizontalGridLines(true)
    
    //Gráfico de Linhas de óbitos por dia
    lineChart.width(width)
      .height(400)
      .dimension(dateDim)
      .margins({top: 30, right: 50, bottom: 25, left: 40})
      .renderArea(false)
      .x(xScale)
      .xUnits(d3.timeDays)
      .renderHorizontalGridLines(true)
      .legend(dc.legend().x(width-200).y(10).itemHeight(13).gap(5))
      .brushOn(false)
      .group(death_by_day, 'Obitos')
      .ordinalColors(['purple'])
    
    //Gráfico de Linhas de casos por dia
    lineChart2.width(width)
      .height(400)
      .dimension(dateDim)
      .margins({top: 30, right: 50, bottom: 25, left: 40})
      .renderArea(false)
      .x(xScale)
      .xUnits(d3.timeDays)
      .renderHorizontalGridLines(true)
      .legend(dc.legend().x(width-200).y(10).itemHeight(13).gap(5))
      .brushOn(false)
      .group(cases_by_day, 'Casos confirmados')
      .ordinalColors(['blue'])
    
    //Gráfico de Setor de Casos por Idade
    pieChart.width(300)
      .height(400)
      .slicesCap(4)
      .innerRadius(100)
      .dimension(ageDim)
      .group(cases_by_age)
      .legend(dc.legend().highlightSelected(true))
      .ordinalColors(['#C215B2', '#720AC9', '#0600B3', '#0A62C9', '#0AB8C2'])
      .on('pretransition', function(chart) {
        chart.selectAll('text.pie-slice').text(function(d) {
          return dc.utils.printSingleValue((d.endAngle - d.startAngle) /   (2*Math.PI) * 100) + '%';
        })
      });
    
    //Gráfico de Setor de Óbitos por Idade
    pieChart2.width(300)
      .height(350)
      .slicesCap(3)
      .innerRadius(100)
      .dimension(ageDim)
      .group(death_by_age)
      .legend(dc.legend().highlightSelected(true))
      .ordinalColors(['#C215B2', '#720AC9', '#0600B3', '#0A62C9'])
      .on('pretransition', function(chart) {
        chart.selectAll('text.pie-slice').text(function(d) {
          return dc.utils.printSingleValue((d.endAngle - d.startAngle) / (2*Math.PI) * 100) + '%';
        })
      });
    
    //Gráfico de Barras de Bairros com maior número de mortes
    let bairroDim = facts.dimension(d => d.bairro).filter(function(d) { return d != "Indeterminado"; })
    let death_by_bairro_top = getTops(death_by_bairro)
    let bairros = death_by_bairro.top(5).map(d => d.key)
    let x_bairro_scale = d3.scaleOrdinal().domain(bairros)
    barChart.width(500)
      .height(400)
      .dimension(bairroDim)
      .gap(80)
      .margins({top: 30, right: 50, bottom: 25, left: 40})
      .x(x_bairro_scale)
      .renderHorizontalGridLines(true)
      .legend(dc.legend().x(width-200).y(10).itemHeight(13).gap(5))
      .brushOn(true)
      .group(death_by_bairro_top, 'Obitos')
      .xUnits(dc.units.ordinal)
      .ordinalColors(['purple'])
      .elasticX()
    
    //Gráfico de Barras de Bairros com maior número de casos
    let cases_by_bairro_top = getTops(cases_by_bairro)
    let cases_bairros = cases_by_bairro.top(5).map(d => d.key)
    let x_bairro_scale2 = d3.scaleOrdinal().domain(cases_bairros)
    barChart2.width(500)
      .height(400)
      .dimension(bairroDim)
      .gap(80)
      .margins({top: 30, right: 50, bottom: 25, left: 40})
      .x(x_bairro_scale2)
      .renderHorizontalGridLines(true)
      .legend(dc.legend().x(width-200).y(10).itemHeight(13).gap(5))
      .brushOn(true)
      .group(cases_by_bairro_top, 'Casos')
      .xUnits(dc.units.ordinal)
      .elasticX()

    dc.renderAll()
  }  


  // MAPA
  death_by_bairro_map = bairroDim.group().reduceSum(d => d.obitos).top(Infinity)
  let deathsByName = transform_dict(death_by_bairro_map)
  bairros_info = await d3.csv("https://raw.githubusercontent.com/viniciusAC/Projeto-final-vis/main/base_de_dados/dados_bairros.csv").then(function(data) {
    let bairrosMap = new Map()
    data.forEach(function(d) {
      if (d["populaçao em 2020"] < 1){
        bairrosMap.set(d.Bairros, 0)
      }
      else{
        bairrosMap.set(d.Bairros,+Math.trunc((deathsByName.get(d.Bairros)/d["populaçao em 2020"])*10000))
      }       
    })
    return bairrosMap
  })

  async function buildMap(){
    let mapInstance = L.map('mapid').setView([-3.792614,-38.515877], 12)
    let blues = ["#E0AAFF", "#C77DFF", "#9D4EDD","#7B2CBF","#5A189A", "#3C096C", "#10002B"]
    let colorScale = d3.scaleQuantile()
      .domain([0, 20, 40, 70, 100, 200, 400, 700])
      .range(blues)

    L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",{ 
      attribution: `&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, Map tiles by &copy; <a href="https://carto.com/attribution">CARTO</a>`,
      maxZoom: 18
    }).addTo(mapInstance)
    
    let legendControl = L.control({position: 'bottomright'});
    legendControl.onAdd = function (map) {
      let div = L.DomUtil.create('div', 'info legend'),
      labels = [],
        n = blues.length,
      from, to;
  
      for (let i = 0; i < n; i++) {
        let c = blues[i]
          let fromto = colorScale.invertExtent(c);
        labels.push(
          '<i style="background:' + blues[i] + '"></i> ' +
          d3.format("d")(fromto[0]) + (d3.format("d")(fromto[1]) ? '&ndash;' + d3.format("d")(fromto[1]) : '+'));
      }
  
      div.innerHTML = labels.join('<br>')
      return div
    }
    legendControl.addTo(mapInstance)

    let infoControl = L.control()
    infoControl.onAdd = function (map) {
      this._div = L.DomUtil.create('div', 'info');
      this.update();
      return this._div;
    }
    infoControl.update = function (feat) {
      this._div.innerHTML = '<h5>Número de óbitos por 10k habitantes</h5>' +  (feat ?
        '<b>' + feat.properties.NOME + '</b><br />' + bairros_info.get(feat.properties.NOME) + ' óbitos por 10k hab'
        : 'Passe o mouse sobre um bairro');
    }
    infoControl.addTo(mapInstance)

    
    function style(feature) {
      return {
        weight: 1,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.9,
        fillColor: colorScale(bairros_info.get(feature.properties.NOME))
      };
    }

    function highlightFeature(e) {
      var layer = e.target;

      layer.setStyle({
          weight: 5,
          color: '#666',
          dashArray: '',
          fillOpacity: 0.7
      });

      if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
          layer.bringToFront();
      }
      infoControl.update(layer.feature);
    }

    function resetHighlight(e) {
      geojson.resetStyle(e.target);
      infoControl.update();
    }

    function zoomToFeature(e) {
      mapInstance.fitBounds(e.target.getBounds());
    }

    function onEachFeature(feature, layer) {
      layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
      });
    }

    geojson = L.geoJson(bairros, {
      style: style,
      onEachFeature: onEachFeature
    }).addTo(mapInstance);
  
    return geojson
  }

  cases_by_day_calendar = dateDim.group().reduceSum(d => d['casos confirmados']).top(Infinity)
  years = d3.groups(cases_by_day_calendar, d => d.key.getUTCFullYear()).reverse()
  cellSize = 17
  width = 960
  height = 136
  timeWeek = d3.utcSunday
  countDay = i => i
  w = timeWeek.count(d3.utcYear(1), 1)
  function pathMonth(t) {
    const n = 7;
    const d = Math.max(0, Math.min(n, countDay(t.getUTCDay())));
    const w = timeWeek.count(d3.utcYear(t), t);
    return `${d === 0 ? `M${w * cellSize},0`
        : d === n ? `M${(w + 1) * cellSize},0`
        : `M${(w + 1) * cellSize},0V${d * cellSize}H${w * cellSize}`}V${n * cellSize}`;
  }

  formatValue = d3.format("+.4")
  formatClose = d3.format("$,.2f")
  formatDate = d3.utcFormat("%x")
  formatDay = i => "DSTQQSS"[i]
  formatMonth = d3.utcFormat("%b")

  max = d3.quantile(cases_by_day_calendar, 0.9975, (d) => Math.abs(d.value));
  color = d3.scaleQuantize()
    .domain([0, +max])
    .range(["#E0AAFF", "#C77DFF", "#9D4EDD","#7B2CBF","#5A189A", "#3C096C", "#10002B"]);

  //Gráfico de Calendário 
  async function buildCalendar() {
    var svg = d3.select('.calendar')
    .attr("viewBox", [0, 0, width, height * years.length])
    .attr("font-family", "sans-serif")
    .attr("font-size", 10);

    const year = svg.selectAll("g")
      .data(years)
      .join("g")
      .attr("transform", (d, i) => `translate(40.5,${height * i + cellSize * 1.5})`);

    year.append("text")
      .attr("x", -5)
      .attr("y", -5)
      .attr("font-weight", "bold")
      .attr("text-anchor", "end")
      .text(([key]) => key);

    year.append("g")
      .attr("text-anchor", "end")
      .selectAll("text")
      .data(d3.range(7))
      .join("text")
      .attr("x", -5)
      .attr("y", i => (countDay(i) + 0.5) * cellSize)
      .attr("dy", "0.31em")
      .text(formatDay);

    year.append("g")
      .selectAll("rect")
      .data(([, values]) => values)
      .join("rect")
      .attr("width", cellSize - 1)
      .attr("height", cellSize - 1)
      .attr("x", d => timeWeek.count(d3.utcYear(d.key), d.key) * cellSize + 0.5)
      .attr("y", d => countDay(d.key.getUTCDay()) * cellSize + 0.5)
      .attr("fill", d => color(d.value))
      .append("title")
      .text(d => `${formatDate(d.key)}
    ${formatValue(d.value)}${d.close === undefined ? "" : `
    ${formatClose(d.close)}`}`);

    const month = year.append("g")
      .selectAll("g")
      .data(([, values]) => d3.utcMonths(new Date('2020-01-01'), new Date('2020-12-5')))
    .join("g");

    month.filter((d, i) => i).append("path")
      .attr("fill", "none")
      .attr("stroke", "#fff")
      .attr("stroke-width", 3)
      .attr("d", pathMonth);

    month.append("text")
      .attr("x", d => timeWeek.count(d3.utcYear(d), timeWeek.ceil(d)) * cellSize + 2)
      .attr("y", -5)
      .text(formatMonth);
      
    return svg.node();
  }


  buildSimpleGrapics()
  buildMap()
  buildCalendar() 
})()