Page({
  data: {
    imagePath: '',
    resultText: '',
    className: '',
    requestContent: '',
    isQuireMode: true,
    answer: '',
    isSubmit: false,
    answerContent: ''
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
    const jsonData = {
      input: {
        input: "根据上述内容，请出一道不同的选择题， 然后我来作答，你判断是否正确。"
      }
    };
    this.setData({
      isQuireMode: false,
      isSubmit: false,
      requestContent: '问题生成中...',
      answer: '',
      answerContent: ''
    })
    wx.request({
      url: 'https://www.njwjxy.cn/chat',
      method: 'POST',
      data: jsonData,
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        const data = res.data;
        this.setData({
          requestContent: data.output || '未返回结果'
        });
      },
      fail: () => {
        this.setData({
          requestContent: '问题生成失败'
        });
      }
    });
  },
  uploadImage(filePath) {
    this.setData({
      className: '',
      resultText: '分析中...',
      isQuireMode: true
    })
    wx.uploadFile({
      url: 'https://www.njwjxy.cn/predict', // 替换为你的后端接口地址
      filePath: filePath,
      name: 'file',
      success: (res) => {
        const data = JSON.parse(res.data);
        this.setData({
          className: data.class_name || '未返回结果',
          resultText: data.content || '未返回结果',
        });
      },
      fail: () => {
        this.setData({
          resultText: '上传失败，请重试',
          className: '',
        });
      }
    });
  },
  handleInput(e) {
    this.setData({
      answer: e.detail.value
    })
  },
  submitAnswer() {
    const jsonData = {
      input: {
        input: this.data.answer
      }
    };
    this.setData({
      answerContent: '判断中...',
      isQuireMode: false,
      isSubmit: true
    });
    wx.request({
      url: 'https://www.njwjxy.cn/chat',
      method: 'POST',
      data: jsonData,
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        const data = res.data;
        this.setData({
          answerContent: data.output || '未返回结果'
        });
      },
      fail: () => {
        this.setData({
          answerContent: '判断返回失败'
        });
      }
    });
  },
  resetAnswer() {
    this.questionsGet();
  }
});