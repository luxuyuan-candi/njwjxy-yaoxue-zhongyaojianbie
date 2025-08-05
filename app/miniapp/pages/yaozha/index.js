// pages/yaozha/index.js
Page({
  data: {
    unitList: [],
    filters: ['全部', '单位', '个人'],
    activeFilter: '全部'
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

  onFilterChange(e) {
    const selected = e.currentTarget.dataset.type;
    this.setData({ activeFilter: selected }, () => {
      this.fetchRecycleList();
    });
  },

  fetchRecycleList(callback) {
    let url = 'https://www.njwjxy.cn:30443/api/get_recycles';
    const typeMap = { '单位': 'company', '个人': 'person' };
    const typeParam = typeMap[this.data.activeFilter];
  
    if (typeParam) {
      url += '?type=' + encodeURIComponent(typeParam);
    }
  
    wx.request({
      url,
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          const formattedList = res.data.data.map(item => {
            const dateObj = new Date(item.date);
            const year = dateObj.getFullYear();
            const month = String(dateObj.getMonth() + 1).padStart(2, '0');
            const day = String(dateObj.getDate()).padStart(2, '0');
            item.date = `${year}-${month}-${day}`;
            return item;
          });
  
          this.setData({ unitList: formattedList });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        if (callback) callback();
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

    wx.navigateTo({ url: '/pages/yaozha_summary/index' }); // 如果你已有页面
  },

  onAddClick() {
    wx.navigateTo({ url: '/pages/yaozha_add/index' }); // 实际跳转页
  }
});