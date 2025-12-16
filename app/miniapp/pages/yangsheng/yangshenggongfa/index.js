// pages/yangsheng/index/index.js
Page({
  data: {
    showSidebar: false,
    videoList: [
      {
        id: 1,
        title: '八段锦 · 基础篇',
        desc: '舒筋活络，适合初学者',
        cover: '/assets/video1.jpg'
      },
      {
        id: 2,
        title: '五禽戏 · 呼吸训练',
        desc: '调理气血，改善体质',
        cover: '/assets/video2.jpg'
      }
    ]
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
  },
  goVideo(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/yangsheng/video/video?id=${id}`
    })
  }
})
