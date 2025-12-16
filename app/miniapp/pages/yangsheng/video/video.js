// pages/yangsheng/video/video.js
Page({
  data: {
    video: {}
  },

  onLoad(options) {
    const id = options.id
    this.getVideoDetail(id)
  },

  getVideoDetail(id) {
    // 示例数据（后期换成接口）
    const data = {
      id,
      title: '八段锦 · 基础篇',
      duration: '12分钟',
      level: '初级',
      desc: '本功法适合初学者练习，通过缓慢、协调的动作舒展筋骨，调和气血。',
      src: 'https://www.njwjxy.cn:30443/cat-video/video_4.mp4'
    }

    this.setData({
      video: data
    })
  }
})
