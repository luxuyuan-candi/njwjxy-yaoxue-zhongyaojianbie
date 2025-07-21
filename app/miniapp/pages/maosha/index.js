Page({
  data: {
    products: []
  },

  onLoad() {
    this.loadProducts();
  },

  loadProducts(callback) {
    wx.request({
      url: 'https://www.njwjxy.cn:30443/api/maoning_maosha/products',
      method: 'GET',
      success: (res) => {
        this.setData({ products: res.data });
        if (callback) callback();
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'none' });
        if (callback) callback();
      }
    });
  },

  onPullDownRefresh() {
    this.loadProducts(() => {
      wx.stopPullDownRefresh(); // 停止下拉动画
    });
  },

  goToAdd() {
    wx.navigateTo({
      url: '/pages/maosha_add/index'
    });
  }
});

