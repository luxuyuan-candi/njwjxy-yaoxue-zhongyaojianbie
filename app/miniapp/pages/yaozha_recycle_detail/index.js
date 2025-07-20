// pages/yaozha_recycle_detail/index.js
Page({
  data: {
    form: {}
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
  
          // ✅ 格式化 date 字段为 yyyy-mm-dd
          if (data.date) {
            const d = new Date(data.date);
            const y = d.getFullYear();
            const m = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            data.date = `${y}-${m}-${day}`;
          }
  
          // ✅ 处理状态字段
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
    const id = this.data.form.id;
    wx.request({
      url: `https://www.njwjxy.cn:30443/api/update_state`,
      method: 'POST',
      data: {
        id: id,
        state: 'finish'
      },
      header: { 'content-type': 'application/json' },
      success: (res) => {
        if (res.data.success) {
          wx.showToast({
            title: '状态已更新',
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
  }
});
