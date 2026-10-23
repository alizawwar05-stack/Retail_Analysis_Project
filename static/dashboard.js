'use strict';
const stats = JSON.parse(document.getElementById('chart-data').textContent);
const teal = '#087f78';
const config = {
  responsive: true,
  displaylogo: false,
  displayModeBar: 'hover',
  modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
  toImageButtonOptions: {
    format: 'png',
    scale: 2
  }
};
const base = {
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: {
    family: 'Segoe UI, Arial, sans-serif',
    color: '#72838a',
    size: 10
  },
  margin: {
    l: 65,
    r: 25,
    t: 25,
    b: 45
  },
  hoverlabel: {
    bgcolor: '#102e36',
    font: {
      color: '#fff'
    }
  },
  xaxis: {
    showline: false,
    zeroline: false,
    gridcolor: '#edf2f3',
    fixedrange: true
  },
  yaxis: {
    showline: false,
    zeroline: false,
    gridcolor: '#edf2f3',
    fixedrange: true
  }
};

function empty(id, message) {
  return Plotly.newPlot(id, [], {
    ...base,
    xaxis: {
      visible: false
    },
    yaxis: {
      visible: false
    },
    annotations: [{
      text: message,
      showarrow: false,
      x: .5,
      y: .5,
      xref: 'paper',
      yref: 'paper'
    }]
  }, config);
}
if (stats.rows) {
  Plotly.newPlot('monthly-chart', [{
    x: stats.monthly.labels,
    y: stats.monthly.values,
    type: 'scatter',
    mode: 'lines+markers',
    line: {
      color: teal,
      width: 2.5
    },
    marker: {
      size: 6,
      color: teal,
      line: {
        color: '#fff',
        width: 1.5
      }
    },
    fill: 'tozeroy',
    fillcolor: 'rgba(8,127,120,.06)',
    hovertemplate: '%{x}<br>£%{y:,.2f}<extra></extra>'
  }], {
    ...base,
    xaxis: {
      ...base.xaxis,
      type: 'date',
      tickformat: '%b %Y',
      nticks: 7,
      showgrid: false
    },
    yaxis: {
      ...base.yaxis,
      tickprefix: '£',
      tickformat: '~s',
      rangemode: 'tozero'
    }
  }, config);
} else empty('monthly-chart', 'No sales for these filters');

function bars(id, rows, products = false) {
  if (!rows.length) return empty(id, 'No records in this selection');
  // Escape data labels that Plotly otherwise interprets as limited HTML.
  const safe = value => String(value).replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  } [c]));
  const labels = rows.map(r => safe(r.label));
  Plotly.newPlot(id, [{
    type: 'bar',
    orientation: 'h',
    x: rows.map(r => r.amount),
    y: labels,
    marker: {
      color: rows.map((_, i) => i === 0 ? teal : '#a5d4c8')
    },
    customdata: rows.map(r => safe(products ? r.description : r.label)),
    hovertemplate: '%{customdata}<br>£%{x:,.2f}<extra></extra>'
  }], {
    ...base,
    margin: {
      l: products ? 80 : 112,
      r: 30,
      t: 17,
      b: 40
    },
    bargap: .42,
    xaxis: {
      ...base.xaxis,
      tickprefix: '£',
      tickformat: '~s',
      rangemode: 'tozero'
    },
    yaxis: {
      ...base.yaxis,
      type: 'category',
      autorange: 'reversed',
      showgrid: false,
      categoryorder: 'array',
      categoryarray: labels
    }
  }, config);
}
bars('countries-chart', stats.countries);
bars('products-chart', stats.products, true);
if (stats.customers) {
  Plotly.newPlot('customers-chart', [{
    type: 'pie',
    values: [stats.repeat, stats.once],
    labels: ['Repeat', 'One-time'],
    hole: .79,
    sort: false,
    direction: 'clockwise',
    marker: {
      colors: [teal, '#d7e7e6']
    },
    textinfo: 'none',
    hovertemplate: '%{label}: %{value:,}<br>%{percent}<extra></extra>'
  }], {
    ...base,
    showlegend: false,
    margin: {
      l: 30,
      r: 30,
      t: 24,
      b: 24
    },
    annotations: [{
      text: `<b>${stats.repeat_pct.toFixed(2)}%</b>`,
      x: .5,
      y: .55,
      font: {
        size: 28,
        color: '#172f38'
      },
      showarrow: false
    }, {
      text: 'repeat customers',
      x: .5,
      y: .36,
      font: {
        size: 10
      },
      showarrow: false
    }]
  }, config);
} else empty('customers-chart', 'No identified customers');

// Anchor navigation keeps the active date and country selection.
document.querySelectorAll('.sidebar nav a').forEach(link => {
  link.href = window.location.pathname + window.location.search + link.hash;
  link.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    link.classList.add('active');
  });
});
document.querySelector('.filters').addEventListener('submit', event => {
  const from = document.querySelector('[name=start]');
  const to = document.querySelector('[name=end]');
  to.setCustomValidity(from.value > to.value ? 'End date must be on or after the start date.' : '');
  if (!to.reportValidity()) event.preventDefault();
});
document.querySelector('[name=end]').addEventListener('input', event => event.target.setCustomValidity(''));
document.querySelector('[name=start]').addEventListener('input', () => document.querySelector('[name=end]').setCustomValidity(''));
