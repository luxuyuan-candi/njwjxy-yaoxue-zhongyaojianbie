// pages/yangsheng/index/index.js
Page({
  data: {
    showSidebar: false
  },

  openSidebar() {
    this.setData({ showSidebar: true })
  },

  closeSidebar() {
    this.setData({ showSidebar: false })
  },

  goPage(e) {
    const page = e.currentTarget.dataset.page


    wx.navigateTo({
      url: `/pages/yangsheng/${page}/index`
    })
  },
  goIndex() {
    this.closeSidebar()

    wx.switchTab({
      url: `/pages/index/index`
    })
  }
})
