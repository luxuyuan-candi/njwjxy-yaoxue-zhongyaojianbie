// pages/yaozha_add/index.js
Page({
  data: {
    date: '',
    location: ''
  },

  onDateChange(e) {
    this.setData({
      date: e.detail.value
    });
  },

  getLocation() {
    const that = this;
    wx.getLocation({
      type: 'wgs84',
      success(res) {
        wx.chooseLocation({
          success(loc) {
            that.setData({
              location: loc.address
            });
          }
        });
      },
      fail() {
        wx.showToast({
          title: '无法获取定位权限',
          icon: 'none'
        });
      }
    });
  },

  onSubmit(e) {
    const data = e.detail.value;
    const date = this.data.date;
    const location = this.data.location;
  
    if (!data.unit || !data.contact || !date || !location || !data.weight) {
      wx.showToast({
        title: '请填写所有字段',
        icon: 'none'
      });
      return;
    }
  
    const postData = {
      unit: data.unit,
      contact: data.contact,
      date: date,
      location: location,
      weight: data.weight,
      herbs: data.herbs || []  // 复选框返回数组
    };
  
    wx.request({
      url: 'https://www.njwjxy.cn:30443/api/add_recycle',  // 替换为你的后端接口地址
      method: 'POST',
      data: postData,
      header: {
        'content-type': 'application/json'
      },
      success(res) {
        if (res.data.success) {
          wx.showToast({
            title: '提交成功',
            icon: 'success',
            duration: 1500,
            success() {
              setTimeout(() => {
                wx.navigateBack();
              }, 1500);
            }
          });
        } else {
          wx.showToast({
            title: '提交失败',
            icon: 'none'
          });
        }
      },
      fail() {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  }  
});