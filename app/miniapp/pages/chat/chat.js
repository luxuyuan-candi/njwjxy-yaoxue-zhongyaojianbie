// pages/index/chat.js
Page({
  data: {
    inputText: '',
    messages: [
      { from: 'bot', text: '您好，我是慢病随访小助手，请问有什么可以帮您？' }
    ],
    loading: false,
    cleared: false
  },

  onInput(e) {
    this.setData({
      inputText: e.detail.value
    });
  },

  onSend() {
    const text = this.data.inputText.trim();
    if (!text) return;
  
    const newMessages = [...this.data.messages, { from: 'user', text }];
    this.setData({ messages: newMessages, inputText: '', loading: true });
    const jsonData = {
      input: {
        input: text,
        openid: getApp().globalData.openid
      }
    };
    // 调用后端
    wx.request({
      url: 'https://www.njwjxy.cn/rag/query',
      method: 'POST',
      data: jsonData,
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        const reply = res.data.output || '未返回结果';
        newMessages.push({ from: 'bot', text: reply });
        this.setData({
          messages: newMessages
        });
      },
      fail: () => {
        newMessages.push({ from: 'bot', text: '网络错误，请稍后再试。' });
        this.setData({
          messages: newMessages
        });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },
  onClear() {
    wx.showModal({
      title: '提示',
      content: '确定要清除所有对话吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            cleared: true
          });
          const jsonData = {
            input: {
              input: "清理缓存",
              openid: getApp().globalData.openid
            }
          };
          wx.request({
            url: 'https://www.njwjxy.cn/rag/query',
            method: 'POST',
            data: jsonData,
            header: {
              'content-type': 'application/json'
            },
            success: (res) => {
              this.setData({
                messages: [
                  { from: 'bot', text: '您好，我是慢病随访小助手，请问有什么可以帮您？' }
                ]
              });
            },
            fail: () => {
              newMessages.push({ from: 'bot', text: '网络错误，请稍后再试。' });
              this.setData({
                messages: newMessages
              });
            },
            complete: () => {
              this.setData({ cleared: false });
            }
          });
        }
      }
    });
  }
});