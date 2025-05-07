App({
  globalData: {
    openid: null,
    userInfo: null
  },
  onLaunch() {
    wx.login({
      success: res => {
        if (res.code) {
          wx.request({
            url: 'https://www.njwjxy.cn:30443/wx-login',
            method: 'POST',
            data: { code: res.code },
            success: result => {
              this.globalData.openid = result.data.openid
              console.log('openid 已保存：', this.globalData.openid)
            }
          })
        }
      }
    })
  },

  onShow() {
    console.log('App Show');
  },

  onHide() {
    console.log('App Hide');
  },

  globalData: {
    userInfo: null
  }
});