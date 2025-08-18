// pages/maosha_add/index.js
Page({
  data: {
    image: '',
    name: '',
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
    const { image, name, phone } = this.data;
    wx.uploadFile({
      url: 'https://www.njwjxy.cn:30443/api/maoning_maoshashiyong/upload',
      filePath: image,
      name: 'image',
      formData: { name, phone },
      success: (res) => {
        wx.showToast({ title: '上传成功' });
        wx.navigateBack();
      }
    });
  },
});
