// pages/yaozha_recycle_detail/index.js
Page({
  data: {
    form: {},
    showModal: false,
  },

  onLoad(options) {
    const id = options.id;
    this.fetchDetail(id);
  },

  fetchDetail(id) {
    wx.request({
      url: `https://www.njwjxy.cn:30443/api/maoning_maoshashiyong/product?id=${id}`,
      method: 'GET',
      success: (res) => {
        this.setData({ form: res.data });
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'none' });
        if (callback) callback();
      }
    });
  },

  markAsFinished() {
    this.setData({ showModal: true });
  },

  onCancel() {
    this.setData({ showModal: false });
  },

  onConfirm() {
    wx.request({
      url: `https://www.njwjxy.cn:30443/api/maoning_maoshashiyong/update`,
      method: 'POST',
      data: {
        id: this.data.form.id,
        state: 'approve',
      },
      header: { 'content-type': 'application/json' },
      success: (res) => {
        if (res.data.success) {
          wx.showToast({
            title: '已核准',
            icon: 'success',
            success: () => {
              setTimeout(() => {
                wx.navigateBack();
              }, 1500);
            }
          });
        } else {
          wx.showToast({ title: '更新失败', icon: 'none' });
        }
      }
    });

    this.setData({ showModal: false });
  }
});