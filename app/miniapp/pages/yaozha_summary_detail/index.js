// pages/yaozha_summary_detail/index.js
Page({
  data: {
    unit: '',
    location: '',
    total: 0,
    categories: [],
    barData: [],
    lineData: [],
    ec: null // 不提前初始化
  },

  onLoad(options) {
    const unit = decodeURIComponent(options.unit || '');
    const location = decodeURIComponent(options.location || '');
    this.setData({ unit, location });
    this.fetchDetail(unit, location);
  },

  fetchDetail(unit, location) {
    wx.request({
      url: `https://www.njwjxy.cn:30443/api/recycle_by_unit?unit=${encodeURIComponent(unit)}&location=${encodeURIComponent(location)}`,
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          const { records, location, total } = res.data.data;

          const categories = records.map(r => {
            const d = new Date(r.date);
            return `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')}`;
          });

          const barData = records.map(r => parseFloat(r.total_weight));
          const lineData = [...barData];

          this.setData({ location, total, categories, barData, lineData }, () => {
            this.initChart();
          });
        }
      }
    });
  },

  initChart() {
    const chartComponent = this.selectComponent('#recycleChart');
    const echarts = require('../../components/ec-canvas/echarts');

    chartComponent.init((canvas, width, height, dpr) => {
      const chart = echarts.init(canvas, null, {
        width,
        height,
        devicePixelRatio: dpr
      });
      canvas.setChart(chart);

      const { categories, barData, lineData } = this.data;

      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['柱状图', '折线图'] },
        xAxis: {
          type: 'category',
          data: categories
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '柱状图',
            type: 'bar',
            data: barData
          },
          {
            name: '折线图',
            type: 'line',
            data: lineData
          }
        ]
      });

      return chart;
    });
  }
});
