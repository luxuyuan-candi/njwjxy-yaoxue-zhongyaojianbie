Page({
  data: {
    imagesDict: {
      "西药": [ 
        {url: 'https://www.njwjxy.cn:30443/medicine-images/H20013003.png', name: '复方对乙酰氨基酚片(II)(散列通)', desc: '用于普通感冒或流行性感冒引起的发热，也用于缓解轻至中度疼痛如头痛、关节痛、偏头痛、牙痛、肌肉痛、神经痛、痛经。'},
        {url: 'https://www.njwjxy.cn:30443/medicine-images/H20013063.png', name: '氨麻美敏片[新康泰克]', desc: '适用于普通感冒或流行性感冒引起的发热、头痛、四肢酸痛、打喷嚏流鼻涕、鼻塞、咳嗽、咽痛等症状'},
       ],
      "中成药": [ 
        {url: 'https://www.njwjxy.cn:30443/medicine-images/Z36021034.png', name: '感冒清胶囊(仁和)', desc: '解表散热，疏肝和胃。用于外感病，邪犯少阳证，症见寒热往来、胸胁苦满、食欲不振、心烦喜呕、口苦咽干'},
        {url: 'https://www.njwjxy.cn:30443/medicine-images/Z44021940.png', name: '感冒灵颗粒', desc: '用于感冒引起的头痛，发热，鼻塞，流涕，咽痛等'},
       ],
      "中成药和西药组合": [ 
        {url: 'https://www.njwjxy.cn:30443/medicine-images/Z20050067.png', name: '桑姜感冒胶囊', desc: '散风清热，祛寒止咳。用于感冒，咳嗽，头痛，咽喉肿痛'},
        {url: 'https://www.njwjxy.cn:30443/medicine-images/Z45021046.png', name: '维C银翘片', desc: '辛凉解表，清热解毒。用于流行性感冒引起的发热头痛、咳嗽、口干、咽喉疼痛'},
       ],
      "保健品": [ 
        {url: 'https://www.njwjxy.cn:30443/medicine-images/Z44022226.png', name: '复方感冒灵片', desc: '辛凉解表，清热解毒。用于风热感冒之发热，微恶风寒，头身痛，口干而渴，鼻塞涕浊，咽喉红肿疼痛，咳嗽，痰黄粘稠'},
       ]
    },
    categories: ["西药","中成药","中成药和西药组合","保健品"] // 用来保存字典的key列表
  },
  onLoad() {
    this.setData({
      categories: Object.keys(this.data.imagesDict)
    });
  }
});
