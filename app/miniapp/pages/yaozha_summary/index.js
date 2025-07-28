// pages/yaozha_summary/index.js
Page({
  data: {
    summaryList: [],
    activeFilter: 'all'  // 默认全部
  },

  onLoad() {
    this.fetchSummary();
  },

  fetchSummary() {
    const type = this.data.activeFilter;
    let url = 'https://www.njwjxy.cn:30443/api/recycle_summary';

    // 如果不是全部，则加上类型过滤参数
    if (type !== 'all') {
      url += `?type=${type}`;
    }

    wx.request({
      url,
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          this.setData({
            summaryList: res.data.data
          });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  changeFilter(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({ activeFilter: type }, () => {
      this.fetchSummary();  // 切换后重新拉取数据
    });
  },

  goToDetail(e) {
    const { unit, location } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/yaozha_summary_detail/index?unit=${encodeURIComponent(unit)}&location=${encodeURIComponent(location)}`
    });
  }
});
