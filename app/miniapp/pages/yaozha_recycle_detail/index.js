// pages/yaozha_recycle_detail/index.js
Page({
  data: {
    form: {},
    showModal: false,
    inputWeight: ''
  },

  onLoad(options) {
    const id = options.id;
    this.fetchDetail(id);
  },

  fetchDetail(id) {
    wx.request({
      url: `https://www.njwjxy.cn:30443/api/get_recycle?id=${id}`,
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          const data = res.data.data;

          // 格式化日期
          if (data.date) {
            const d = new Date(data.date);
            const y = d.getFullYear();
            const m = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            data.date = `${y}-${m}-${day}`;
          }

          data.status = data.state === 'finish' ? '已回收' : '待处理';
          data.herbs = data.herbs || '';
          this.setData({ form: data });
        } else {
          wx.showToast({ title: '加载失败', icon: 'none' });
        }
      }
    });
  },

  markAsFinished() {
    this.setData({ showModal: true });
  },

  onInputWeight(e) {
    this.setData({ inputWeight: e.detail.value });
  },

  onCancel() {
    this.setData({ showModal: false, inputWeight: '' });
  },

  onConfirm() {
    const weight = parseFloat(this.data.inputWeight);
    if (isNaN(weight) || weight <= 0) {
      wx.showToast({ title: '请输入有效重量', icon: 'none' });
      return;
    }

    const id = this.data.form.id;
    wx.request({
      url: `https://www.njwjxy.cn:30443/api/update_state`,
      method: 'POST',
      data: {
        id: id,
        state: 'finish',
        approved_weight: weight
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

    this.setData({ showModal: false, inputWeight: '' });
  }
});