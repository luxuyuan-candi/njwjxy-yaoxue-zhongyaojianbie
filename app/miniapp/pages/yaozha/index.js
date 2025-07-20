// pages/yaozha/index.js
Page({
  data: {
    unitList: []
  },

  onLoad() {
    this.fetchRecycleList();
  },

    // ✅ 下拉刷新回调
  onPullDownRefresh() {
    this.fetchRecycleList(() => {
      wx.stopPullDownRefresh(); // 关闭刷新动画
    });
  },

  fetchRecycleList() {
    wx.request({
      url: 'https://www.njwjxy.cn:30443/api/get_recycles', // 替换为你的实际地址
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          const formattedList = res.data.data.map(item => {
            // 将 GMT 格式转换成 Date 对象
            const dateObj = new Date(item.date);
            // 转换为 yyyy-mm-dd 格式
            const year = dateObj.getFullYear();
            const month = String(dateObj.getMonth() + 1).padStart(2, '0');
            const day = String(dateObj.getDate()).padStart(2, '0');
            item.date = `${year}-${month}-${day}`;
  
            return item;
          });
  
          this.setData({
            unitList: formattedList
          });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/yaozha_recycle_detail/index?id=${id}`
    });
  },

  goToStatistics() {
    wx.showToast({
      title: '跳转到统计页',
      icon: 'success'
    });
    // wx.navigateTo({ url: '/pages/statistics/statistics' }); // 如果你已有页面
  },

  onAddClick() {
    wx.navigateTo({ url: '/pages/yaozha_add/index' }); // 实际跳转页
  }
});