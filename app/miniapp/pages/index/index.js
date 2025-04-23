Page({
  data: {
    userInfo: {},
    hasUserInfo: false,
    avatarUrl: '',
    nickname: ''
  },
  onLoad() {
    // 如果全局已经有了，就直接展示
    const globalUser = getApp().globalData.openid
    if (globalUser) {
      this.setData({
        nickname: globalUser
      })
    }
  },
  onChooseAvatar(e) {
    this.setData({
      avatarUrl: e.detail.avatarUrl,
      hasUserInfo: true
    });
  },
  onInputNickname(e) {
    this.setData({
      nickname: e.detail.value,
      hasUserInfo: true
    });
  }
})