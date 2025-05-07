Page({
  data: {
    avatarUrl: '../../images/header.png',
    nickname: '',
    recognitionCount: 0,
    quizScore: '24/50'
  },

  fetchData() {
    wx.request({
      url: 'https://www.njwjxy.cn:30443/recognition',
      method: 'POST',
      data: { openid: this.data.nickname },
      success: result => {
        this.setData({
          recognitionCount: result.data.recognition_count
        });
        console.log('recognitionCount已获取')
      },
      fail: err => {
        console.error('请求失败', err);
      },
      complete: () => {
        wx.stopPullDownRefresh();
      }
    })
  },

  onLoad() {
    // 如果全局已经有了，就直接展示
    const globalUser = getApp().globalData.openid
    if (globalUser) {
      this.setData({
        nickname: globalUser
      })
    }
    this.fetchData();
  },

  onPullDownRefresh() {
    console.log('触发下拉刷新');
    this.fetchData();
  },

  onChooseAvatar(e) {
    this.setData({
      avatarUrl: e.detail.avatarUrl
    });
  },
  onInputNickname(e) {
    this.setData({
      nickname: e.detail.value
    });
  }
})