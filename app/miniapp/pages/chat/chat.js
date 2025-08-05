// pages/index/chat.js
Page({
  data: {
    inputText: '',
    messages: [
      { from: 'bot', text: '您好，我是药邻康小助手，仅提供参考，不能代替医生诊疗，请问有什么可以帮您？' }
    ],
    loading: false,
    currentMessage: '',
    cleared: false,
    showForm: false,
    formData: {
      name: '',
      gender: '',
      age: '',
      history: '',
      symptoms: '',
      duration: '',
      medication: '',
      allergy: ''
    }
  },
  onLoad() {
    console.log("已经登录")
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
      url: 'https://www.njwjxy.cn:30443/rag/query',
      method: 'POST',
      data: jsonData,
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        console.log("清理成功")
      },
      fail: () => {
        console.log("清理失败")
      },
      complete: () => {
        this.setData({ cleared: false });
      }
    });
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
      url: 'https://www.njwjxy.cn:30443/rag/query',
      method: 'POST',
      data: jsonData,
      timeout: 300000,
      header: {
        'content-type': 'application/json'
      },
      responseType: 'arraybuffer', // 接收字节流
      /*
      success: (res) => {
        const reply = res.data.output || '未返回结果';
        newMessages.push({ from: 'bot', text: reply });
        this.setData({
          messages: newMessages
        });
      },
      */
      success: (res) => {
        const result = this.ab2str(res.data);
        this.displayTypingEffect(result);
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
  ab2str(buf) {
    const decoder = new TextDecoder('utf-8');
    return decoder.decode(new Uint8Array(buf));
  },
  displayTypingEffect(text) {
    let index = 0;
    const interval = setInterval(() => {
      if (index < text.length) {
        const newChar = text[index++];
        const messages = this.data.messages;
  
        if (messages[messages.length - 1]?.from === 'bot') {
          messages[messages.length - 1].text += newChar;
        } else {
          messages.push({ from: 'bot', text: newChar });
        }
  
        this.setData({ messages, currentMessage: messages[messages.length - 1].text });
      } else {
        clearInterval(interval);
        this.setData({ loading: false, currentMessage: '' });
      }
    }, 50);
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
            url: 'https://www.njwjxy.cn:30443/rag/query',
            method: 'POST',
            data: jsonData,
            header: {
              'content-type': 'application/json'
            },
            success: (res) => {
              this.setData({
                messages: [
                  { from: 'bot', text: '您好，我是药邻康小助手，仅提供参考，不能代替医生诊疗，请问有什么可以帮您？' }
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
  },
  copyText(e) {
    const content = e.currentTarget.dataset.content;
    wx.setClipboardData({
      data: content,
      success(res) {
        wx.showToast({
          title: '复制成功'
        });
      }
    });
  },
  onLongPress(e) {
    const text = e.currentTarget.dataset.content;
    const that = this;
    wx.showActionSheet({
      itemList: ['复制文字', '转为语音', '用药详情'],
      success(res) {
        if (res.tapIndex === 0) {
          // 复制到剪贴板
          wx.setClipboardData({
            data: text,
            success() {
              wx.showToast({ title: '已复制', icon: 'success' });
            }
          });
        } else if (res.tapIndex === 1) {
          // 语音播放功能（简单使用 TTS）
          that.playTextAudio(text);
        } else if (res.tapIndex === 2) {
          wx.navigateTo({
            url: `/pages/detail/detail?content=${encodeURIComponent(text)}`
          });
        }
      },
      fail(res) {
        console.log(res.errMsg);
      }
    });
  },
  
  // 简易文字转语音播放（需后台支持）
  playTextAudio(text) {
    if (text.length > 500) {
      wx.showToast({
        title: '文本过长，最多支持500字符',
        icon: 'none',
        duration: 2000
      });
      return;
    }
    wx.showLoading({
      title: '正在生成语音...',
      mask: true
    });
    wx.request({
      url: 'https://www.njwjxy.cn:30443/api/qwen-tts', // 替换成你自己的 TTS API
      method: 'POST',
      data: { text },
      success(res) {
        wx.hideLoading(); // 隐藏加载提示
  
        const audioUrl = res.data.audioUrl;
        const innerAudioContext = wx.createInnerAudioContext();
  
        innerAudioContext.src = audioUrl;
  
        // 播放开始时提示
        innerAudioContext.onPlay(() => {
          wx.showToast({
            title: '语音播放中',
            icon: 'none',
            duration: 1500
          });
        });
  
        // 播放结束时提示
        innerAudioContext.onEnded(() => {
          wx.showToast({
            title: '播放完成',
            icon: 'none',
            duration: 1000
          });
        });
  
        // 播放错误处理
        innerAudioContext.onError((res) => {
          wx.showToast({
            title: '播放出错',
            icon: 'none',
            duration: 1500
          });
        });
        innerAudioContext.play();
      },
      fail() {
        wx.hideLoading();
        wx.showToast({
          title: '语音播放失败',
          icon: 'none'
        });
      }
    });
  },
  onOpenForm() {
    this.setData({ showForm: true });
  },
  onFormCancel() {
    this.setData({ showForm: false });
  },
  onFormInput(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({
      [`formData.${field}`]: value
    });
  },
  onFormSubmit() {
    const data = this.data.formData;

    // 简单验证：至少填写姓名和症状
    if (!data.name || !data.symptoms) {
      wx.showToast({
        title: '请填写姓名和症状',
        icon: 'none'
      });
      return;
    }

    // 格式化消息内容
    const messageText = 
      `👤 姓名：${data.name}\n` +
      `性别：${data.gender || '未填写'}\n` +
      `年龄：${data.age || '未填写'}\n` +
      `📝 既往史：${data.history || '无'}\n` +
      `⚠️ 症状：${data.symptoms}\n` +
      `⏱ 症状持续时间：${data.duration || '未填写'}\n` +
      `💊 药品/保健品：${data.medication || '无'}\n` +
      `🌿 过敏史：${data.allergy || '无'}`;

    this.setData({ showForm: false }, () => {
      this.setData({
        formData: {
          name: '',
          gender: '',
          age: '',
          history: '',
          symptoms: '',
          duration: '',
          medication: '',
          allergy: ''
        },
        inputText: messageText
      });
      this.onSend();
    });
  },
});