Page({
  data: {
    imagePath: '',
    resultText: ''
  },

  chooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFiles[0].tempFilePath;
        this.setData({
          imagePath: filePath,
          resultText: '分析中...'
        });
        this.uploadImage(filePath);
      }
    });
  },

  uploadImage(filePath) {
    wx.uploadFile({
      url: 'http://127.0.0.1:5000/predict', // 替换为你的后端接口地址
      filePath: filePath,
      name: 'file',
      success: (res) => {
        const data = JSON.parse(res.data);
        this.setData({
          resultText: data.class_name || '未返回结果'
        });
      },
      fail: () => {
        this.setData({
          resultText: '上传失败，请重试'
        });
      }
    });
  }
});