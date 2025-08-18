Page({
  data: {
    products: []
  },

  onLoad() {
    this.loadProducts();
  },

  loadProducts(callback) {
    wx.request({
      url: 'https://www.njwjxy.cn:30443/api/maoning_maoshashiyong/products',
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

  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/maoshashiyong_detail/index?id=${id}`
    });
  },

  goToAdd() {
    wx.navigateTo({
      url: '/pages/maoshashiyong_add/index'
    });
  }
});

