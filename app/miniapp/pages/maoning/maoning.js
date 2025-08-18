Page({
  data: {
    swiperInterval: 5000, // 默认轮播间隔5秒
    videoList: [
      { src: 'https://www.njwjxy.cn:30443/cat-video/video_1.mp4' },
      { src: 'https://www.njwjxy.cn:30443/cat-video/video_2.mp4' },
      { src: 'https://www.njwjxy.cn:30443/cat-video/video_3.mp4' },
      { src: 'https://www.njwjxy.cn:30443/cat-video/video_4.mp4' }
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
  },
  goToMaoShaShiYong() {
    wx.navigateTo({
      url: '/pages/maoshashiyong/index'
    })
  }
})