Page({
  data: {
    swiperInterval: 5000, // 默认轮播间隔5秒
    videoList: [
      { src: 'https://www.pexels.com/zh-cn/download/video/13764245/' },
      { src: 'https://www.pexels.com/zh-cn/download/video/19709308/' },
      { src: 'https://www.pexels.com/zh-cn/download/video/3040808/' }
    ]
  },

  // 视频播放时暂停轮播
  onVideoPlay() {
    this.setData({ swiperInterval: 0 }); // 停止自动轮播
  },

  // 视频播放结束恢复轮播
  onVideoEnded() {
    this.setData({ swiperInterval: 5000 }); // 恢复轮播
  },

  goToYaoZha() {
    wx.navigateTo({
      url: '/pages/yaozha/index'
    })
  },
  goToMaoSha() {
    wx.navigateTo({
      url: '/pages/maosha/index'
    })
  }
})