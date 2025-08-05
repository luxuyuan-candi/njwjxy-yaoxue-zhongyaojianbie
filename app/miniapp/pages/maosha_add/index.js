// pages/maosha_add/index.js
Page({
  data: {
    image: '',
    spec: '',
    price: '',
    location: '',
    phone: ''
  },
  chooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      success: (res) => {
        this.setData({
          image: res.tempFiles[0].tempFilePath
        });
      }
    });
  },
  onInput(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({
      [key]: e.detail.value
    });
  },
  submit() {
    const { image, spec, price, location, phone } = this.data;
    wx.uploadFile({
      url: 'https://www.njwjxy.cn:30443/api/maoning_maosha/upload',
      filePath: image,
      name: 'image',
      formData: { spec, price, location, phone },
      success: (res) => {
        wx.showToast({ title: '上传成功' });
        wx.navigateBack();
      }
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
});
