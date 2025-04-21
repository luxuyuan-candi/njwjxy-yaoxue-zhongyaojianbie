Page({
  data: {
    imagePath: '',
    resultText: '',
    className: ''
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
          resultText: '分析中...',
          className: ''
        });
        this.uploadImage(filePath);
      }
    });
  },
  questionsGet() {
  },
  uploadImage(filePath) {
    wx.uploadFile({
      url: 'https://www.njwjxy.cn/predict', // 替换为你的后端接口地址
      filePath: filePath,
      name: 'file',
      success: (res) => {
        const data = JSON.parse(res.data);
        this.setData({
          className: data.class_name || '未返回结果',
          resultText: data.content || '未返回结果'
        });
      },
      fail: () => {
        this.setData({
          resultText: '上传失败，请重试',
          className: ''
        });
      }
    });
  }
});