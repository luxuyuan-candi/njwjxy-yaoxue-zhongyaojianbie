Page({
  data: {
    image: '',
    erweiimage: '',
    ywymimage: '',
    spec: '',
    price: '',
    location: '',
    phone: ''
  },
  chooseImage(e) {
    const key = e.currentTarget.dataset.key;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      success: (res) => {
        this.setData({
          [key]: res.tempFiles[0].tempFilePath
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
    const { image, erweiimage, ywymimage, spec, price, location, phone } = this.data;
    let uploadId = null;
  
    // 第一步，上传主图
    wx.uploadFile({
      url: 'https://www.njwjxy.cn:30443/api/maoning_maosha/upload',
      filePath: image,
      name: 'image',
      formData: { spec, price, location, phone },
      success: (res) => {
        const data = JSON.parse(res.data);
        uploadId = data.uploadId;
  
        // 第二步，上传二维码
        if (erweiimage) {
          wx.uploadFile({
            url: 'https://www.njwjxy.cn:30443/api/maoning_maosha/upload',
            filePath: erweiimage,
            name: 'erweiimage',
            formData: { uploadId },
          });
        }
  
        // 第三步，上传溯源码
        if (ywymimage) {
          wx.uploadFile({
            url: 'https://www.njwjxy.cn:30443/api/maoning_maosha/upload',
            filePath: ywymimage,
            name: 'ywymimage',
            formData: { uploadId },
          });
        }
  
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