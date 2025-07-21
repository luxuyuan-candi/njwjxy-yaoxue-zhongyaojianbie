// pages/yaozha_summary/index.js
Page({
  data: {
    summaryList: []
  },

  onLoad() {
    this.fetchSummary();
  },

  fetchSummary() {
    wx.request({
      url: 'https://www.njwjxy.cn:30443/api/recycle_summary',
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
  goToDetail(e) {
    const { unit, location } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/yaozha_summary_detail/index?unit=${encodeURIComponent(unit)}&location=${encodeURIComponent(location)}`
    });
  }
});
