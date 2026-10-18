var SPOT_IMAGES={
  '陕西省历史博物馆':'/static/景点照片/spot1.png',
  '大唐芙蓉园':'/static/景点照片/spot2.png',
  '青龙寺':'/static/景点照片/spot3.png',
  '大雁塔':'/static/景点照片/spot4.png',
  '终南山南五台':'/static/景点照片/spot5.png',
  '西安城墙':'/static/景点照片/spot6.png',
  '西安博物院':'/static/景点照片/spot7.png',
  '钟楼':'/static/景点照片/spot8.png',
  '大唐不夜城':'/static/景点照片/spot9.png',
  '华清宫':'/static/景点照片/spot10.png',
  '兵马俑':'/static/景点照片/spot11.png',
  '白鹿原':'/static/景点照片/spot12.png'
};
var SPOT_3D_MODELS={
  '大雁塔':{
    id:'0f669b923c7c4ec98a699ff9342f017d',
    url:'https://sketchfab.com/3d-models/giant-wild-goose-pagoda-0f669b923c7c4ec98a699ff9342f017d'
  },
  '钟楼':{
    id:'aeab462f18ab4347bfa0b943efe97b8b',
    url:'https://sketchfab.com/3d-models/the-bell-tower-of-xian-aeab462f18ab4347bfa0b943efe97b8b'
  },
  '兵马俑':{
    id:'c3c7b97bc4f044bfbac59d78233e9a2c',
    url:'https://sketchfab.com/3d-models/terracotta-general-figure-qin-dynastychina-c3c7b97bc4f044bfbac59d78233e9a2c'
  }
};

var spot3DPreviousOverflow='';
function openSpot3DModel(){
  var modal=document.getElementById('spot3DModal');
  if(!modal)return;
  var frame=modal.querySelector('.sketchfab-frame');
  var modelId=frame&&frame.getAttribute('data-model-id');
  if(!frame||!modelId)return;
  if(!frame.src||frame.src==='about:blank'){
    frame.src='https://sketchfab.com/models/'+modelId+'/embed?autostart=1&ui_theme=dark';
  }
  spot3DPreviousOverflow=document.body.style.overflow;
  document.body.style.overflow='hidden';
  modal.hidden=false;
  modal.setAttribute('aria-hidden','false');
  var closeButton=modal.querySelector('.sketchfab-close');
  if(closeButton)closeButton.focus();
  document.addEventListener('keydown',handleSpot3DKeydown);
}
function closeSpot3DModel(){
  var modal=document.getElementById('spot3DModal');
  if(!modal)return;
  var frame=modal.querySelector('.sketchfab-frame');
  if(frame)frame.src='about:blank';
  modal.hidden=true;
  modal.setAttribute('aria-hidden','true');
  document.body.style.overflow=spot3DPreviousOverflow;
  document.removeEventListener('keydown',handleSpot3DKeydown);
  var trigger=document.querySelector('.hero-name-3d');
  if(trigger)trigger.focus();
}
function handleSpot3DKeydown(event){
  if(event.key==='Escape')closeSpot3DModel();
}
function fullscreenSpot3DModel(){
  var dialog=document.querySelector('#spot3DModal .sketchfab-dialog');
  if(!dialog)return;
  if(dialog.requestFullscreen)dialog.requestFullscreen();
  else if(dialog.webkitRequestFullscreen)dialog.webkitRequestFullscreen();
}
var SPOT_INTRO={
  '陕西省历史博物馆':{
    type:'文化景点',
    desc:[
      '陕西历史博物馆位于西安市雁塔区小寨东路91号，是中国第一座大型现代化国家级博物馆，被誉为"古都明珠，华夏宝库"。',
      '馆藏文物多达170余万件，上起远古人类初始阶段使用的简单石器，下至1840年前社会生活中的各类器物，时间跨度长达一百多万年。',
      '其中商周青铜器精美绝伦、历代陶俑千姿百态、汉唐金银器独步全国，被誉为"地下文物宝库"的精华浓缩。'
    ]
  },
  '大唐芙蓉园':{
    type:'文化景点',
    desc:[
      '大唐芙蓉园位于西安市曲江新区，是中国第一个全方位展示盛唐风貌的大型皇家园林式文化主题公园。',
      '园内汇集了唐代园林建筑、文化、艺术、礼仪、服饰、饮食等多元盛唐文化，是体验大唐盛世的绝佳去处。',
      '夜晚的水幕电影、灯光秀和各类唐风演出，让游客仿佛穿越回千年前的长安城。'
    ]
  },
  '青龙寺':{
    type:'文化景点',
    desc:[
      '青龙寺始建于隋代开皇二年（公元582年），是汉传佛教密宗祖庭，也是日本佛教真言宗的发源地。',
      '寺内樱花是西安春季最负盛名的赏樱胜地，每年三四月份樱花盛开时节，游人如织。',
      '青龙寺承载着深厚的中日文化交流史，至今仍是中日佛教文化交流的重要场所。'
    ]
  },
  '大雁塔':{
    type:'文化景点',
    desc:[
      '大雁塔位于西安市大慈恩寺内，是唐代著名高僧玄奘法师为保存由天竺经丝绸之路带回长安的经卷佛像而主持修建。',
      '塔高64.5米，共七层，是西安市的标志性建筑和著名古迹，1961年被列为全国重点文物保护单位。',
      '塔下的大雁塔北广场是亚洲最大的音乐喷泉广场，每晚的水景表演吸引众多游客驻足观赏。'
    ]
  },
  '终南山南五台':{
    type:'自然景点',
    desc:[
      '终南山位于西安市以南，是秦岭山脉的重要组成部分，自古以来就是道教文化的发祥地之一。',
      '五台山景区山势峻秀，林木葱茏，四季景色各异，是登山观景、避暑休闲的理想去处。',
      '山中古刹众多，文化底蕴深厚，"终南捷径"的典故就源于此地。'
    ]
  },
  '西安城墙':{
    type:'文化景点',
    desc:[
      '西安城墙是中国现存规模最大、保存最完整的古代城垣，始建于明洪武年间，至今已有600多年历史。',
      '城墙周长13.7公里，墙高12米，可以骑行环游一周，俯瞰古城风光，感受千年历史的厚重。',
      '夜晚的城墙在灯光映衬下气势恢宏，是西安最具代表性的历史文化地标之一。'
    ]
  },
  '西安博物院':{
    type:'文化景点',
    desc:[
      '西安博物院位于西安市碑林区友谊西路72号，是一座集文物收藏、展示、研究于一体的综合性博物馆。',
      '院内以著名的唐代建筑小雁塔为中心，馆藏文物11万余件，其中三级以上珍贵文物14400余件。',
      '小雁塔为唐代密檐式砖塔的典型代表，是西安唐代文化的重要见证。'
    ]
  },
  '钟楼':{
    type:'文化景点',
    desc:[
      '西安钟楼位于市中心，建于明洪武十七年（1384年），是中国现存形制最大、保存最完整的钟楼。',
      '钟楼坐落于古城中心，是西安传统文化的象征，登楼可俯瞰四方街景，感受古城风貌。',
      '夜晚的钟楼在灯光下金碧辉煌，与不远处的鼓楼交相辉映，是西安最具标志性的夜景之一。'
    ]
  },
  '大唐不夜城':{
    type:'休闲娱乐',
    desc:[
      '大唐不夜城位于西安市曲江新区大雁塔脚下，是中国规模最大的开放式步行街区之一。',
      '街区以盛唐文化为背景，融合现代商业、餐饮、演艺等多元业态，被誉为"全国十大夜经济地标"。',
      '不倒翁小姐姐、巡游表演、大唐光影秀等特色演出已成为西安最受欢迎的网红打卡场景。'
    ]
  },
  '华清宫':{
    type:'文化景点',
    desc:[
      '华清宫位于西安市临潼区骊山脚下，因唐玄宗与杨贵妃的爱情故事和"长恨歌"而闻名于世。',
      '景区内拥有保存完好的唐代皇家温泉遗址和西安事变发生地"五间厅"，承载着深厚的历史文化。',
      '大型实景历史舞剧《长恨歌》以骊山为背景，是中国旅游演艺的经典之作。'
    ]
  },
  '兵马俑':{
    type:'文化景点',
    desc:[
      '秦始皇兵马俑博物馆位于西安市临潼区，是世界文化遗产，被誉为"世界第八大奇迹"。',
      '兵马俑发现于1974年，是秦始皇陵的陪葬坑，出土的陶俑形态各异，栩栩如生，展现了秦代高超的雕塑艺术。',
      '一号坑、二号坑、三号坑共出土陶俑、陶马近八千件，规模宏大，气势恢宏。'
    ]
  },
  '白鹿原':{
    type:'文化景点',
    desc:[
      '白鹿原位于西安市东南，是关中平原上一片广袤的黄土台塬，因陈忠实的同名长篇小说而闻名于世。',
      '景区融合了关中民俗文化、影视拍摄、休闲度假等多元业态，是体验陕西农耕文化的特色目的地。',
      '原上风光秀美，民俗活动丰富，老腔表演、传统手工艺展示让游客深度感受关中文化的魅力。'
    ]
  }
};
var SPOT_COORDS={
  '陕西省历史博物馆':[108.9484, 34.2241],
  '大唐芙蓉园':    [108.9759, 34.2098],
  '青龙寺':        [108.9817, 34.2363],
  '大雁塔':        [108.9594, 34.2225],
  '终南山南五台':  [108.8417, 34.0233],
  '西安城墙':      [108.9398, 34.2614],
  '西安博物院':    [108.9387, 34.2438],
  '钟楼':          [108.9425, 34.2658],
  '大唐不夜城':    [108.9617, 34.2156],
  '华清宫':        [109.2151, 34.3636],
  '兵马俑':        [109.2785, 34.3848],
  '白鹿原':        [109.1372, 34.1856]
};
var SPOT_META={
  '陕西历史博物馆':{
    level:'国家一级博物馆',
    duration:'3-4小时',
    bestTime:'全年皆宜',
    openTime:'09:00-17:30 (周一闭馆)',
    address:'西安市雁塔区小寨东路91号'
  },
  '大唐芙蓉园':{
    level:'AAAAA级',
    duration:'4-5小时',
    bestTime:'春秋 / 夜晚',
    openTime:'09:00-22:00',
    address:'西安市曲江新区芙蓉西路99号'
  },
  '青龙寺':{
    level:'AAAA级',
    duration:'1-2小时',
    bestTime:'3-4月赏樱季',
    openTime:'09:00-17:00',
    address:'西安市雁塔区西影路与雁翔路交叉口'
  },
  '大雁塔':{
    level:'AAAAA级',
    duration:'2-3小时',
    bestTime:'夜晚音乐喷泉',
    openTime:'08:00-17:00 (登塔 09:00-17:00)',
    address:'西安市雁塔区慈恩路1号'
  },
  '终南山南五台':{
    level:'AAAA级',
    duration:'一整天',
    bestTime:'夏秋季节',
    openTime:'08:00-17:00',
    address:'西安市长安区五台街道'
  },
  '西安城墙':{
    level:'AAAAA级',
    duration:'2-3小时',
    bestTime:'傍晚 / 夜晚',
    openTime:'08:00-22:00',
    address:'西安市碑林区南大街2号'
  },
  '西安博物院':{
    level:'国家一级博物馆',
    duration:'2-3小时',
    bestTime:'全年皆宜',
    openTime:'09:00-17:30 (周二闭馆)',
    address:'西安市碑林区友谊西路72号'
  },
  '钟楼':{
    level:'全国重点文保',
    duration:'1小时',
    bestTime:'夜晚',
    openTime:'08:30-21:00',
    address:'西安市碑林区东西南北四条大街交汇处'
  },
  '大唐不夜城':{
    level:'AAAA级',
    duration:'3-4小时',
    bestTime:'夜晚 19:00 后',
    openTime:'全天开放 (商铺 10:00-22:00)',
    address:'西安市雁塔区雁塔南路大雁塔南广场'
  },
  '华清宫':{
    level:'AAAAA级',
    duration:'3-4小时',
    bestTime:'春秋季节',
    openTime:'07:00-19:00',
    address:'西安市临潼区华清路038号'
  },
  '兵马俑':{
    level:'AAAAA级 · 世界遗产',
    duration:'3-4小时',
    bestTime:'春秋季节',
    openTime:'08:30-17:30',
    address:'西安市临潼区秦陵北路'
  },
  '白鹿原':{
    level:'AAAA级',
    duration:'4-5小时',
    bestTime:'春秋季节',
    openTime:'09:00-21:00',
    address:'西安市灞桥区滨河大道'
  }
};
var spots=[],rankData=[],charts={},theme=localStorage.getItem('theme')||'dark';
var cmpSelectedSpots = ['', '', ''];  // 已选的3个景点
var dataMaxDate = null;   // 数据最新日期（从后端取）
var currentRankingMode = 'hot';   // 全局榜单状态：'hot' / 'quality'
var homeHotData = [];             // 首页热度榜缓存
var homeQualityData = [];         // 首页好评榜缓存
var spotNegInsights = {};         // 景点差评原因缓存
document.documentElement.setAttribute('data-theme',theme);
// ===== 词云页筛选框 =====
async function generateAllWC(){
  var spot=document.getElementById('globalSpotSelect').value;
  var oldSel=document.getElementById('wcs');
  if(oldSel) oldSel.value=spot;

  // 1. 综合词云
  var urlAll='/api/wordcloud';
  if(spot) urlAll+='?spot_name='+encodeURIComponent(spot);
  var dAll=await api(urlAll);
  if(dAll&&dAll.length){
    mkW('wc0',dAll);
    window._wcDataAll=dAll;     // 缓存到全局
  } else {
    window._wcDataAll=[];
  }

  // 2. 好评词云
  var pos=await api('/api/wordcloud?'+(spot?'spot_name='+encodeURIComponent(spot)+'&':'')+'sentiment=positive');
  if(pos&&pos.length){
    mkW('wc1',pos);
    window._wcDataPos=pos;
  } else {
    window._wcDataPos=[];
  }

  // 3. 差评词云
  var neg=await api('/api/wordcloud?'+(spot?'spot_name='+encodeURIComponent(spot)+'&':'')+'sentiment=negative');
  if(neg&&neg.length){
    mkW('wc2',neg);
    window._wcDataNeg=neg;
  } else {
    window._wcDataNeg=[];
  }

  // 4. 根据当前激活的 Tab 渲染 TOP10
  var activeTab=document.querySelector('.wc-tab-card .wc-tab.on');
  var target=activeTab?activeTab.getAttribute('data-target'):'综合';
  renderKeywordRankByTab(target);

  // 5. 情感关键词热力图
  loadKeywordSentimentChart();

  // 6. 时序词云
  loadTimeWordCloud(spot);
}

// 根据当前 Tab 取对应数据渲染 TOP10
function renderKeywordRankByTab(target){
  var data=[];
  if(target==='综合')      data=window._wcDataAll||[];
  else if(target==='好评') data=window._wcDataPos||[];
  else if(target==='差评') data=window._wcDataNeg||[];
  renderKeywordRank(data);
}
// Tab 切换：综合 / 好评 / 差评
function switchWCTab(el, target){
  var tabs=document.querySelectorAll('.wc-tab-card .wc-tab');
  tabs.forEach(function(t){t.classList.remove('on')});
  if(el) el.classList.add('on');

  var panes=document.querySelectorAll('.wc-tab-content');
  panes.forEach(function(p){p.classList.remove('active')});
  var current=document.querySelector('.wc-tab-content[data-pane="'+target+'"]');
  if(current) current.classList.add('active');

  // ✨ 切 Tab 同时切 TOP10
  renderKeywordRankByTab(target);

  setTimeout(function(){
    var chartId=target==='综合'?'wc0':(target==='好评'?'wc1':'wc2');
    if(charts[chartId]&&!charts[chartId].isDisposed()){
      charts[chartId].resize();
    }
  },50);
    // 动态标题
  var titleEl=document.querySelector('.wc-rank-card .ch-title');
  if(titleEl){
    if(target==='综合') titleEl.textContent='综合关键词 TOP10';
    else if(target==='好评') titleEl.textContent='好评关键词 TOP10';
    else if(target==='差评') titleEl.textContent='差评关键词 TOP10';
  }
}

// 渲染关键词热度 TOP10
function renderKeywordRank(data){
  var listEl=document.getElementById('wcRankList');
  if(!listEl)return;
  if(!data||!data.length){
    listEl.innerHTML='<div class="wc-rank-empty">暂无数据</div>';
    return;
  }
  // 取 TOP10
  var top10=data.slice(0,10);
  var totalValue=data.reduce(function(s,d){return s+(d.value||0)},0);
  var maxValue=top10[0].value||1;

  // 渐变色池
  var colors=['#3b82f6','#6366f1','#8b5cf6','#a78bfa','#10b981','#34d399','#fbbf24','#fb923c','#ef4444','#f472b6'];

  listEl.innerHTML=top10.map(function(d,i){
    var rank=i+1;
    var pct=totalValue>0?(d.value/totalValue*100).toFixed(2):'0.00';
    var barPct=(d.value/maxValue*100).toFixed(0);
    var color=colors[i%colors.length];
    var rankCls=rank<=3?'top':'';
    return '<div class="wcr-item">'
      +'<div class="wcr-num '+rankCls+'" style="background:'+color+'">'+rank+'</div>'
      +'<div class="wcr-name">'+d.name+'</div>'
      +'<div class="wcr-count">'+d.value.toLocaleString()+'</div>'
      +'<div class="wcr-bar"><div class="wcr-bar-fill" style="width:'+barPct+'%;background:'+color+'"></div></div>'
      +'<div class="wcr-pct">'+pct+'%</div>'
      +'</div>';
  }).join('');
}
function initGlobalSpotSelect(){
  var sel=document.getElementById('globalSpotSelect');
  if(!sel) return;
  if(!spots||spots.length===0){
    setTimeout(initGlobalSpotSelect,1000);
    return;
  }
  sel.innerHTML='<option value="">全部景点</option>';
  spots.forEach(function(s){
    var opt=document.createElement('option');
    opt.value=s;
    opt.textContent=s;
    sel.appendChild(opt);
  });
}

async function onGlobalSpotChange(){
  // 触发完整的词云重载（综合 + 好评 + 差评 + 热力图 + 工作日节假日词云）
  await generateAllWC();
}
async function loadDetailAgeChart(spotName){
  if(!spotName)return;
  var url='/api/age_data?spot_name='+encodeURIComponent(spotName);
  var data=await api(url);
  if(!data)return;

  // ===== 1. 环形图（出行场景）- 带环外标签 =====
  var donutEl=document.getElementById('portraitDonut');
  if(donutEl){
    var scenes=(data.游客画像&&data.游客画像.出行场景)?data.游客画像.出行场景:{};
    var sceneOrder=['亲子出行','家庭出行','情侣出行','朋友结伴','独自旅行'];
    var sceneColors={'亲子出行':'#fbbf24','家庭出行':'#10b981','情侣出行':'#f472b6','朋友结伴':'#3b82f6','独自旅行':'#a78bfa'};
    var pieData=[];
    sceneOrder.forEach(function(name){
      var val=scenes[name];
      if(val&&val>0){
        pieData.push({name:name,value:val,itemStyle:{color:sceneColors[name]}});
      }
    });
    if(pieData.length>0){
      var c=mk('portraitDonut');
      if(c){
        c.setOption({
          backgroundColor:'transparent',
          tooltip:{
            trigger:'item',
            formatter:'{b}: {c}%',
            backgroundColor:tt.backgroundColor,borderColor:tt.borderColor,textStyle:tt.textStyle
          },
          series:[{
            type:'pie',
            radius:['40%','60%'],
            center:['50%','50%'],
            padAngle:2,
            itemStyle:{borderRadius:4,borderColor:css('--card'),borderWidth:2},
            label:{
              show:true,
              position:'outside',
              formatter:'{b}\n{c}%',
              color:css('--t1'),
              fontSize:12,
              fontWeight:'bold',
              lineHeight:16
            },
            labelLine:{
              show:true,
              length:10,
              length2:10,
              lineStyle:{color:css('--t3'),width:1}
            },
            emphasis:{scale:true,scaleSize:5},
            data:pieData
          }]
        });
      }
    } else {
      donutEl.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--t3);font-size:13px">暂无场景数据</div>';
    }
  }

  // ===== 2. 主要客群 =====
  var mainEl=document.getElementById('portraitMainCluster');
  if(mainEl&&data.典型客群聚类){
    var entries=Object.entries(data.典型客群聚类);
    entries.sort(function(a,b){return (b[1].占比||0)-(a[1].占比||0)});
    if(entries.length>0){
      var topName=entries[0][0];
      var topInfo=entries[0][1];
      var topPct=Math.min(100,topInfo.占比||0).toFixed(1);
      mainEl.innerHTML=
        '<div class="pmc-label">主要客群</div>'
        +'<div class="pmc-content">'
        +'<span class="pmc-name">'+topName+'</span>'
        +'<span class="pmc-pct">'+topPct+'%</span>'
        +'</div>';
    }
  }

  // ===== 3. 关注重点 TOP3 =====
  var focusEl=document.getElementById('portraitFocus');
  if(focusEl){
    var focus=(data.行为特征画像&&data.行为特征画像.关注重点)?data.行为特征画像.关注重点:{};
    var fEntries=Object.entries(focus).sort(function(a,b){return b[1]-a[1]}).slice(0,3);
    if(fEntries.length>0){
      focusEl.innerHTML=fEntries.map(function(p){
        var pct=Math.min(100,p[1]).toFixed(1);
        return '<span class="psi-tag">'+p[0]+' '+pct+'%</span>';
      }).join('');
    } else {
      focusEl.innerHTML='<span class="psi-tag" style="opacity:.5">暂无</span>';
    }
  }

  // ===== 4. 信息渠道 TOP3 =====
  var channelsEl=document.getElementById('portraitChannels');
  if(channelsEl){
    var channels=(data.行为特征画像&&data.行为特征画像.浏览偏好)?data.行为特征画像.浏览偏好:{};
    var cEntries=Object.entries(channels).sort(function(a,b){return b[1]-a[1]}).slice(0,3);
    if(cEntries.length>0){
      channelsEl.innerHTML=cEntries.map(function(p){
        var pct=Math.min(100,p[1]).toFixed(1);
        return '<span class="psi-tag">'+p[0]+' '+pct+'%</span>';
      }).join('');
    } else {
      channelsEl.innerHTML='<span class="psi-tag" style="opacity:.5">暂无</span>';
    }
  }
}

// ===== 时序词云 =====
// ===== 工作日 vs 节假日 差异分析 =====
var currentDiffSentiment = 'positive';

async function loadTimeWordCloud(spotName){
  spotName = spotName || '';
  await loadWeekdayHolidayDiff(spotName);
}

async function loadWeekdayHolidayDiff(spotName){
  var url = '/api/weekday_holiday_diff';
  if(spotName) url += '?spot_name=' + encodeURIComponent(spotName);

  var data = await api(url);
  if(!data) return;

  window._diffData = data;
  renderDiffByTab(currentDiffSentiment);
}

// 渲染差异对比
function renderDiffByTab(sentiment){
  var data = window._diffData;
  if(!data) return;

  var diffData = data[sentiment] || {workday_only: [], holiday_only: [], common: []};

  renderDiffList('workdayDiffList', diffData.workday_only, 'workday');
  renderDiffList('holidayDiffList', diffData.holiday_only, 'holiday');
  renderCommonTags(diffData.common);

  // 更新计数
  var wEl = document.getElementById('workdayCount');
  var hEl = document.getElementById('holidayCount');
  if(wEl) wEl.textContent = 'TOP ' + diffData.workday_only.length;
  if(hEl) hEl.textContent = 'TOP ' + diffData.holiday_only.length;
}

function renderDiffList(elId, items, type){
  var el = document.getElementById(elId);
  if(!el) return;

  if(!items || items.length === 0){
    el.innerHTML = '<div class="diff-loading">暂无差异数据</div>';
    return;
  }

  var maxCount = items[0].count;
  el.innerHTML = items.map(function(item){
    var pct = (item.count / maxCount * 100).toFixed(0);
    return '<div class="diff-item">'
      + '<span class="diff-word">' + item.word + '</span>'
      + '<div class="diff-bar"><div class="diff-bar-fill" style="width:' + pct + '%"></div></div>'
      + '<span class="diff-count">' + item.count + '</span>'
      + '</div>';
  }).join('');
}

function renderCommonTags(items){
  var el = document.getElementById('commonWordsTags');
  if(!el) return;

  if(!items || items.length === 0){
    el.innerHTML = '<span class="diff-loading-inline">暂无共同高频词</span>';
    return;
  }

  el.innerHTML = items.map(function(item){
    return '<span class="diff-tag">'
      + item.word
      + '<span class="diff-tag-count">' + item.count + '</span>'
      + '</span>';
  }).join('');
}

// Tab 切换
function switchDiffTab(el, sentiment){
  currentDiffSentiment = sentiment;
  var tabs = document.querySelectorAll('.week-tabs .wc-tab');
  tabs.forEach(function(t){ t.classList.remove('on') });
  if(el) el.classList.add('on');

  renderDiffByTab(sentiment);
}

function createParticles(){var c=document.getElementById('particles');if(!c)return;c.innerHTML='';for(var i=0;i<18;i++){var p=document.createElement('div');p.className='particle';var sz=Math.random()*4+2;var cl=theme==='dark'?['rgba(0,212,170,.15)','rgba(167,139,250,.15)']:['rgba(13,148,136,.08)','rgba(124,58,237,.08)'];p.style.cssText='width:'+sz+'px;height:'+sz+'px;left:'+Math.random()*100+'%;background:'+cl[Math.floor(Math.random()*cl.length)]+';animation-duration:'+(Math.random()*15+10)+'s;animation-delay:'+(Math.random()*10)+'s';c.appendChild(p)}}
createParticles();

window.addEventListener('scroll',function(){document.getElementById('topbar').classList.toggle('scrolled',window.scrollY>10);var btn=document.getElementById('backTop');if(btn)btn.classList.toggle('show',window.scrollY>400)});

function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()}
function mk(id){if(charts[id]&&!charts[id].isDisposed())charts[id].dispose();var d=document.getElementById(id);if(!d)return null;var c=echarts.init(d,theme==='dark'?'dark':undefined);charts[id]=c;return c}
async function api(url){try{var r=await fetch(url),d=await r.json();return d.status==='success'?d.data:null}catch(e){console.error(e);return null}}
function md(t){return typeof marked!=='undefined'&&marked.parse?marked.parse(t):t.replace(/\n/g,'<br>')}
function fillSels(){
  ['cs1','cs2','cs3','ops','ds'].forEach(function(id){
    var el=document.getElementById(id);
    if(!el)return;
    var f=el.options[0];
    el.innerHTML='';
    el.appendChild(f);
    spots.forEach(function(s){
      var o=document.createElement('option');
      o.value=s;
      o.textContent=s;
      el.appendChild(o);
    });
  });
  initCmpSelector();
}

// 初始化对比选择器
function initCmpSelector(){
  cmpSelectedSpots = ['', '', ''];
  for(var i=0;i<3;i++){
    var img = document.getElementById('cmpImg'+i);
    if(img) img.src = '/static/景点照片/spot' + (i+1) + '.png';
    var name = document.getElementById('cmpName'+i);
    if(name) name.textContent = i<2 ? '选择景点'+(i+1) : '选择景点3（可选）';
    var meta = document.getElementById('cmpMeta'+i);
    if(meta) meta.textContent = '-';
    var card = document.querySelectorAll('.cmp-pick-card')[i];
    if(card) card.classList.remove('filled');
  }
  refreshCmpSelectOptions();
  updateCmpActionBtn();
}

// 防重复：刷新所有下拉的可选项
function refreshCmpSelectOptions(){
  ['cs1','cs2','cs3'].forEach(function(id, idx){
    var sel = document.getElementById(id);
    if(!sel) return;
    var currentVal = cmpSelectedSpots[idx];
    var firstOption = sel.options[0];
    sel.innerHTML = '';
    sel.appendChild(firstOption);
    spots.forEach(function(s){
      var o = document.createElement('option');
      o.value = s;
      o.textContent = s;
      // 如果别的选了，禁用
      if(cmpSelectedSpots.indexOf(s) >= 0 && s !== currentVal){
        o.disabled = true;
        o.textContent = s + ' （已选）';
      }
      sel.appendChild(o);
    });
    if(currentVal) sel.value = currentVal;
  });
}

// 切换某个景点选择
function onCmpSpotChange(idx, spotName){
  cmpSelectedSpots[idx] = spotName;

  // 更新卡片显示
  var card = document.querySelectorAll('.cmp-pick-card')[idx];
  var img = document.getElementById('cmpImg'+idx);
  var name = document.getElementById('cmpName'+idx);
  var meta = document.getElementById('cmpMeta'+idx);

  if(spotName){
    if(card) card.classList.add('filled');
    if(img && SPOT_IMAGES[spotName]) img.src = SPOT_IMAGES[spotName];
    if(name) name.textContent = spotName;
    // 找数据
    var r = rankData.find(function(d){ return d.spot_name === spotName });
    if(meta){
      if(r){
        meta.textContent = '⭐ ' + r.avg_score + ' · ' + r.comment_count.toLocaleString() + ' 条评论';
      } else {
        meta.textContent = '加载中...';
      }
    }
  } else {
    if(card) card.classList.remove('filled');
    if(img) img.src = '/static/景点照片/spot' + (idx+1) + '.png';
    if(name) name.textContent = idx<2 ? '选择景点'+(idx+1) : '选择景点3（可选）';
    if(meta) meta.textContent = '-';
  }

  refreshCmpSelectOptions();
  updateCmpActionBtn();
}

// 更新对比按钮状态
function updateCmpActionBtn(){
  var btn = document.getElementById('cmpActionBtn');
  if(!btn) return;
  var filled = cmpSelectedSpots.filter(function(s){ return s }).length;
  btn.disabled = filled < 2;
}
window.addEventListener('resize',function(){
  Object.values(charts).forEach(function(c){if(c&&!c.isDisposed())c.resize()});
  syncVoiceHeight();   // 窗口变化时也同步
});
function switchPage(name, el){
  document.querySelectorAll('.nav-btn').forEach(function(c){c.classList.remove('active')});
  document.querySelectorAll('.page').forEach(function(p){p.classList.remove('on')});
  if(el)el.classList.add('active');
  else{var btn=document.querySelector('.nav-btn[data-p="'+name+'"]');if(btn)btn.classList.add('active')}
  var pg=document.getElementById('p-'+name);if(pg)pg.classList.add('on');
  setTimeout(function(){Object.values(charts).forEach(function(c){if(c&&!c.isDisposed())c.resize()})},100);

  if(name==='operation')loadOp();
  if(name==='prediction')loadPredictionDetail();
  if(name==='rankingsFull' && rankData && rankData.length){
    renderFullRankings(rankData,window._lastOverview);
    setTimeout(initRankingsFullPage, 100);
  }

  // ✨ 新增：控制底部行动栏显示
  var actionBar = document.getElementById('planActionBar');
  if(actionBar){
    actionBar.style.display = (name === 'plan') ? 'flex' : 'none';
  }

  var t=document.querySelector('.content-area');
  if(t)window.scrollTo({top:t.offsetTop-64,behavior:'smooth'});
}
function goHome(){window.scrollTo({top:0,behavior:'smooth'});switchPage('rankings')}
// 导航栏搜索框展开/收起
function toggleTopbarSearch(){
  var input=document.getElementById('searchInput');
  if(!input)return;
  if(input.classList.contains('expanded')){
    collapseTopbarSearch();
  } else {
    input.classList.add('expanded');
    input.classList.remove('ts-input-collapsed');
    setTimeout(function(){input.focus()},50);
  }
}
function collapseTopbarSearch(){
  var input=document.getElementById('searchInput');
  if(!input)return;
  if(input.value)return;  // 有内容就不收起
  input.classList.remove('expanded');
  input.classList.add('ts-input-collapsed');
  var box=document.getElementById('searchResults');
  if(box)box.classList.remove('show');
}

// Banner搜索
function onHeroSearch(val){
  var box=document.getElementById('heroSearchResults');
  if(!val||val.trim().length===0){box.classList.remove('show');return}
  var keyword=val.trim();
  var matched=spots.filter(function(s){return s.includes(keyword)});
  var html='';
  if(matched.length>0){
    html=matched.map(function(s){
      var r=rankData.find(function(d){return d.spot_name===s});
      return '<div class="search-item" onclick="heroSearchSelect(\''+s+'\')"><span>🏔️</span><span>'+s+'</span><span class="si-score">'+(r?r.avg_score+'⭐':'')+'</span></div>';
    }).join('');
  } else {
    html='<div style="padding:20px;text-align:center"><div style="font-size:24px;margin-bottom:8px;opacity:.5">🔍</div><div style="font-size:12px;color:#64748b">未找到"<span style="color:#3b82f6">'+keyword+'</span>"</div></div>';
  }
  box.innerHTML=html;
  box.classList.add('show');
}
function heroSearchSelect(n){
  document.getElementById('heroSearchResults').classList.remove('show');
  document.getElementById('heroSearchInput').value='';
  var ds=document.getElementById('ds');if(ds)ds.value=n;
  switchPage('detail');loadDetail();
}
function doHeroSearch(){
  var v=document.getElementById('heroSearchInput').value.trim();
  if(!v)return;
  if(spots.includes(v)){heroSearchSelect(v);return}
  var matched=spots.filter(function(s){return s.includes(v)});
  if(matched.length===1){heroSearchSelect(matched[0]);return}
  onHeroSearch(v);
}
document.addEventListener('click',function(e){
  if(!e.target.closest('.hero-search'))document.getElementById('heroSearchResults').classList.remove('show');
});
function onSearch(val){var box=document.getElementById('searchResults');if(!val||val.trim().length===0){box.classList.remove('show');return}var keyword=val.trim();var matched=spots.filter(function(s){return s.includes(keyword)});var html='';if(matched.length>0){html=matched.map(function(s){var r=rankData.find(function(d){return d.spot_name===s});return '<div class="search-item" onclick="searchSelect(\''+s+'\')"><span>🏔️</span><span>'+s+'</span><span class="si-score">'+(r?r.avg_score+'⭐':'')+'</span></div>'}).join('')}else{html='<div style="padding:20px 18px;text-align:center"><div style="font-size:28px;margin-bottom:10px;opacity:.5">🔍</div><div style="font-size:13px;color:var(--t1);font-weight:600;margin-bottom:8px">找不到与"<span style="color:var(--blue)">'+keyword+'</span>"相符的景点</div><div style="font-size:11px;color:var(--t3);line-height:1.8;text-align:left;padding:0 8px">建议：<br>· 请检查输入有无错误<br>· 请尝试景点全称或部分名称</div><div style="margin-top:12px;font-size:11px;color:var(--t3)">当前共 <span style="color:var(--blue);font-weight:600">'+spots.length+'</span> 个景点</div></div>'}box.innerHTML=html;box.classList.add('show')}
function searchSelect(n){document.getElementById('searchResults').classList.remove('show');document.getElementById('searchInput').value='';var ds=document.getElementById('ds');if(ds)ds.value=n;switchPage('detail');loadDetail()}
function doSearch(){var v=document.getElementById('searchInput').value.trim();if(!v)return;if(spots.includes(v)){searchSelect(v);return}var matched=spots.filter(function(s){return s.includes(v)});if(matched.length===1){searchSelect(matched[0]);return}onSearch(v)}
document.addEventListener('click',function(e){if(!e.target.closest('.topbar-search'))document.getElementById('searchResults').classList.remove('show')});
function animateNumber(el,target,dur){dur=dur||1200;var st=performance.now();function up(now){var p=Math.min((now-st)/dur,1);el.textContent=Math.floor(target*(1-Math.pow(1-p,3))).toLocaleString();if(p<1)requestAnimationFrame(up);else el.textContent=target.toLocaleString()}requestAnimationFrame(up)}
async function switchEngine(engine){await api('/api/set_engine?engine='+engine)}
async function syncEngine(){var data=await api('/api/current_engine');if(data){var sel=document.getElementById('aiEngine');if(sel)sel.value=data.engine}}
function aiBadge(data){return data.source==='ai'?'<span class="ai-badge badge-ai">🤖 '+(data.engine||'AI')+'</span>':'<span class="ai-badge badge-local">📊 '+(data.engine||'本地')+'</span>'}
var tt={backgroundColor:'rgba(20,27,45,.9)',borderColor:'rgba(255,255,255,.1)',textStyle:{color:'#eef0ff'}};

function toggleTheme(){var saved={};['ds','ps','cs1','cs2','cs3','ops','wcs','wct','aiEngine'].forEach(function(id){var el=document.getElementById(id);if(el)saved[id]=el.value});var curPage='rankings';var ab=document.querySelector('.nav-btn.active');if(ab&&ab.dataset&&ab.dataset.p)curPage=ab.dataset.p;theme=theme==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',theme);localStorage.setItem('theme',theme);createParticles();Object.keys(charts).forEach(function(k){if(charts[k]&&!charts[k].isDisposed())charts[k].dispose();delete charts[k]});loadRankings().then(function(){setTimeout(function(){Object.entries(saved).forEach(function(pair){var el=document.getElementById(pair[0]);if(el&&pair[1])el.value=pair[1]});if(curPage==='wordcloud')loadWC();if(curPage==='detail'&&saved['ds'])loadDetail();if(curPage==='comparison'&&saved['cs1']&&saved['cs2'])loadCmp();if(curPage==='operation')loadOp();switchPage(curPage)},200)})}

async function loadOverviewData(){var d=await api('/api/overview');if(!d)return null;spots=d.spots_list;fillSels();return d}

// 热度图
async function loadHeatBar(){
  var data=await api('/api/heatmap');
  if(!data) return;
  renderHeatChart(data);

  var range=await api('/api/date_range');
  if(range){
    var ds=document.getElementById('heatDateStart');
    var de=document.getElementById('heatDateEnd');
    if(ds&&range.min) ds.value=range.min;
    if(de&&range.max) de.value=range.max;
  }

  updateSliderUI(0);
}
function renderHeatChart(data){var c=mk('ch3');if(!c)return;var sp=data.slice(0,20).reverse();c.setOption({backgroundColor:'transparent',tooltip:{trigger:'axis',axisPointer:{type:'shadow'},backgroundColor:tt.backgroundColor,borderColor:tt.borderColor,textStyle:tt.textStyle,formatter:function(p){return '<b>'+p[0].name+'</b><br/>热度:'+p[0].value+'<br/><span style="font-size:11px;color:#888">点击查看趋势</span>'}},grid:{left:'18%',right:'13%',top:'3%',bottom:'3%'},xAxis:{type:'value',axisLabel:{color:css('--t2')},splitLine:{lineStyle:{color:css('--border')}}},yAxis:{type:'category',data:sp.map(function(s){return s.spot_name}),axisLabel:{color:css('--t1'),fontSize:12}},series:[{type:'bar',data:sp.map(function(s){return{value:s.heat,itemStyle:{color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:css('--purple')},{offset:1,color:css('--blue')}]),borderRadius:[0,8,8,0]}}}),barWidth:'55%',label:{show:true,position:'right',color:css('--blue'),fontSize:12,fontWeight:'bold'},cursor:'pointer'}]});c.off('click');c.on('click',function(params){if(params.name)goDetail(params.name)})}
function updatePlane(){
  var slider = document.getElementById('timeSlider');
  var plane = document.getElementById('sliderPlane');
  if(!slider || !plane) return;

  var min = parseFloat(slider.min || 0);
  var max = parseFloat(slider.max || 4);
  var val = parseFloat(slider.value || 0);

  var percent = ((val - min) / (max - min)) * 100;
  plane.style.left = percent + '%';
}

var TIME_OPTIONS=[
  {label:'全部时间',days:null},
  {label:'近1年',days:365},
  {label:'近6个月',days:180},
  {label:'近3个月',days:90},
  {label:'近1个月',days:30}
];

function updateSliderUI(val){
  val=parseInt(val);
  var plane=document.getElementById('sliderPlane');
  if(plane) plane.style.left=(val/4*100)+'%';

  var ticks=document.querySelectorAll('.slider-tick');
  ticks.forEach(function(t,i){t.classList.toggle('active',i<=val)});

  var dots=document.querySelectorAll('.track-dot');
  dots.forEach(function(d,i){
    d.classList.remove('passed','current');
    if(i<val) d.classList.add('passed');
    if(i===val) d.classList.add('current');
  });

  document.getElementById('timeSliderValue').textContent=TIME_OPTIONS[val].label;
}

async function onTimeSliderChange(val){
  updateSliderUI(val);
  var opt=TIME_OPTIONS[parseInt(val)];
  var url='/api/heat_by_period';
  if(opt.days) url+='?days='+opt.days;
  var data=await api(url);
  if(data) renderHeatChart(data);
}

function clickTick(idx){
  document.getElementById('timeSlider').value=idx;
  onTimeSliderChange(idx);
}

async function onDateRangeApply(){
  var start=document.getElementById('heatDateStart').value;
  var end=document.getElementById('heatDateEnd').value;
  if(!start||!end){alert('请选择起止时间');return}
  document.getElementById('timeSliderValue').textContent=start+' 至 '+end;
  var data=await api('/api/heat_by_period?start='+start+'&end='+end);
  if(data) renderHeatChart(data);
}

function onDateRangeReset(){
  document.getElementById('timeSlider').value=0;
  updateSliderUI(0);
  document.getElementById('heatDateStart').value='';
  document.getElementById('heatDateEnd').value='';
  loadHeatBar();
}
// 排名
async function loadRankings(){
  var overview = await loadOverviewData();
  window._lastOverview = overview;

  // 并行请求双榜数据
  var results = await Promise.all([
    api('/api/dual_rankings?type=hot&mafengwo=33&ctrip=34&dianping=33'),
    api('/api/dual_rankings?type=quality')
  ]);

  var hotData = results[0] || [];
  var qualityData = results[1] || [];

  // 兼容旧字段
  hotData.forEach(function(d){ d.heat_index = d.heat_score });

  // 缓存到全局
  homeHotData = hotData;
  homeQualityData = qualityData;
  rankData = hotData;

  // 5指标卡
  if(overview){
    var sentiment = overview.sentiment_summary || {};
    var posCount = sentiment.positive || 0;
    var totalC = overview.total_comments || 1;
    var posRate = ((posCount / totalC) * 100).toFixed(1);

    // 真实变化数据
    var changes = overview.changes || {};

    function fmtTrend(val, suffix, label){
      suffix = suffix || '';
      label = label || '较上周';
      if(val === undefined || val === null){
        return '<span class="neutral">--</span>';
      }
      if(val === 0){
        return '<span class="neutral">持平</span> ' + label;
      }
      var sign = val > 0 ? '+' : '';
      var cls = val > 0 ? 'up' : 'down';
      return '<span class="' + cls + '">' + sign + val + suffix + '</span> ' + label;
    }

    // 评论新增：显示近7天新增条数（永远是正数）
    var recentCount = changes.recent_count || 0;
    var commentTrend = recentCount > 0
      ? '<span class="up">+' + recentCount.toLocaleString() + '</span> 近7天新增'
      : '<span class="neutral">近期无新增</span>';

    // 评分趋势：近7天评分 vs 之前7天
    var scoreTrend = (changes.score_change !== undefined)
      ? fmtTrend(changes.score_change)
      : '<span class="neutral">数据稳定</span>';

    // 好评率趋势：近7天好评率 vs 之前7天
    var posRateTrend = (changes.pos_rate_change !== undefined)
      ? fmtTrend(changes.pos_rate_change, '%')
      : '<span class="neutral">口碑稳定</span>';

    var metrics = [
      {icon:'🏔️', cls:'metric-icon-blue', label:'景点总数', value:overview.total_spots || 0, trend:'<span class="neutral">已覆盖西安</span>'},
      {icon:'💬', cls:'metric-icon-green', label:'游客评论', value:totalC.toLocaleString(), trend:commentTrend},
      {icon:'⭐', cls:'metric-icon-yellow', label:'平均评分', value:overview.avg_score || '-', trend:scoreTrend},
      {icon:'👍', cls:'metric-icon-purple', label:'好评率', value:posRate + '%', trend:posRateTrend},
      {icon:'📊', cls:'metric-icon-pink', label:'数据维度', value:'12+', trend:'<span class="neutral">多维分析</span>'}
    ];
    var mh = '';
    metrics.forEach(function(m){
      mh += '<div class="metric-card"><div class="metric-icon-wrap ' + m.cls + '">' + m.icon + '</div><div class="metric-info"><div class="metric-label">' + m.label + '</div><div class="metric-value">' + m.value + '</div><div class="metric-trend">' + m.trend + '</div></div></div>';
    });
    var mg = document.getElementById('metricGrid');
    if(mg) mg.innerHTML = mh;
}

  // 根据当前全局 Tab 状态渲染首页
  if(currentRankingMode === 'quality'){
    renderCompactQualityList(qualityData.slice(0, 5));
  } else {
    renderCompactRankList(hotData.slice(0, 5));
  }

  loadHomeDiagnosis();
  loadHotPotential();
  loadDistrictMap();
  renderInsights(hotData, overview);
  renderFullRankings(hotData, overview);
}

function renderCompactRankList(top5){
  var listEl=document.getElementById('rankListCompact');
  if(!listEl)return;
  // 兼容新旧字段：优先用 heat_score（新双榜单字段），fallback 到 heat_index
  function getScore(item){
    return item.heat_score!==undefined ? item.heat_score : item.heat_index;
  }
  var maxScore=top5[0]?getScore(top5[0]):100;
  listEl.innerHTML=top5.map(function(item,i){
    var rk=i+1;
    var rkCls=rk<=3?'r'+rk:'ro';
    var img=SPOT_IMAGES[item.spot_name]||'/static/景点照片/spot1.png';
    var score=getScore(item);
    var pct=(score/maxScore*100).toFixed(0);
    return '<div class="rank-item" onclick="goDetail(\''+item.spot_name+'\')">'
      +'<div class="rank-num '+rkCls+'">'+rk+'</div>'
      +'<div class="rank-thumb"><img src="'+img+'" alt="'+item.spot_name+'" onerror="this.style.display=\'none\'"></div>'
      +'<div class="rank-info"><div class="rank-name">'+item.spot_name+'</div><div class="rank-loc">西安</div></div>'
      +'<div class="rank-score">'+score+'</div>'
      +'<div class="rank-bar-wrap"><div class="rank-bar-fill" style="width:'+pct+'%"></div></div>'
      +'</div>';
  }).join('');
}
// ===== 首页双榜 Tab 切换 =====
function switchHomeRankTab(target, el){
  currentRankingMode = target;

  // Tab 高亮
  var tabs = document.querySelectorAll('.home-rank-tab');
  tabs.forEach(function(t){ t.classList.remove('on') });
  if(el) el.classList.add('on');

  // 渲染对应榜单
  if(target === 'quality'){
    renderCompactQualityList(homeQualityData.slice(0, 5));
  } else {
    renderCompactRankList(homeHotData.slice(0, 5));
  }
}

// ===== 查看全部（带状态跳转）=====
function goToFullRankings(){
  switchPage('rankingsFull');
  // 同步完整页的 Tab 到当前状态
  setTimeout(function(){
    switchDualTab(currentRankingMode);
  }, 150);
}

// ===== 返回首页（保留 Tab 状态）=====
function goBackHome(){
  switchPage('rankings');
  // 同步首页 Tab 高亮
  var tabs = document.querySelectorAll('.home-rank-tab');
  tabs.forEach(function(t){
    t.classList.remove('on');
    if(t.getAttribute('data-target') === currentRankingMode){
      t.classList.add('on');
    }
  });
}
// ===== 首页好评榜紧凑版（TOP5）=====
function renderCompactQualityList(top5){
  var listEl = document.getElementById('rankListCompact');
  if(!listEl) return;

  if(!top5 || !top5.length){
    listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--t3)">暂无数据</div>';
    return;
  }

  var maxScore = top5[0].quality_score || 100;

  listEl.innerHTML = top5.map(function(item, i){
    var rk = i + 1;
    var rkCls = rk <= 3 ? 'r' + rk : 'ro';
    var img = SPOT_IMAGES[item.spot_name] || '/static/景点照片/spot1.png';
    var pct = (item.quality_score / maxScore * 100).toFixed(0);

    return '<div class="rank-item-quality" onclick="goDetail(\'' + item.spot_name + '\')">'
      + '<div class="rank-num ' + rkCls + '">' + rk + '</div>'
      + '<div class="rank-thumb"><img src="' + img + '" alt="' + item.spot_name + '" onerror="this.style.display=\'none\'"></div>'
      + '<div class="rank-info"><div class="rank-name">' + item.spot_name + '</div><div class="rank-loc">⭐ ' + item.avg_score + '</div></div>'
      + '<div class="rank-quality-badge">👍 ' + item.quality_score + '</div>'
      + '<div class="rank-bar-wrap"><div class="rank-bar-fill" style="width:' + pct + '%;background:linear-gradient(90deg,#10b981,#34d399)"></div></div>'
      + '</div>';
  }).join('');
}
// ===== 差评原因 Tooltip（完整排名页好评榜用）=====


// ===== 差评原因 Tooltip（全局浮层版）=====

// 显示 tooltip
async function loadNegTooltip(el, spotName){
  var tip = document.getElementById('globalNegTooltip');
  if(!tip) return;

  // 计算位置：在触发元素下方
  var rect = el.getBoundingClientRect();
  var tipW = 280;

  // 水平位置：尽量居中对齐触发元素，但不超出屏幕
  var left = rect.left + rect.width / 2 - tipW / 2;
  if(left < 10) left = 10;
  if(left + tipW > window.innerWidth - 10) left = window.innerWidth - tipW - 10;

  // 垂直位置：优先向下，空间不够就向上
  var top = rect.bottom + 8;
  if(top + 200 > window.innerHeight){
    top = rect.top - 200;
  }

  tip.style.left = left + 'px';
  tip.style.top = top + 'px';
  tip.classList.add('show');

  // 有缓存直接用
  if(spotNegInsights[spotName]){
    renderNegTooltip(tip, spotName, spotNegInsights[spotName]);
    return;
  }

  tip.innerHTML = '<div class="neg-tooltip-loading">🔍 分析差评原因...</div>';

  // 优先用 AI 洞察
  var data = await api('/api/ai_insight?spot_name=' + encodeURIComponent(spotName));

  if(data && data.improvements && data.improvements.length){
    spotNegInsights[spotName] = data.improvements;
    renderNegTooltip(tip, spotName, data.improvements);
    return;
  }

  // 降级：用失望原因模型
  var negData = await api('/api/negative_model?spot_name=' + encodeURIComponent(spotName) + '&top_n=4');
  if(negData && negData.items && negData.items.length){
    var reasons = negData.items
      .filter(function(d){ return d.impact > 0 })
      .map(function(d){ return d.factor + '（' + d.occurrence_pct + '% 提到）' });
    spotNegInsights[spotName] = reasons;
    renderNegTooltip(tip, spotName, reasons);
    return;
  }

  tip.innerHTML = '<div class="neg-tooltip-title">⚠️ ' + spotName + '</div>'
    + '<div style="color:var(--t3);font-size:11px">暂无差评诊断数据</div>';
}

// 渲染 tooltip 内容
function renderNegTooltip(tipEl, spotName, items){
  var html = '<div class="neg-tooltip-title">⚠️ ' + spotName + ' · 主要问题</div>';
  html += items.slice(0, 4).map(function(item){
    return '<div class="neg-tooltip-item">'
      + '<div class="neg-tooltip-dot"></div>'
      + '<div>' + item + '</div>'
      + '</div>';
  }).join('');
  tipEl.innerHTML = html;
}

// 隐藏 tooltip
function hideNegTooltip(){
  var tip = document.getElementById('globalNegTooltip');
  if(tip) tip.classList.remove('show');
}
function renderFullRankings(data, overview){
  // 根据当前榜单模式决定数据源
  var sortedData;
  if(currentRankingMode === 'quality' && homeQualityData.length){
    sortedData = homeQualityData;
  } else {
    sortedData = (data && data.length) ? data : homeHotData;
  }
  if(!sortedData || !sortedData.length) return;

  var top6 = sortedData.slice(0, 6);

  function getScore(item){
    if(currentRankingMode === 'quality') return item.quality_score || 0;
    return item.heat_score || item.heat_index || 0;
  }

  function buildCard(item, i){
    var rk = i + 1;
    var rkC = rk <= 3 ? 'cc-rk' + rk : 'cc-rko';
    var img = SPOT_IMAGES[item.spot_name] || '/static/景点照片/spot1.png';
    var score = getScore(item);
    var avgScore = item.avg_score || 0;
    var stars = '';
    for(var j = 0; j < 5; j++){
      stars += '<span class="star' + (j < Math.round(avgScore) ? '' : ' off') + '">'
        + (j < Math.round(avgScore) ? '★' : '☆') + '</span>';
    }

    var scoreLabel, extraInfo;
    if(currentRankingMode === 'quality'){
      scoreLabel = '👍 ';
      extraInfo = '<div>好评 <span class="cs-val" style="color:var(--green)">' + (item.positive_rate || 0) + '%</span></div>'
        + '<div>差评 <span class="cs-val" style="color:var(--red)">' + (item.negative_rate || 0) + '%</span></div>';
    } else {
      scoreLabel = '🔥 ';
      extraInfo = '<div>好评率 <span class="cs-val" style="color:var(--green)">' + (item.positive_rate || 0) + '%</span></div>';
    }

    return '<div class="carousel-card" onclick="goDetail(\'' + item.spot_name + '\')">'
      + '<img class="cc-img" src="' + img + '" alt="' + item.spot_name + '">'
      + '<div class="cc-body">'
      + '<div class="cc-top-row"><span class="cc-rank ' + rkC + '">#' + rk + '</span>'
      + '<span class="cc-heat">' + scoreLabel + score + '</span></div>'
      + '<div class="cc-name">' + item.spot_name + '</div>'
      + '<div class="cc-stars">' + stars + '</div>'
      + '<div class="cc-stats">'
      + '<div>评论 <span class="cs-val">' + (item.comment_count || 0).toLocaleString() + '</span></div>'
      + extraInfo
      + '<div>均分 <span class="cs-val">' + avgScore + '</span></div>'
      + '</div></div></div>';
  }

  // 3份循环滚动
  var cards = '';
  top6.forEach(function(item, i){ cards += buildCard(item, i) });
  top6.forEach(function(item, i){ cards += buildCard(item, i) });
  top6.forEach(function(item, i){ cards += buildCard(item, i) });

  var ca = document.getElementById('carousel-area');
  if(ca){
    ca.innerHTML = '<div class="carousel-section"><div class="carousel-wrap">'
      + '<div class="carousel-track" id="carouselTrack">' + cards + '</div>'
      + '</div><div class="carousel-hint">← 拖动浏览 →</div></div>';
  }

  setTimeout(initCarousel, 200);
  loadHeatBar();
}
function initCarousel(){var track=document.getElementById('carouselTrack');if(!track)return;var cw=360,total=6;track.scrollLeft=cw*total+(cw*total/2)-(track.offsetWidth/2);var isDrag=false,startX,scrollS;track.addEventListener('scroll',function(){if(track.scrollLeft>=cw*total*2){track.style.scrollBehavior='auto';track.scrollLeft-=cw*total;track.style.scrollBehavior='smooth'}else if(track.scrollLeft<=cw*total*0.3){track.style.scrollBehavior='auto';track.scrollLeft+=cw*total;track.style.scrollBehavior='smooth'}updateCards(track)});track.addEventListener('mousedown',function(e){isDrag=true;startX=e.pageX;scrollS=track.scrollLeft;track.style.scrollBehavior='auto'});track.addEventListener('mousemove',function(e){if(!isDrag)return;e.preventDefault();track.scrollLeft=scrollS-(e.pageX-startX)*1.5});track.addEventListener('mouseup',function(){isDrag=false;track.style.scrollBehavior='smooth'});track.addEventListener('mouseleave',function(){isDrag=false;track.style.scrollBehavior='smooth'});track.addEventListener('touchstart',function(e){startX=e.touches[0].pageX;scrollS=track.scrollLeft;track.style.scrollBehavior='auto'},{passive:true});track.addEventListener('touchmove',function(e){track.scrollLeft=scrollS-(e.touches[0].pageX-startX)*1.5},{passive:true});track.addEventListener('touchend',function(){track.style.scrollBehavior='smooth'});updateCards(track)}
function updateCards(track){var cards=track.querySelectorAll('.carousel-card');var center=track.scrollLeft+track.offsetWidth/2;cards.forEach(function(card){var cc=card.offsetLeft+card.offsetWidth/2;var dist=Math.abs(cc-center);card.classList.remove('center','near');if(dist<160)card.classList.add('center');else if(dist<500)card.classList.add('near')})}
function goDetail(n){var ds=document.getElementById('ds');if(ds)ds.value=n;switchPage('detail');loadDetail()}
async function loadHomeDiagnosis(){
  var listEl=document.getElementById('homeDiagList');
  var metaEl=document.getElementById('homeDiagMeta');
  if(!listEl)return;

  // 同时拿两个数据：基础影响分 + 时序趋势
  var negData=await api('/api/negative_model?top_n=5');
  var trendData=await api('/api/factor_trend_simple?days=30');

  if(!negData||!negData.items||!negData.items.length){
    listEl.innerHTML='<div style="text-align:center;padding:30px;color:var(--t3)">暂无诊断数据</div>';
    return;
  }

  var summary=negData.summary||{};
  if(metaEl){
    var trendInfo=trendData?' · 近30天痛点变化已分析':'';
    metaEl.textContent='基于 '+summary.sample_size+' 条评论 · 线性回归模型'+trendInfo;
  }

  var items=negData.items.filter(function(d){return d.impact>0}).slice(0,5);
  if(!items.length){
    listEl.innerHTML='<div style="text-align:center;padding:30px;color:var(--green)">✓ 当前未检测到显著问题</div>';
    return;
  }

  // 构建 factor -> trend 映射
  var trendMap={};
  if(trendData&&trendData.items){
    trendData.items.forEach(function(t){
      trendMap[t.factor]=t;
    });
  }

  var maxImpact=Math.max.apply(null,items.map(function(d){return d.impact}));
  listEl.innerHTML=items.map(function(d,i){
    var cls=i===0?'':'p'+i;
    var pct=(d.impact/maxImpact*100).toFixed(0);
    var trend=trendMap[d.factor];

    // 趋势箭头
    var trendHtml='';
    if(trend){
      if(trend.trend==='up'){
        trendHtml='<span class="diag-trend up" title="近30天出现率：'+trend.recent_rate+'%（全时段：'+trend.all_rate+'%）">↑ +'+trend.change+'%</span>';
      } else if(trend.trend==='down'){
        trendHtml='<span class="diag-trend down" title="近30天出现率：'+trend.recent_rate+'%（全时段：'+trend.all_rate+'%）">↓ '+trend.change+'%</span>';
      } else {
        trendHtml='<span class="diag-trend flat" title="出现率稳定">— 稳定</span>';
      }
    }

    return '<div class="diagnosis-item">'
      +'<div class="diag-row">'
      +'<span class="diag-tag '+cls+'">P'+i+'</span>'
      +'<span class="diag-name">'+d.factor+'</span>'
      +trendHtml
      +'<span class="diag-coef">影响 '+d.impact+'</span>'
      +'</div>'
      +'<div class="diag-bar-wrap"><div class="diag-bar-fill" style="width:'+pct+'%"></div></div>'
      +'<div class="diag-meta">'+d.occurrence_pct+'% 的评论提到 · β系数 '+d.coef+'</div>'
      +'</div>';
  }).join('');
}

// ===== 首页：热度爆发预测 =====
async function loadHotPotential(){
  var listEl=document.getElementById('potentialList');
  if(!listEl)return;

  var data=await api('/api/hot_potential?top_n=5');
  if(!data||!data.length){
    listEl.innerHTML='<div style="text-align:center;padding:30px;color:var(--t3)">暂无预测数据</div>';
    return;
  }

  // 更新副标题为真实日期
  var subtitleEl = document.querySelector('.potential-head .potential-subtitle');
  if(subtitleEl && dataMaxDate){
    subtitleEl.innerHTML = '基于数据 '+dataMaxDate+' · 预测未来7天';
  }

  listEl.innerHTML=data.map(function(item,i){
    var img=SPOT_IMAGES[item.spot_name]||'/static/景点照片/spot1.png';
    var growthSign=item.growth_rate>=0?'+':'';
    return '<div class="potential-item" onclick="switchPage(\'prediction\')">'
      +'<div class="potential-thumb"><img src="'+img+'" alt="'+item.spot_name+'" onerror="this.style.display=\'none\'"></div>'
      +'<div class="potential-info">'
      +'<div class="potential-name">'+item.spot_name+'</div>'
      +'<div class="potential-score-row">'
      +'<span class="potential-score">'+item.potential_score+'</span>'
      +'<span class="potential-score-label">爆发指数</span>'
      +'</div>'
      +'<div class="potential-growth">预计热度 '+growthSign+item.growth_rate+'%</div>'
      +'</div>'
      +'<div class="potential-chart" id="potChart'+i+'"></div>'
      +'</div>';
  }).join('');

  // 渲染每个小折线图
  setTimeout(function(){
    data.forEach(function(item,i){
      renderMiniChart('potChart'+i, item.history_data, item.forecast_data);
    });
  },100);
}

function renderMiniChart(id, history, forecast){
  var c=mk(id);
  if(!c)return;
  var allData=history.concat(forecast);
  var splitLine=history.length-1;

  c.setOption({
    backgroundColor:'transparent',
    grid:{left:0,right:0,top:5,bottom:5,containLabel:false},
    xAxis:{type:'category',show:false,data:allData.map(function(_,i){return i})},
    yAxis:{type:'value',show:false},
    series:[
      {
        type:'line',
        data:history.concat(forecast.map(function(){return null})),
        smooth:true,
        symbol:'none',
        lineStyle:{color:'#3b82f6',width:2},
        areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(59,130,246,.3)'},{offset:1,color:'rgba(59,130,246,0)'}])}
      },
      {
        type:'line',
        data:history.map(function(){return null}).concat(forecast),
        smooth:true,
        symbol:'none',
        lineStyle:{color:'#8b5cf6',width:2,type:'dashed'}
      }
    ]
  });
}

// ===== 预测详情页 =====
async function loadPredictionDetail(){
  var listEl=document.getElementById('predictionDetailList');
  if(!listEl)return;
  listEl.innerHTML='<div class="loading"><div class="spinner"></div>加载预测数据...</div>';

  var topData=await api('/api/hot_potential?top_n=5');
  if(!topData||!topData.length){
    listEl.innerHTML='<div style="text-align:center;padding:60px;color:var(--t3)">暂无预测数据</div>';
    return;
  }

  var html='';
  for(var i=0;i<topData.length;i++){
    var item=topData[i];
    // 用各景点自己的最新日期
    var spotDate = item.base_date || dataMaxDate;
    var dateHint = spotDate ? '📅 数据更新至 ' + spotDate : '';
    html+='<div class="prediction-detail-card" id="pdCard_'+i+'">'
      +'<div class="pd-head">'
      +'<div class="pd-rank">#'+(i+1)+'</div>'
      +'<div style="flex:1">'
      +'<div class="pd-name">'+item.spot_name+'</div>'
      +'<div class="pd-score-line">爆发指数 <strong>'+item.potential_score+'</strong> · 预计热度 <strong style="color:'+(item.growth_rate>=0?'#10b981':'#ef4444')+'">'+(item.growth_rate>=0?'+':'')+item.growth_rate+'%</strong></div>'
      +'</div>'
      +(dateHint ? '<div style="font-size:11px;color:var(--t3);background:var(--bg2);padding:5px 12px;border-radius:6px;align-self:flex-start;white-space:nowrap">'+dateHint+'</div>' : '')
      +'</div>'
      +'<div id="pdContent_'+i+'"><div class="loading"><div class="spinner"></div>加载详情...</div></div>'
      +'</div>';

  }
  listEl.innerHTML=html;

  // 异步加载每个景点的详情
  for(var i=0;i<topData.length;i++){
    await loadOneDetail(i, topData[i].spot_name);
  }
}

async function loadOneDetail(idx, spotName){
  var data=await api('/api/hot_potential_detail?spot_name='+encodeURIComponent(spotName));
  var container=document.getElementById('pdContent_'+idx);
  if(!container)return;
  if(!data){
    container.innerHTML='<p style="color:var(--t3);text-align:center;padding:20px">加载失败</p>';
    return;
  }

  var html='<div class="pd-horizontal-layout">'

    // 左：关键指标
    +'<div class="pd-col pd-col-metrics">'
    +'<div class="pd-col-title">📊 关键指标</div>'
    +'<div class="pd-metric-stack">'
    +'<div class="pd-metric-row"><div class="pd-metric-val">'+data.recent_count+'</div><div class="pd-metric-label">近30天评论 <span class="pd-metric-change '+(data.count_growth>=0?'up':'down')+'">'+(data.count_growth>=0?'+':'')+data.count_growth+'%</span></div></div>'
    +'<div class="pd-metric-row"><div class="pd-metric-val">'+data.recent_avg_score+'</div><div class="pd-metric-label">近30天评分 <span class="pd-metric-change '+(data.score_change>=0?'up':'down')+'">'+(data.score_change>=0?'+':'')+data.score_change+'</span></div></div>'
    +'<div class="pd-metric-row"><div class="pd-metric-val">'+data.predicted_7d_count+'</div><div class="pd-metric-label">预计未来7天评论</div></div>'
    +'</div></div>'

    // 中：趋势曲线
    +'<div class="pd-col pd-col-chart">'
    +'<div class="pd-col-title">📈 趋势预测</div>'
    +'<div class="pd-chart" id="pdChart_'+idx+'"></div>'
    +'<div class="pd-chart-legend">实线：历史 · 虚线：预测</div>'
    +'</div>'

    // 右：上涨关键词
    +'<div class="pd-col pd-col-keywords">'
    +'<div class="pd-col-title">🔍 爆发原因</div>'
    +'<div class="pd-keywords-list">';

  if(data.rising_keywords&&data.rising_keywords.length){
    data.rising_keywords.slice(0,6).forEach(function(kw){
      var newCls=kw.is_new?'new':'';
      html+='<div class="pd-keyword-row '+newCls+'">'
        +'<div class="pd-kw-info"><div class="pd-kw-name">'+kw.word+'</div><div class="pd-kw-meta">'+kw.current_count+' 次提及</div></div>'
        +'<div class="pd-kw-change '+newCls+'">'+kw.change_pct+'</div>'
        +'</div>';
    });
  } else {
    html+='<div style="text-align:center;padding:20px;color:var(--t3);font-size:12px">暂无显著上涨关键词</div>';
  }

  html+='</div></div></div>';
  container.innerHTML=html;

  setTimeout(function(){
    renderDetailChart('pdChart_'+idx, data.history_data, data.forecast_data, data.base_date);
  },100);
}

function renderDetailChart(id, history, forecast, spotBaseDate){
  var c=mk(id);
  if(!c)return;

  // 优先用该景点自己的最新日期
  var baseDate;
  if(spotBaseDate){
    baseDate = new Date(spotBaseDate);
  } else if(dataMaxDate){
    baseDate = new Date(dataMaxDate);
  } else {
    baseDate = new Date();
  }

  function fmtShort(d){
    return (d.getMonth()+1) + '/' + d.getDate();
  }

  var historyDates = [];
  var forecastDates = [];
  for(var i=29; i>=0; i--){
    var d = new Date(baseDate);
    d.setDate(d.getDate() - i);
    historyDates.push(fmtShort(d));
  }
  for(var j=1; j<=7; j++){
    var d = new Date(baseDate);
    d.setDate(d.getDate() + j);
    forecastDates.push(fmtShort(d));
  }
  var allDates = historyDates.concat(forecastDates);

  var baseLabel = baseDate.getFullYear()+'-'+String(baseDate.getMonth()+1).padStart(2,'0')+'-'+String(baseDate.getDate()).padStart(2,'0');

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{
      trigger:'axis',
      backgroundColor:tt.backgroundColor,
      borderColor:tt.borderColor,
      textStyle:tt.textStyle,
      formatter:function(params){
        var idx = params[0].dataIndex;
        var label = idx < 30 ? '历史' : '预测';
        var dateStr = allDates[idx];
        var html = '<b>' + label + ' · ' + dateStr + '</b><br/>';
        params.forEach(function(p){
          if(p.value !== null && p.value !== undefined){
            html += p.marker + ' ' + p.seriesName + ': ' + p.value + '<br/>';
          }
        });
        return html;
      }
    },
    grid:{left:'5%',right:'5%',top:'18%',bottom:'18%'},
    legend:{data:['历史评论量','预测评论量'],textStyle:{color:css('--t2')},top:0},
    xAxis:{
      type:'category',
      data:allDates,
      axisLabel:{
        color:css('--t2'),
        fontSize:10,
        interval: 3
      }
    },
    yAxis:{type:'value',axisLabel:{color:css('--t2')},splitLine:{lineStyle:{color:css('--border')}}},
    series:[
      {
        name:'历史评论量',type:'line',
        data:history.concat(forecast.map(function(){return null})),
        smooth:true,
        lineStyle:{color:'#3b82f6',width:2.5},
        itemStyle:{color:'#3b82f6'},
        areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(59,130,246,.2)'},{offset:1,color:'rgba(59,130,246,0)'}])}
      },
      {
        name:'预测评论量',type:'line',
        data:history.map(function(){return null}).concat(forecast),
        smooth:true,
        lineStyle:{color:'#8b5cf6',width:2.5,type:'dashed'},
        itemStyle:{color:'#8b5cf6'}
      },
      {
        type:'line',
        markLine:{
          silent:true,
          symbol:'none',
          data:[{xAxis:30}],
          lineStyle:{color:'#94a3b8',type:'dashed',width:1.5},
          label:{
            formatter:'最新数据 ' + baseLabel.substring(5),
            color:css('--t2'),
            fontSize:11,
            position:'insideEndTop'
          }
        }
      }
    ]
  });
}
async function loadDistrictMap(){
  var geoResp=await api('/api/xian_geojson');
  if(!geoResp){var el=document.getElementById('districtMap');if(el)el.innerHTML='<div style="text-align:center;padding:60px;color:var(--t3)">地图数据加载失败</div>';return}
  var heatData=await api('/api/district_heat');
  if(!heatData)heatData=[];

  echarts.registerMap('xian', geoResp);

  var c=mk('districtMap');if(!c)return;
  var maxV=Math.max.apply(null,heatData.map(function(d){return d.value}).concat([1]));

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{
      trigger:'item',
      backgroundColor:tt.backgroundColor,
      borderColor:tt.borderColor,
      textStyle:tt.textStyle,
      formatter:function(p){
        if(!p.data) return '<b>'+p.name+'</b><br/>暂无景点数据';
        var spotsList=p.data.spots?p.data.spots.map(function(s){return '· '+s.name+' ('+s.score+'分)'}).join('<br/>'):'';
        return '<b>'+p.name+'</b><br/>'
          +'综合热度：'+p.data.value+'<br/>'
          +'景点数：'+p.data.spot_count+'<br/>'
          +'评论数：'+p.data.comment_count.toLocaleString()+'<br/>'
          +'<br/>包含景点：<br/>'+spotsList;
      }
    },
    visualMap:{
      show:false,
      min:0,
      max:maxV,
      inRange:{color:['#bfdbfe','#93c5fd','#60a5fa','#3b82f6','#1d4ed8']}
    },
            series:[{
      type:'map',
      map:'xian',
      roam:false,
      label:{
        show:true,
        fontSize:11,
        color:'#1e40af',
        fontWeight:'bold',
        // 关键：通过 formatter 控制哪些区显示名字
        formatter:function(params){
          // 只显示这些大区的名字
          var bigDistricts=['雁塔区','未央区','长安区','灞桥区','鄠邑区','阎良区','临潼区','高陵区','周至县','蓝田县'];
          if(bigDistricts.indexOf(params.name)>=0) return params.name;
          return '';
        }
      },
      itemStyle:{
        borderColor:'#94a3b8',
        borderWidth:1.2,
        areaColor:'#dbeafe'
      },
      emphasis:{
        label:{show:true,color:'#1e3a8a',fontWeight:'bold',fontSize:13},
        itemStyle:{
          areaColor:'#3b82f6',
          borderColor:'#1e40af',
          borderWidth:2,
          shadowBlur:10,
          shadowColor:'rgba(59,130,246,.3)'
        }
      },
      data:heatData
    }]
  });

  // 渲染右侧排名列表
  renderDistrictRankList(heatData);
}
function renderDistrictRankList(data){
  var listEl=document.getElementById('districtRankList');
  if(!listEl)return;
  // 按热度排序
  var sorted=data.slice().sort(function(a,b){return b.value-a.value});
  listEl.innerHTML=sorted.map(function(d,i){
    var rk=i+1;
    var rkCls=rk<=3?'r'+rk:'ro';
    return '<div class="dist-rank-item">'
      +'<div class="dist-rank-num '+rkCls+'">'+rk+'</div>'
      +'<div class="dist-rank-name">'+d.name+'</div>'
      +'<div class="dist-rank-val">'+d.value+'</div>'
      +'</div>';
  }).join('');
}
// 词云
async function loadWC(){
  var sp=document.getElementById('wcs').value;
  var st=document.getElementById('wct').value;
  var url='/api/wordcloud?';
  if(sp) url+='spot_name='+encodeURIComponent(sp)+'&';
  if(st) url+='sentiment='+st;

  var d=await api(url);
  if(d&&d.length) mkW('wc0',d);

  var pos=await api('/api/wordcloud?'+(sp?'spot_name='+encodeURIComponent(sp)+'&':'')+'sentiment=positive');
  var neg=await api('/api/wordcloud?'+(sp?'spot_name='+encodeURIComponent(sp)+'&':'')+'sentiment=negative');

  if(pos&&pos.length) mkW('wc1',pos);
  if(neg&&neg.length) mkW('wc2',neg);

  // 情感热力图也跟着景点变化
  loadKeywordSentimentChart();
}
function mkW(id,data){var c=mk(id);if(!c)return;var pool=theme==='dark'?['#60a5fa','#3b82f6','#2563eb','#7dd3fc','#0ea5e9','#38bdf8','#818cf8','#6366f1']:['#3b82f6','#2563eb','#1d4ed8','#0ea5e9','#0284c7','#6366f1','#4f46e5','#1e40af'];c.setOption({backgroundColor:'transparent',tooltip:{show:true,formatter:function(p){return p.name+': '+p.value+'次'},backgroundColor:tt.backgroundColor,borderColor:tt.borderColor,textStyle:tt.textStyle},series:[{type:'wordCloud',shape:'circle',left:'center',top:'center',width:'90%',height:'90%',sizeRange:[14,54],rotationRange:[-45,45],rotationStep:15,gridSize:8,textStyle:{fontFamily:'Microsoft YaHei',fontWeight:'bold',color:function(){return pool[Math.floor(Math.random()*pool.length)]}},data:data.map(function(d){return{name:d.name,value:d.value}})}]})}

// 深度分析
async function loadAIKW(s){
  var posBox=document.getElementById('voicePos');
  var negBox=document.getElementById('voiceNeg');
  if(!posBox||!negBox)return;

  var data=await api('/api/ai_keywords?spot_name='+encodeURIComponent(s));
  if(!data){
    if(posBox) posBox.innerHTML='<div class="hi-loading" style="color:var(--red)">加载失败</div>';
    if(negBox) negBox.innerHTML='<div class="hi-loading" style="color:var(--red)">加载失败</div>';
    return;
  }

  // 12 张头像
  function getAvatar(idx){
    return '/static/游客头像/'+idx+'.jpg';
  }

  // 基于景点名的固定洗牌（同景点每次刷新分配方案稳定）
  function shuffle12(seed){
    var arr=[1,2,3,4,5,6,7,8,9,10,11,12];
    var s=0;
    for(var i=0;i<seed.length;i++) s=(s*31+seed.charCodeAt(i))&0x7fffffff;
    // Fisher-Yates 用 seed 做伪随机
    for(var i=arr.length-1;i>0;i--){
      s=(s*9301+49297)%233280;
      var j=s%(i+1);
      var t=arr[i];arr[i]=arr[j];arr[j]=t;
    }
    return arr;
  }

  function renderList(phrases,type,avatarPool){
    return phrases.map(function(p,i){
      var avatarIdx=avatarPool[i % avatarPool.length];
      return '<div class="voice-card '+type+'">'
        +'<div class="vc-avatar"><img src="'+getAvatar(avatarIdx)+'" alt="游客" onerror="this.style.display=\'none\';this.parentNode.classList.add(\'no-img\')"></div>'
        +'<div class="vc-text">'+p+'</div>'
        +'</div>';
    }).join('');
  }

  var posPhrases=(data.positive||[]).slice(0,8);
  var negPhrases=(data.negative||[]).slice(0,8);

  // 好评和差评分别用不同的洗牌结果，避免重复
  var posPool=shuffle12(s+'_pos');
  var negPool=shuffle12(s+'_neg');

  if(posPhrases.length){
    posBox.innerHTML=renderList(posPhrases,'pos',posPool);
  } else {
    posBox.innerHTML='<div class="hi-loading" style="color:var(--t3)">暂无好评数据</div>';
  }

  if(negPhrases.length){
    negBox.innerHTML=renderList(negPhrases,'neg',negPool);
  } else {
    negBox.innerHTML='<div class="hi-loading" style="color:var(--t3)">暂无差评数据</div>';
  }

  // 触发失望诊断图表 resize
  setTimeout(function(){
    if(charts.detailNegativeChart&&!charts.detailNegativeChart.isDisposed()){
      charts.detailNegativeChart.resize();
    }
  },100);
}
function syncVoiceHeight(){
  var voiceCard=document.querySelector('.detail-voice-card');
  var diagCard=document.querySelector('.detail-diag-card');
  if(!voiceCard||!diagCard)return;
  var diagH=diagCard.offsetHeight;
  if(diagH>0){
    voiceCard.style.height=diagH+'px';
  }
}

// 趋势图
async function loadSpotTrend(spotName){
  if(!spotName) return;
  var startEl = document.getElementById('trendDateStart');
  var endEl = document.getElementById('trendDateEnd');
  var url = '/api/spot_trend?spot_name=' + encodeURIComponent(spotName);
  if(startEl && startEl.value) url += '&start=' + startEl.value;
  if(endEl && endEl.value) url += '&end=' + endEl.value;

  var data = await api(url);
  if(!data || !data.length){
    var el = document.getElementById('trendChart');
    if(el) el.innerHTML = '<div style="text-align:center;padding:40px;color:var(--t3)">暂无趋势数据</div>';
    return;
  }

  if(startEl && !startEl.value && data.length > 0) startEl.value = data[0].month + '-01';
  if(endEl && !endEl.value && data.length > 0) endEl.value = data[data.length-1].month + '-28';

  var c = mk('trendChart');
  if(!c) return;

  var months = data.map(function(d){ return d.month });
  var counts = data.map(function(d){ return d.count });
  // ✨ 评分为 0 的月份显示为 null，让评分线在空月份断开
  var scores = data.map(function(d){ return d.avg_score > 0 ? d.avg_score : null });

  var markPoints = [];
  data.forEach(function(d, i){
    if(d.is_peak){
      markPoints.push({
        name:'峰值',
        value:d.count,
        xAxis:i,
        yAxis:d.count,
        itemStyle:{color:'#ef4444'},
        symbolSize:16,
        label:{
          show:true,
          formatter:'🔥 峰值\n'+d.count+'条',
          color:'#ef4444',
          fontSize:11,
          fontWeight:'bold',
          position:'top',
          lineHeight:16
        }
      });
    }
    if(d.is_turning){
      markPoints.push({
        name:'转折',
        value:d.count,
        xAxis:i,
        yAxis:d.count,
        itemStyle:{color:'#fb923c'},
        symbol:'diamond',
        symbolSize:12,
        label:{show:true, formatter:'⚡', position:'top', fontSize:14}
      });
    }
  });

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{
      trigger:'axis',
      backgroundColor:tt.backgroundColor,
      borderColor:tt.borderColor,
      textStyle:tt.textStyle,
      formatter:function(params){
        var h = '<b>' + params[0].axisValue + '</b><br/>';
        params.forEach(function(p){
          if(p.value === null || p.value === undefined){
            // 空月份特殊处理
            if(p.seriesIndex === 0){
              h += p.marker + ' ' + p.seriesName + ': 0 条<br/>';
            } else {
              h += p.marker + ' ' + p.seriesName + ': 无数据<br/>';
            }
          } else {
            h += p.marker + ' ' + p.seriesName + ': ' + p.value + (p.seriesIndex === 0 ? ' 条' : ' 分') + '<br/>';
          }
        });
        return h;
      }
    },
    legend:{data:['评论量','平均评分'], textStyle:{color:css('--t2')}, bottom:0},
    grid:{left:'10%', right:'10%', top:'12%', bottom:'18%'},
    xAxis:{
      type:'category',
      data:months,
      axisLabel:{color:css('--t2'), fontSize:10, rotate:30},
      axisLine:{lineStyle:{color:css('--border')}}
    },
    yAxis:[
      {
        type:'value',
        name:'评论量',
        nameTextStyle:{color:css('--t2'), fontSize:11},
        axisLabel:{color:css('--t2')},
        splitLine:{lineStyle:{color:css('--border')}}
      },
      {
        type:'value',
        name:'评分',
        nameTextStyle:{color:css('--t2'), fontSize:11},
        axisLabel:{color:css('--t2')},
        splitLine:{show:false},
        min:1,
        max:5
      }
    ],
    series:[
      {
        name:'评论量',
        type:'line',
        data:counts,
        smooth:true,
        lineStyle:{color:'#00d4aa', width:3},
        areaStyle:{
          color:new echarts.graphic.LinearGradient(0,0,0,1,[
            {offset:0, color:'rgba(0,212,170,.25)'},
            {offset:1, color:'rgba(0,212,170,.02)'}
          ])
        },
        itemStyle:{color:'#00d4aa'},
        markPoint:{data:markPoints, symbolSize:14}
      },
      {
        name:'平均评分',
        type:'line',
        yAxisIndex:1,
        data:scores,
        smooth:true,
        connectNulls:false,    // ✨ 空值处断开，不连接
        lineStyle:{color:'#a78bfa', width:2, type:'dashed'},
        itemStyle:{color:'#a78bfa'}
      }
    ]
  });
}
function applyTrendDate(){var spot=document.getElementById('ds').value;if(spot)loadSpotTrend(spot)}
function resetTrendDate(){var s=document.getElementById('trendDateStart');var e=document.getElementById('trendDateEnd');if(s)s.value='';if(e)e.value='';var spot=document.getElementById('ds').value;if(spot)loadSpotTrend(spot)}
async function genAIReply(){
  var reviewText = document.getElementById('reviewText').value.trim();
  var spotName = document.getElementById('ds').value;
  var score = parseInt(document.getElementById('reviewScore').value);
  var btn = document.getElementById('genReplyBtn');
  var resultEl = document.getElementById('replyResult');

  if(!reviewText){
    alert('请输入差评内容');
    return;
  }

  btn.disabled = true;
  btn.textContent = '⏳ 生成中...';
  resultEl.classList.add('show');
  resultEl.innerHTML = '<div class="reply-result-card"><div class="loading" style="padding:20px"><div class="spinner"></div>AI正在分析差评并生成专业回复...</div></div>';

  try{
    var resp = await fetch('/api/ai_reply', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        review_text: reviewText,
        spot_name: spotName,
        sentiment_score: score
      })
    });
    var json = await resp.json();

    if(json.status === 'success' && json.data){
      var d = json.data;
      var warning = d.needs_review
        ? '<div class="reply-warning">⚠️ 该评分极低（1分），建议人工审核后再发送给游客</div>'
        : '';

      resultEl.innerHTML =
        '<div class="reply-result-card">'
        + '<div class="reply-result-head">'
        +   '<span class="reply-result-title">📨 AI生成的官方回复</span>'
        +   '<span class="reply-engine-tag">🤖 ' + (d.engine || 'AI') + '</span>'
        + '</div>'
        + '<div class="reply-text" id="replyTextContent">' + d.reply + '</div>'
        + warning
        + '<div class="reply-actions">'
        +   '<button class="reply-action-btn primary" onclick="copyReply()">📋 复制回复</button>'
        +   '<button class="reply-action-btn" onclick="genAIReply()">🔄 重新生成</button>'
        + '</div>'
        + '</div>';
    } else {
      resultEl.innerHTML = '<div class="reply-result-card" style="border-color:rgba(239,68,68,.3)"><span style="color:var(--red)">❌ ' + (json.message || '生成失败') + '</span></div>';
    }
  } catch(err){
    resultEl.innerHTML = '<div class="reply-result-card" style="border-color:rgba(239,68,68,.3)"><span style="color:var(--red)">❌ 请求失败：' + err.message + '</span></div>';
  } finally {
    btn.disabled = false;
    btn.textContent = '🤖 生成回复';
  }
}

function copyReply(){
  var text = document.getElementById('replyTextContent').innerText;
  if(!text) return;
  navigator.clipboard.writeText(text).then(function(){
    var btns = document.querySelectorAll('.reply-action-btn.primary');
    btns.forEach(function(b){
      var orig = b.innerHTML;
      b.innerHTML = '✅ 已复制';
      setTimeout(function(){b.innerHTML = orig}, 1500);
    });
  }).catch(function(){
    alert('复制失败，请手动选择复制');
  });
}
async function loadAISpot(){
  var spot=document.getElementById('ds').value;
  if(!spot){alert('请先选择景点');return}

  var body=document.getElementById('aiReportBody');
  if(!body){alert('请先选择景点并加载详情');return}

  body.innerHTML='<div class="loading"><div class="spinner"></div>🤖 AI分析中...</div>';

  var data=await api('/api/ai_spot_analysis?spot_name='+encodeURIComponent(spot));
  if(!data){body.innerHTML='<p style="color:var(--red);padding:20px">AI分析失败</p>';return}

  body.innerHTML='<div style="margin-bottom:10px">'+aiBadge(data)+'</div><div class="ai-result">'+md(data.content)+'</div>';
}
// 深度洞察四宫格
async function renderInsights(rankData, overview){
  var ig=document.getElementById('insightGrid');
  if(!ig||!overview)return;

  // ===== 卡 1：TOP 景点（直接用 rankData）=====
  var topSpot=rankData[0]||{};

  // ===== 卡 2：整体满意度（用 overview）=====
  var totalC=overview.total_comments||1;
  var posCnt=overview.sentiment_summary?overview.sentiment_summary.positive||0:0;
  var posRate=(posCnt/totalC*100).toFixed(1);

  // ===== 卡 3、卡 4 需要并行请求 =====
  var results=await Promise.all([
    api('/api/negative_model?top_n=1'),
    api('/api/hot_potential?top_n=1')
  ]);
  var negData=results[0]||{};
  var potData=results[1]||[];

  // 卡 3：最大痛点
  var topNeg=(negData.items&&negData.items.length>0)?negData.items[0]:null;
  var negFactor=topNeg?topNeg.factor:'-';
  var negImpact=topNeg?topNeg.impact:'-';
  var negOccur=topNeg?topNeg.occurrence_pct+'%':'-';

  // 卡 4：爆发潜力
  var topPot=(potData&&potData.length>0)?potData[0]:null;
  var potName=topPot?topPot.spot_name:'-';
  var potScore=topPot?topPot.potential_score:'-';
  var potGrowth=topPot?(topPot.growth_rate>=0?'+':'')+topPot.growth_rate+'%':'-';

  var insights=[
    {
      icon:'🏆',
      iconBg:'rgba(59,130,246,.1)',
      iconColor:'#3b82f6',
      title:'热度 TOP 景点',
      main:topSpot.spot_name||'-',
      bottom:(topSpot.comment_count||0).toLocaleString()+' 条游客评论',
      badge:'评分 '+(topSpot.avg_score||'-'),
      badgeCls:'badge-blue'
    },
    {
      icon:'📊',
      iconBg:'rgba(16,185,129,.1)',
      iconColor:'#10b981',
      title:'整体满意度',
      main:posRate+'%',
      bottom:'基于 '+totalC.toLocaleString()+' 条评论',
      badge:'好评率',
      badgeCls:'badge-green'
    },
    {
      icon:'⚠️',
      iconBg:'rgba(239,68,68,.1)',
      iconColor:'#ef4444',
      title:'最大痛点',
      main:negFactor,
      bottom:negOccur+' 的差评提到',
      badge:'影响 '+negImpact,
      badgeCls:'badge-pink'
    },
    {
      icon:'🚀',
      iconBg:'rgba(245,158,11,.1)',
      iconColor:'#f59e0b',
      title:'爆发潜力之星',
      main:potName,
      bottom:'预计热度 '+potGrowth,
      badge:'指数 '+potScore,
      badgeCls:'badge-orange'
    }
  ];

  ig.innerHTML=insights.map(function(it){
    return '<div class="insight-card">'
      +'<div class="insight-head">'
      +'<div class="insight-icon" style="background:'+it.iconBg+';color:'+it.iconColor+'">'+it.icon+'</div>'
      +'<div class="insight-title">'+it.title+'</div>'
      +'</div>'
      +'<div class="insight-main">'+it.main+'</div>'
      +'<div class="insight-bottom"><span>'+it.bottom+'</span><span class="badge '+it.badgeCls+'">'+it.badge+'</span></div>'
      +'</div>';
  }).join('');
}
// 对比

async function loadCmp(){
  var sps = cmpSelectedSpots.filter(function(s){ return s });
  if(sps.length < 2){
    alert('请至少选择2个景点');
    return;
  }

  var resultEl = document.getElementById('cr2');
  resultEl.innerHTML = '<div class="loading"><div class="spinner"></div>对比分析中...</div>';

  // 并行请求
  var results = await Promise.all([
    api('/api/comparison_advanced?spots=' + encodeURIComponent(sps.join(','))),
    api('/api/ai_comparison_summary?spots=' + encodeURIComponent(sps.join(',')))
  ]);

  var data = results[0];
  var aiSummary = results[1];

  if(!data || !data.length){
    resultEl.innerHTML = '<div class="card"><p style="color:var(--red);padding:20px">数据加载失败</p></div>';
    return;
  }

  var colors = ['#7a9cc6', '#b598d4', '#e8a87c'];

  // 1. 核心指标 PK 卡
  var html = renderCmpPKCards(data, colors);

  // 2. 雷达 + 评分分布
  html += '<div class="cmp-mid-grid">';
  html += '<div class="card"><div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(122,156,198,.1)">🎯</span><span class="ch-title">能力雷达对比</span></div></div><div class="chart-box" id="cmpRadarChart" style="height:380px"></div></div>';
  html += '<div class="card"><div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(181,152,212,.1)">📊</span><span class="ch-title">评分分布对比</span></div></div><div class="chart-box" id="cmpDistChart" style="height:380px"></div></div>';
  html += '</div>';

  // 3. AI 对比卡片
  html += renderCmpAICards(data, aiSummary, colors);

  // 4. AI 推荐结论
  html += renderCmpSummary(aiSummary);

  resultEl.innerHTML = html;

  // 渲染图表
  setTimeout(function(){
    renderCmpRadar(data, colors);
    renderCmpDist(data, colors);
  }, 200);
}

// 核心指标 PK 卡
function renderCmpPKCards(data, colors){
  var metrics = [
    {key:'avg_score', icon:'⭐', title:'平均评分', suffix:'', better:'higher'},
    {key:'positive_rate', icon:'👍', title:'好评率', suffix:'%', better:'higher'},
    {key:'negative_rate', icon:'📉', title:'差评率', suffix:'%', better:'lower'},
    {key:'heat_score', icon:'🔥', title:'综合热度', suffix:'', better:'higher'}
  ];

  var html = '<div class="cmp-pk-grid">';
  metrics.forEach(function(m){
    var values = data.map(function(d){ return d[m.key] });
    var champion = m.better === 'higher' ? Math.max.apply(null, values) : Math.min.apply(null, values);

    html += '<div class="cmp-pk-card">';
    html += '<div class="cmp-pk-head"><span class="cmp-pk-icon">' + m.icon + '</span><span class="cmp-pk-title">' + m.title + '</span></div>';
    html += '<div class="cmp-pk-rows">';
    data.forEach(function(d, i){
      var isChamp = d[m.key] === champion;
      var val;
      if(m.key === 'heat_score'){
        val = d[m.key] !== undefined ? d[m.key] : '-';
      } else {
        val = d[m.key];
      }
      html += '<div class="cmp-pk-row' + (isChamp ? ' champion' : '') + '">';
      html += '<span class="cmp-pk-spot"><span class="cmp-pk-dot" style="background:' + colors[i] + '"></span>' + d.name + '</span>';
      html += '<span class="cmp-pk-value">' + val + m.suffix + (isChamp ? '<span class="cmp-pk-crown">🏆</span>' : '') + '</span>';
      html += '</div>';
    });
    html += '</div></div>';
  });
  html += '</div>';
  return html;
}

// 雷达图
function renderCmpRadar(data, colors){
  var c = mk('cmpRadarChart');
  if(!c) return;
  var dimensions = ['服务质量', '卫生环境', '设施完善', '性价比', '文化体验', '人流管理'];

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{backgroundColor:tt.backgroundColor,borderColor:tt.borderColor,textStyle:tt.textStyle},
    legend:{data:data.map(function(d){return d.name}),textStyle:{color:css('--t2')},bottom:0},
    radar:{
      indicator:dimensions.map(function(d){return {name:d,max:100}}),
      center:['50%','48%'],
      radius:'62%',
      shape:'polygon',
      splitNumber:4,
      axisName:{color:css('--t1'),fontSize:12,fontWeight:600},
      splitLine:{lineStyle:{color:css('--border')}},
      splitArea:{areaStyle:{color:['rgba(255,255,255,0)','rgba(122,156,198,.03)','rgba(255,255,255,0)','rgba(122,156,198,.03)']}},
      axisLine:{lineStyle:{color:css('--border')}}
    },
    series:[{
      type:'radar',
      data:data.map(function(d,i){
        return {
          name:d.name,
          value:dimensions.map(function(dim){return d.radar_scores[dim] || 0}),
          lineStyle:{color:colors[i],width:2},
          areaStyle:{color:colors[i],opacity:0.15},
          itemStyle:{color:colors[i]}
        };
      })
    }]
  });
}

// 评分分布分组柱状图
function renderCmpDist(data, colors){
  var c = mk('cmpDistChart');
  if(!c) return;

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{trigger:'axis',backgroundColor:tt.backgroundColor,borderColor:tt.borderColor,textStyle:tt.textStyle},
    legend:{data:data.map(function(d){return d.name}),textStyle:{color:css('--t2')},top:0},
    grid:{left:'8%',right:'5%',top:'15%',bottom:'15%'},
    xAxis:{type:'category',data:['1分','2分','3分','4分','5分'],axisLabel:{color:css('--t2')}},
    yAxis:{type:'value',axisLabel:{color:css('--t2')},splitLine:{lineStyle:{color:css('--border')}}},
    series:data.map(function(d,i){
      return {
        name:d.name,
        type:'bar',
        data:[1,2,3,4,5].map(function(s){return d.score_distribution[s] || d.score_distribution[String(s)] || 0}),
        itemStyle:{color:colors[i],borderRadius:[6,6,0,0]},
        barGap:'10%',
        barCategoryGap:'30%'
      };
    })
  });
}

// AI 对比 3 列卡片
function renderCmpAICards(data, aiSummary, colors){
  var profiles = (aiSummary && aiSummary.spot_profiles) ? aiSummary.spot_profiles : [];

  var gridClass = data.length === 2 ? 'cmp-ai-grid two-cols' : 'cmp-ai-grid';
  var html = '<div class="' + gridClass + '">';
  data.forEach(function(d, i){
    var profile = profiles.find(function(p){ return p.name === d.name });

    html += '<div class="cmp-ai-card" data-idx="' + i + '">';
    html += '<div class="cmp-ai-name">' + d.name + '</div>';
    if(profile && profile.tagline){
      html += '<div class="cmp-ai-tagline">"' + profile.tagline + '"</div>';
    }

    // 优势
    html += '<div class="cmp-ai-section">';
    html += '<div class="cmp-ai-section-title pos">✅ 核心优势</div>';
    if(d.positive_keywords && d.positive_keywords.length){
      html += '<ul class="cmp-ai-list pos">';
      d.positive_keywords.slice(0,4).forEach(function(k){
        html += '<li>' + k + '</li>';
      });
      html += '</ul>';
    } else {
      html += '<div style="color:var(--t3);font-size:11px">暂无数据</div>';
    }
    html += '</div>';

    // 不足
    html += '<div class="cmp-ai-section">';
    html += '<div class="cmp-ai-section-title neg">⚠️ 主要不足</div>';
    if(d.negative_keywords && d.negative_keywords.length){
      html += '<ul class="cmp-ai-list neg">';
      d.negative_keywords.slice(0,4).forEach(function(k){
        html += '<li>' + k + '</li>';
      });
      html += '</ul>';
    } else {
      html += '<div style="color:var(--t3);font-size:11px">暂无数据</div>';
    }
    html += '</div>';

    // 适合人群
    if(profile && profile.best_for){
      html += '<div class="cmp-ai-section">';
      html += '<div class="cmp-ai-section-title tag">🎯 适合人群</div>';
      html += '<div class="cmp-ai-best">' + profile.best_for + '</div>';
      html += '</div>';
    }

    html += '</div>';
  });
  html += '</div>';
  return html;
}

// AI 推荐结论
function renderCmpSummary(aiSummary){
  if(!aiSummary || !aiSummary.summary){
    return '';
  }

  var html = '<div class="cmp-summary-card">';
  html += '<div class="cmp-summary-head">';
  html += '<div class="cmp-summary-title"><div class="cmp-summary-icon">💡</div>AI 综合推荐</div>';
  if(aiSummary.engine){
    html += '<span class="ai-badge ' + (aiSummary.status === 'success' ? 'badge-ai' : 'badge-local') + '">🤖 ' + aiSummary.engine + '</span>';
  }
  html += '</div>';

  // 一句话总结
  html += '<div class="cmp-summary-text">' + aiSummary.summary + '</div>';

  // 场景推荐
  if(aiSummary.scenario_recommendations && aiSummary.scenario_recommendations.length){
    var icons = {'文化深度游':'🏛️','情侣浪漫游':'💝','亲子家庭游':'👨‍👩‍👧','网红打卡':'📸','性价比之选':'💰'};
    html += '<div class="cmp-scenario-title">🏆 不同需求的最佳选择</div>';
    html += '<div class="cmp-scenario-grid">';
    aiSummary.scenario_recommendations.forEach(function(s){
      var icon = icons[s.scenario] || '🎯';
      html += '<div class="cmp-scenario-item">';
      html += '<div class="cmp-scenario-icon">' + icon + '</div>';
      html += '<div class="cmp-scenario-info">';
      html += '<div class="cmp-scenario-name">' + s.scenario + '</div>';
      html += '<div class="cmp-scenario-recommend">' + s.recommend + '</div>';
      html += '<div class="cmp-scenario-reason">' + s.reason + '</div>';
      html += '</div>';
      html += '</div>';
    });
    html += '</div>';
  }

  html += '</div>';
  return html;
}
// ========== 旅游规划 - 重构版 ==========

// 全局存储已选景点
var planSelectedSpots = [];

// 初始化景点卡片网格
function initPlanSpots(){
  var container=document.getElementById('planSpots');
  if(!container||!spots.length)return;

  container.innerHTML=spots.map(function(s){
    var img=SPOT_IMAGES[s]||'/static/景点照片/spot1.png';
    var meta=(typeof SPOT_META!=='undefined'&&SPOT_META[s])?SPOT_META[s]:{level:'-',duration:'2-3小时',address:'西安市'};
    var rank=rankData.find(function(d){return d.spot_name===s});
    var rating=rank?rank.avg_score:'-';
    // 从 address 提取区域（取最后2-3个字，如"临潼区"）
    var area=meta.address.match(/(雁塔区|碑林区|临潼区|长安区|未央区|曲江新区|碑林区|灞桥区|新城区|莲湖区|高陵区|阎良区|周至县|蓝田县|鄠邑区|长安区)/);
    var areaText=area?area[0]:'西安';

    return '<div class="spot-pick-card" data-spot="'+s+'" onclick="togglePlanSpot(this)">'
      +'<div class="spc-img-wrap">'
      +'<img class="spc-img" src="'+img+'" alt="'+s+'" onerror="this.src=\'/static/景点照片/spot1.png\'">'
      +'<div class="spc-check"><span>✓</span></div>'
      +'</div>'
      +'<div class="spc-body">'
      +'<div class="spc-name">'+s+'</div>'
      +'<div class="spc-meta"><span>⭐ '+rating+'</span><span>⏰ '+meta.duration+'</span></div>'
      +'<div class="spc-area">📍 '+areaText+'</div>'
      +'<div class="spc-btn">+ 加入行程</div>'
      +'</div>'
      +'</div>';
  }).join('');
}

// 点击景点卡片：加入/移除
function togglePlanSpot(el){
  var spot=el.getAttribute('data-spot');
  if(!spot)return;
  var idx=planSelectedSpots.indexOf(spot);
  if(idx>=0){
    planSelectedSpots.splice(idx,1);
    el.classList.remove('on');
  } else {
    planSelectedSpots.push(spot);
    el.classList.add('on');
  }
  // 自动按最优路径排序
  optimizeItineraryOrderSilent();
  refreshPlanUI();
}

// 从行程预览里移除一个景点
function removeFromItinerary(spot){
  var idx=planSelectedSpots.indexOf(spot);
  if(idx<0)return;
  planSelectedSpots.splice(idx,1);
  var card=document.querySelector('.spot-pick-card[data-spot="'+spot+'"]');
  if(card) card.classList.remove('on');
  // 移除后也重新优化
  optimizeItineraryOrderSilent();
  refreshPlanUI();
}

// 清空全部
function clearItinerary(){
  planSelectedSpots=[];
  document.querySelectorAll('.spot-pick-card.on').forEach(function(c){c.classList.remove('on')});
  refreshPlanUI();
}

// 解析时长字符串为小时数（如 "3-4小时" -> 3.5）
function parseDurationHours(str){
  if(!str)return 0;
  var m=str.match(/(\d+)(?:-(\d+))?\s*小时/);
  if(m){
    var lo=parseFloat(m[1]);
    var hi=m[2]?parseFloat(m[2]):lo;
    return (lo+hi)/2;
  }
  if(/半天/.test(str)) return 4;
  if(/一?整天|一天/.test(str)) return 8;
  if(/一?天/.test(str)) return 6;
  return 3;
}
// ========== 行程地图 ==========

// 计算两点距离（粗略，用经纬度直接算）
function spotDistance(a, b){
  var dx=a[0]-b[0];
  var dy=a[1]-b[1];
  return Math.sqrt(dx*dx+dy*dy);
}

// 智能优化顺序：贪心算法（从第一个景点开始，每次找最近的）
// 智能优化顺序（核心算法，无UI弹窗）
function optimizeItineraryOrderSilent(){
  if(planSelectedSpots.length<=2) return;

  var coords=planSelectedSpots.map(function(s){return SPOT_COORDS[s]||null});
  if(coords.some(function(c){return !c})) return;

  var optimized=[planSelectedSpots[0]];
  var remaining=planSelectedSpots.slice(1);

  while(remaining.length>0){
    var lastCoord=SPOT_COORDS[optimized[optimized.length-1]];
    var bestIdx=0;
    var bestDist=Infinity;
    for(var i=0;i<remaining.length;i++){
      var d=spotDistance(lastCoord, SPOT_COORDS[remaining[i]]);
      if(d<bestDist){
        bestDist=d;
        bestIdx=i;
      }
    }
    optimized.push(remaining[bestIdx]);
    remaining.splice(bestIdx,1);
  }

  planSelectedSpots=optimized;
}

// 手动按钮：保留入口，但内部调用 silent 版本 + 刷新 UI
function optimizeItineraryOrder(){
  if(planSelectedSpots.length<=2){
    alert('至少需要 3 个景点才能优化顺序');
    return;
  }
  optimizeItineraryOrderSilent();
  refreshPlanUI();
}

// 渲染行程地图
function renderItineraryMap(){
  var mapEl=document.getElementById('itineraryMap');
  if(!mapEl)return;

  // 没有景点时清空
  if(planSelectedSpots.length===0){
    if(charts.itineraryMap&&!charts.itineraryMap.isDisposed()){
      charts.itineraryMap.dispose();
      delete charts.itineraryMap;
    }
    mapEl.innerHTML='<div class="map-empty">选择景点后将在此显示路线</div>';
    return;
  }

  // 收集有坐标的景点
  var validSpots=planSelectedSpots.map(function(s,i){
    var coord=SPOT_COORDS[s];
    if(!coord)return null;
    return {name:s, coord:coord, order:i+1};
  }).filter(function(x){return x!==null});

  if(validSpots.length===0){
    mapEl.innerHTML='<div class="map-empty">景点坐标缺失</div>';
    return;
  }

  // 散点数据（带编号 label）
  var scatterData=validSpots.map(function(s){
    return {
      name:s.name,
      value:[s.coord[0], s.coord[1], s.order],
      label:{
        show:true,
        formatter:s.order+'',
        color:'#fff',
        fontSize:11,
        fontWeight:'bold'
      }
    };
  });

  // 连线数据
  var lineData=[];
  for(var i=0;i<validSpots.length-1;i++){
    lineData.push({
      coords:[validSpots[i].coord, validSpots[i+1].coord]
    });
  }

  // 确保 geojson 已注册（首页地图初始化时已经 echarts.registerMap('xian',...)）
  // 这里直接使用
  var c=mk('itineraryMap');
  if(!c)return;

    // ===== 自动计算地图聚焦范围 =====
  var lons=validSpots.map(function(s){return s.coord[0]});
  var lats=validSpots.map(function(s){return s.coord[1]});
  var minLon=Math.min.apply(null,lons);
  var maxLon=Math.max.apply(null,lons);
  var minLat=Math.min.apply(null,lats);
  var maxLat=Math.max.apply(null,lats);

  // 中心点
  var centerLon=(minLon+maxLon)/2;
  var centerLat=(minLat+maxLat)/2;

  // 跨度（用经纬度差的较大值）
  var spanLon=maxLon-minLon;
  var spanLat=maxLat-minLat;
  var span=Math.max(spanLon, spanLat);

  // 根据跨度反推 zoom（经验值）
  // 西安市跨度约 1.5°×0.8°，默认 zoom=1 是看全西安
  // 跨度越小 zoom 越大
  var zoom;
  if(span<0.01)      zoom=8;     // 几乎同一点
  else if(span<0.05) zoom=5;     // 同一区内
  else if(span<0.15) zoom=3;     // 相邻区
  else if(span<0.4)  zoom=2;     // 跨多个区
  else               zoom=1.2;   // 跨整个西安

  // 单个景点时使用更高 zoom
  if(validSpots.length===1) zoom=4;

  var c=mk('itineraryMap');
  if(!c)return;

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{
      trigger:'item',
      formatter:function(p){
        if(p.seriesType==='effectScatter'){
          return '<b>'+p.value[2]+'. '+p.name+'</b>';
        }
        return p.name;
      },
      backgroundColor:tt.backgroundColor,
      borderColor:tt.borderColor,
      textStyle:tt.textStyle
    },
    geo:{
      map:'xian',
      roam:true,                          // 改成 true，允许用户手动缩放
      zoom:zoom,                          // 自动缩放级别
      center:[centerLon, centerLat],      // 自动居中
      label:{show:false},
      itemStyle:{
        areaColor:'#e0eaff',
        borderColor:'#94a3b8',
        borderWidth:0.8
      },
      emphasis:{
        itemStyle:{areaColor:'#c7d9ff'},
        label:{show:false}
      },
      // 阻止地图缩放过度
      scaleLimit:{min:1, max:12}
    },
    series:[
      {
        type:'lines',
        coordinateSystem:'geo',
        data:lineData,
        lineStyle:{
          color:'#3b82f6',
          width:2.5,
          curveness:0.2,
          opacity:0.8
        },
        effect:{
          show:true,
          period:4,
          trailLength:0.3,
          symbol:'arrow',
          symbolSize:8,
          color:'#fbbf24'
        },
        z:2
      },
      {
        type:'effectScatter',
        coordinateSystem:'geo',
        data:scatterData,
        symbolSize:22,
        rippleEffect:{
          brushType:'stroke',
          scale:2.5,
          period:3
        },
        itemStyle:{
          color:'#3b82f6',
          shadowBlur:10,
          shadowColor:'rgba(59,130,246,.5)'
        },
        z:3
      }
    ]
  });
}
// 刷新所有 UI（行程预览、统计、底部栏）
function refreshPlanUI(){
  var count=planSelectedSpots.length;

  // 计算总时长
  var totalHours=0;
  planSelectedSpots.forEach(function(s){
    var meta=(typeof SPOT_META!=='undefined'&&SPOT_META[s])?SPOT_META[s]:null;
    if(meta) totalHours+=parseDurationHours(meta.duration);
  });
  var hoursText=totalHours.toFixed(1);

  // 行程预览列表
  var listEl=document.getElementById('planItinerary');
  if(listEl){
    if(count===0){
      listEl.innerHTML='<div class="plan-empty">还未选择景点</div>';
    } else {
      listEl.innerHTML=planSelectedSpots.map(function(s,i){
        var meta=(typeof SPOT_META!=='undefined'&&SPOT_META[s])?SPOT_META[s]:{duration:'-',address:'西安'};
        var area=meta.address.match(/(雁塔区|碑林区|临潼区|长安区|未央区|曲江新区|灞桥区|新城区|莲湖区|高陵区|阎良区|周至县|蓝田县|鄠邑区)/);
        var areaText=area?area[0]:'西安';
        return '<div class="itin-item">'
          +'<div class="itin-num">'+(i+1)+'</div>'
          +'<div class="itin-info">'
          +'<div class="itin-name">'+s+'</div>'
          +'<div class="itin-meta">'+areaText+' · '+meta.duration+'</div>'
          +'</div>'
          +'<button class="itin-remove" onclick="removeFromItinerary(\''+s+'\')">×</button>'
          +'</div>';
      }).join('');
    }
  }

  // 行程统计
  var statsEl=document.getElementById('planItineraryStats');
  if(statsEl){
    if(count>0){
      statsEl.style.display='block';
      var pisDur=document.getElementById('pisDuration');
      if(pisDur) pisDur.textContent=hoursText+' 小时';
    } else {
      statsEl.style.display='none';
    }
  }

  // 底部行动栏
  var pabCount=document.getElementById('pabCount');
  var pabDuration=document.getElementById('pabDuration');
  var btn=document.getElementById('planSubmitBtn');
  if(pabCount) pabCount.textContent=count;
  if(pabDuration) pabDuration.textContent=hoursText;
  if(btn){
    btn.disabled=(count===0);
    if(count>0) btn.classList.add('on');
    else btn.classList.remove('on');
  }
    // 同步刷新地图
  setTimeout(renderItineraryMap, 50);
}

// 偏好卡片单选切换
document.addEventListener('click',function(e){
  var card=e.target.closest('.pref-card');
  if(!card)return;
  var parent=card.parentNode;
  parent.querySelectorAll('.pref-card').forEach(function(c){c.classList.remove('on')});
  card.classList.add('on');
});

// 获取选中的偏好值
function getPrefValue(prefName){
  var group=document.querySelector('.pref-options[data-pref="'+prefName+'"]');
  if(!group)return '';
  var sel=group.querySelector('.pref-card.on');
  return sel?sel.getAttribute('data-val'):'';
}

// 生成 AI 行程
async function generateDayPlan(){
  if(planSelectedSpots.length===0){alert('请至少选择一个景点');return}

  var duration=getPrefValue('duration')||'一日游';
  var startTime=document.getElementById('planStartTime').value||'08:30';
  var transport=getPrefValue('transport')||'地铁+步行';
  var seasonEl = document.getElementById('planSeason');
  var season = seasonEl ? seasonEl.value : '不限';

  document.getElementById('pr').innerHTML='<div class="card"><div class="loading"><div class="spinner"></div>🤖 AI 正在规划行程（'+planSelectedSpots.length+'个景点，'+duration+'）...</div></div>';

  setTimeout(function(){
    document.getElementById('pr').scrollIntoView({behavior:'smooth',block:'start'});
  },100);

  var spotsStr=planSelectedSpots.join(',');
  var url='/api/day_plan?spots='+encodeURIComponent(spotsStr)
    +'&duration='+encodeURIComponent(duration)
    +'&start_time='+encodeURIComponent(startTime)
    +'&transport='+encodeURIComponent(transport)
    +'&season='+encodeURIComponent(season);   // ✨ 新增

  var data=await api(url);

  if(!data||data.error){
    document.getElementById('pr').innerHTML='<div class="card"><p style="color:var(--red)">'+(data&&data.error?data.error:'AI 规划生成失败，请重试')+'</p></div>';
    return;
  }

  var spotsTag=planSelectedSpots.map(function(s){
    return '<span class="plan-result-tag">'+s+'</span>'
  }).join('');

  var seasonText = season === '不限' ? '' : (' · 季节偏好：' + season);

  document.getElementById('pr').innerHTML=
    '<div class="card">'
    +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(52,211,153,.1)">🗺️</span><span class="ch-title">'+duration+'规划方案</span></div>'+aiBadge(data)+'</div>'
    +'<div class="plan-result-meta">'
    +'<div class="prm-row"><span class="prm-label">景点：</span><div class="prm-tags">'+spotsTag+'</div></div>'
    +'<div class="prm-row"><span class="prm-label">出发时间：</span>'+startTime+' · 交通：'+transport+seasonText+'</div>'
    +'</div>'
    +'<div class="ai-result">'+md(data.content)+'</div>'
    +'</div>';
}
// 展开/收起更多景点
function togglePlanMore(){
  var grid=document.getElementById('planSpots');
  var text=document.getElementById('planMoreText');
  var arrow=document.getElementById('planMoreArrow');
  if(!grid)return;
  grid.classList.toggle('collapsed');
  if(grid.classList.contains('collapsed')){
    if(text) text.textContent='查看更多景点';
    if(arrow) arrow.textContent='▼';
  } else {
    if(text) text.textContent='收起景点';
    if(arrow) arrow.textContent='▲';
  }
}
// 运营
async function loadOp(){
  // 1. 加载运营预警
  loadOperationAlerts();

  // 2. 加载节假日预测
  loadHolidayForecast();

  // 4. 加载原有的成功因子 + 失望诊断
  var d = await api('/api/operation_model');
  if(!d){
    document.getElementById('or').innerHTML='<div class="loading"><p>失败</p></div>';
    return;
  }
  var factors = await api('/api/success_factors');

  var html = '';

  if(factors && factors.length){
    html += '<div class="card"><div class="card-head"><div class="ch-left">🔑 成功因子</div><span class="ch-badge">AI提炼</span></div><div>'
      + factors.map(function(f){return'<span class="factor-tag">'+f+'</span>'}).join('') + '</div></div>';
  }

  html += '<div class="card"><div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(239,68,68,.1)">⚠️</span><span class="ch-title">总体失望原因诊断</span></div><span class="ch-badge">线性回归模型</span></div><div class="chart-box" id="overallNegativeChart"></div><div id="overallNegativeTable"></div></div>';

  document.getElementById('or').innerHTML = html;
  loadNegativeModel('overall');
}
async function loadOperationAlerts(){
  var contentEl = document.getElementById('alertContent');
  var summaryEl = document.getElementById('alertSummary');
  if(!contentEl) return;

  var data = await api('/api/operation_alerts');
  if(!data){
    contentEl.innerHTML = '<div class="alert-empty">数据加载失败</div>';
    return;
  }

  var summary = data.summary || {};
  if(summaryEl){
    summaryEl.innerHTML = '🟠 紧急 ' + summary.urgent_count + ' · 🟡 关注 ' + summary.warning_count + ' · 🟢 平稳 ' + summary.stable_count;
  }

  var html = '';

  function renderSection(title, icon, items, level){
    if(!items || !items.length) return '';
    var h = '<div class="alert-section ' + level + '">';
    h += '<div class="alert-section-head">';
    h += '<span class="alert-section-icon">' + icon + '</span>';
    h += '<span class="alert-section-title">' + title + '</span>';
    h += '<span class="alert-section-count">' + items.length + '</span>';
    h += '</div>';
    h += '<div class="alert-grid">';
    items.forEach(function(item){
      h += '<div class="alert-card ' + item.level + '" onclick="goDetail(\'' + item.spot_name + '\')">';
      h += '<div class="alert-card-head">';
      h += '<span class="alert-spot-name">' + item.spot_name + '</span>';
      var levelText = item.level === 'urgent' ? '紧急' : (item.level === 'warning' ? '关注' : '平稳');
      h += '<span class="alert-level-badge">' + levelText + '</span>';
      h += '</div>';
      item.alerts.forEach(function(a, alertIdx){
        var hasComments = a.related_comments && a.related_comments.length > 0;
        h += '<div class="alert-item' + (hasComments ? ' has-tooltip' : '') + '"';
        if(hasComments){
            h += ' onmouseenter="showAlertTooltip(this, ' + JSON.stringify(a.related_comments).replace(/"/g, '&quot;') + ')"';
            h += ' onmouseleave="hideAlertTooltip()"';
        }
        h += '>';
        h += '<span class="alert-item-icon">' + a.icon + '</span>';
        h += '<div class="alert-item-text">';
        h += '<span class="alert-item-type">' + a.type + '</span>：' + a.desc;
        if(hasComments){
            h += ' <span class="alert-tip-hint">查看详情 →</span>';
        }
        h += '</div></div>';
    });
      h += '</div>';
    });
    h += '</div></div>';
    return h;
  }

  html += renderSection('紧急预警', '🟠', data.urgent, 'urgent');
  html += renderSection('关注预警', '🟡', data.warning, 'warning');
  html += renderSection('平稳运营', '🟢', data.stable, 'stable');

  if(!html){
    html = '<div class="alert-empty">暂无预警数据</div>';
  }

  contentEl.innerHTML = html;
}
async function loadHolidayForecast(){
  var contentEl = document.getElementById('holidayContent');
  if(!contentEl) return;

  var data = await api('/api/holiday_forecast');
  if(!data || !data.holiday){
    contentEl.innerHTML = '<div class="alert-empty">暂无预测数据</div>';
    return;
  }

  var h = data.holiday;
  var forecasts = data.forecasts || [];

  // 客流等级图标
  var levelIcons = {extreme: '🔴', high: '🟠', medium: '🟡', low: '🟢'};

  var html = '';

  // 节假日 Header
  html += '<div class="holiday-header">';
  html += '<div class="holiday-icon">🎉</div>';
  html += '<div class="holiday-info">';
  html += '<div class="holiday-name">' + h.name + ' · ' + h.date + '</div>';
  html += '<div class="holiday-meta">假期时长 <strong>' + h.duration + '</strong> 天 · 基于历史同期数据预测</div>';
  html += '</div>';
  html += '<div class="holiday-countdown">';
  html += '<div class="holiday-countdown-num">' + h.days_left + '</div>';
  html += '<div class="holiday-countdown-label">天后到来</div>';
  html += '</div>';
  html += '</div>';

  // 各景点预测
  var maxPred = forecasts.length > 0 ? forecasts[0].predicted_total : 1;
  html += '<div class="holiday-forecast-list">';
  forecasts.forEach(function(f){
    var pct = (f.predicted_total / maxPred * 100).toFixed(0);
    html += '<div class="holiday-spot-row">';
    html += '<div class="holiday-spot-name">' + f.spot_name + '</div>';
    html += '<div class="holiday-spot-bar-wrap">';
    html += '<div class="holiday-bar"><div class="holiday-bar-fill ' + f.level + '" style="width:' + pct + '%"></div></div>';
    html += '</div>';
    html += '<div class="holiday-spot-info">';
    html += '<div class="holiday-pred-num' + (f.has_history ? '' : ' no-history') + '">' + f.predicted_total.toLocaleString() + ' 条评论</div>';
    html += '<div style="display:flex;align-items:center;gap:6px">';
    html += '<span class="holiday-pred-label">' + (f.has_history ? '基于历史' : '估算') + '</span>';
    html += '<span class="holiday-level-tag ' + f.level + '">' + f.level_text + '</span>';
    html += '</div>';
    html += '</div>';
    html += '</div>';
  });
  html += '</div>';

  // 综合建议
  var topForecast = forecasts.filter(function(f){ return f.level === 'extreme' || f.level === 'high' });
  if(topForecast.length > 0){
    html += '<div class="holiday-suggestions">';
    html += '<div class="holiday-sug-title">💡 高客流景点应对建议</div>';
    var topSpot = topForecast[0];
    topSpot.suggestions.forEach(function(s){
      html += '<div class="holiday-sug-item">' + s + '</div>';
    });
    html += '</div>';
  }

  contentEl.innerHTML = html;
}
var radarSelectedSpots = [];

function initCapabilityRadar(){
  var chipsEl = document.getElementById('radarSpotChips');
  if(!chipsEl) return;

  // 默认选前3个
  radarSelectedSpots = spots.slice(0, 3);

  chipsEl.innerHTML = spots.map(function(s){
    var isOn = radarSelectedSpots.indexOf(s) >= 0;
    return '<div class="radar-chip' + (isOn ? ' on' : '') + '" data-spot="' + s + '" onclick="toggleRadarSpot(this,\'' + s + '\')">' + s + '</div>';
  }).join('');

  renderCapabilityRadar();
}

function toggleRadarSpot(el, spot){
  var idx = radarSelectedSpots.indexOf(spot);
  if(idx >= 0){
    radarSelectedSpots.splice(idx, 1);
    el.classList.remove('on');
  } else {
    if(radarSelectedSpots.length >= 4){
      alert('最多选择 4 个景点');
      return;
    }
    radarSelectedSpots.push(spot);
    el.classList.add('on');
  }
  renderCapabilityRadar();
}

async function renderCapabilityRadar(){
  if(radarSelectedSpots.length === 0){
    var c = mk('capabilityRadarChart');
    if(c) c.clear();
    return;
  }

  var url = '/api/capability_radar?spots=' + encodeURIComponent(radarSelectedSpots.join(','));
  var data = await api(url);
  if(!data || !data.length) return;

  var dimensions = ['服务质量', '卫生环境', '设施完善', '性价比', '文化体验', '人流管理'];
  var colors = ['#7a9cc6', '#b598d4', '#e8a87c', '#a8c5a8', '#d4b86a', '#c97c8c'];

  var c = mk('capabilityRadarChart');
  if(!c) return;

  c.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: tt.backgroundColor,
      borderColor: tt.borderColor,
      textStyle: tt.textStyle
    },
    legend: {
      data: data.map(function(d){ return d.spot_name }),
      textStyle: { color: css('--t2') },
      bottom: 0
    },
    radar: {
      indicator: dimensions.map(function(d){ return { name: d, max: 100 } }),
      center: ['50%', '50%'],
      radius: '65%',
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: css('--t1'),
        fontSize: 12,
        fontWeight: 600
      },
      splitLine: {
        lineStyle: { color: css('--border') }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(255,255,255,0)', 'rgba(122,156,198,.03)', 'rgba(255,255,255,0)', 'rgba(122,156,198,.03)']
        }
      },
      axisLine: {
        lineStyle: { color: css('--border') }
      }
    },
    series: [{
      type: 'radar',
      data: data.map(function(d, i){
        return {
          name: d.spot_name,
          value: dimensions.map(function(dim){ return d.scores[dim] || 0 }),
          lineStyle: { color: colors[i % colors.length], width: 2 },
          areaStyle: { color: colors[i % colors.length], opacity: 0.15 },
          itemStyle: { color: colors[i % colors.length] }
        };
      })
    }]
  });
}
async function loadAIOp(){
  var spot=document.getElementById('ops').value;
  if(!spot){alert('请选择景点');return}

  // 复用现有的 ai-op-result 卡片（不破坏页面其他部分）
  var old=document.getElementById('ai-op-result');
  if(old) old.remove();

  var newCard=document.createElement('div');
  newCard.className='card';
  newCard.id='ai-op-result';
  newCard.innerHTML='<div class="loading"><div class="spinner"></div>🤖 AI 运营报告生成中（数据较多，约15秒）...</div>';
  document.getElementById('or').appendChild(newCard);

  // 并行请求三个接口
  var results=await Promise.all([
    api('/api/spot/'+encodeURIComponent(spot)),
    api('/api/ai_operation_model?spot_name='+encodeURIComponent(spot)),
    api('/api/ai_insight?spot_name='+encodeURIComponent(spot))
  ]);

  var spotData=results[0]||{};
  var aiOpData=results[1]||{};
  var aiInsightData=results[2]||{};

  var el=document.getElementById('ai-op-result');
  if(!el)return;

  if(!aiOpData||!aiOpData.content){
    el.innerHTML='<div style="padding:20px;color:var(--red)">AI 运营报告生成失败，请重试</div>';
    return;
  }

  // 提取数据
  var avgScore=spotData.avg_score||0;
  var positiveRate=spotData.positive_rate||0;
  var negativeRate=spotData.negative_rate||0;
  var totalComments=spotData.total_comments||0;
  var scoreDist=spotData.score_distribution||{};
  var wordcloud=spotData.wordcloud||[];
  var topWords=wordcloud.slice(0,10).map(function(w){return w.name});
  var highlights=aiInsightData.highlights||[];
  var improvements=aiInsightData.improvements||[];

  // 热度趋势
  var trend=spotData.trend||[];
  var trendHtml='';
  if(trend.length>=2){
    var last=trend[trend.length-1];
    var prev=trend[trend.length-2];
    var diff=last.count-prev.count;
    if(diff>0){
      trendHtml='<span style="color:var(--green);font-weight:600">📈 近两月评论量增长 '+diff+' 条，热度上升</span>';
    } else if(diff<0){
      trendHtml='<span style="color:var(--orange);font-weight:600">📉 近两月评论量下降 '+Math.abs(diff)+' 条，需关注</span>';
    } else {
      trendHtml='<span style="color:var(--t2)">📊 近两月评论量持平</span>';
    }
  }

  // 评分分布最大值（用于条形图归一化）
  var maxDist=0;
  [1,2,3,4,5].forEach(function(s){
    var v=scoreDist[s]||0;
    if(v>maxDist) maxDist=v;
  });
  if(maxDist===0) maxDist=1;

  // 构建 HTML
  var html='';

  // ===== 头部 =====
  html+='<div class="card-head">'
    +'<div class="ch-left"><span class="ch-icon" style="background:rgba(0,212,170,.1)">🤖</span><span class="ch-title">'+spot+' AI 运营诊断报告</span></div>'
    +aiBadge(aiOpData)
    +'</div>';

  html+='<div class="aiop-body">';

  // ===== 1. 四指标卡 =====
  html+='<div class="aiop-metrics-row">'
    +'<div class="aiop-metric aiop-metric-blue"><div class="aiop-metric-val">'+avgScore+'</div><div class="aiop-metric-label">平均评分</div></div>'
    +'<div class="aiop-metric aiop-metric-green"><div class="aiop-metric-val">'+positiveRate+'%</div><div class="aiop-metric-label">好评率</div></div>'
    +'<div class="aiop-metric aiop-metric-orange"><div class="aiop-metric-val">'+negativeRate+'%</div><div class="aiop-metric-label">差评率</div></div>'
    +'<div class="aiop-metric aiop-metric-purple"><div class="aiop-metric-val">'+totalComments.toLocaleString()+'</div><div class="aiop-metric-label">评论总数</div></div>'
    +'</div>';

  // ===== 2. 评分分布 =====
  html+='<div class="aiop-section">'
    +'<div class="aiop-section-title">⭐ 评分分布</div>'
    +'<div class="aiop-score-dist">';
  [5,4,3,2,1].forEach(function(s){
    var cnt=scoreDist[s]||0;
    var pct=(cnt/maxDist*100).toFixed(0);
    var color=s>=4?'var(--green)':(s===3?'#fbbf24':'var(--red)');
    html+='<div class="aiop-score-item">'
      +'<div class="aiop-score-label">'+s+'分</div>'
      +'<div class="aiop-score-bar-wrap"><div class="aiop-score-bar-fill" style="width:'+pct+'%;background:'+color+'"></div></div>'
      +'<div class="aiop-score-val">'+cnt+'</div>'
      +'</div>';
  });
  html+='</div></div>';

  // ===== 3. 热度趋势 =====
  if(trendHtml){
    html+='<div class="aiop-section">'
      +'<div class="aiop-section-title">📈 热度趋势</div>'
      +'<div class="aiop-trend-text">'+trendHtml+'</div>'
      +'</div>';
  }

  // ===== 4. 高频评价词 =====
  if(topWords.length>0){
    html+='<div class="aiop-section">'
      +'<div class="aiop-section-title">🏷️ 游客高频评价词</div>'
      +'<div class="aiop-kw-tags">'
      +topWords.map(function(w){return '<span class="aiop-kw-tag">'+w+'</span>'}).join('')
      +'</div></div>';
  }

  // ===== 5. AI 亮点 + 待改进 双栏 =====
  if(highlights.length>0||improvements.length>0){
    html+='<div class="aiop-insight-twocol">';
    html+='<div class="aiop-insight-col aiop-insight-pos">'
      +'<div class="aiop-insight-title">✅ 亮点</div>'
      +'<ul class="aiop-insight-list">'
      +(highlights.length?highlights.map(function(h){return '<li>'+h+'</li>'}).join(''):'<li style="opacity:.5">暂无</li>')
      +'</ul></div>';
    html+='<div class="aiop-insight-col aiop-insight-neg">'
      +'<div class="aiop-insight-title">⚠️ 待改进</div>'
      +'<ul class="aiop-insight-list">'
      +(improvements.length?improvements.map(function(i){return '<li>'+i+'</li>'}).join(''):'<li style="opacity:.5">暂无</li>')
      +'</ul></div>';
    html+='</div>';
  }

  // ===== 6. AI 深度运营报告（markdown） =====
  html+='<div class="aiop-section aiop-report-section">'
    +'<div class="aiop-section-title">📋 AI 深度运营分析</div>'
    +'<div class="ai-result">'+md(aiOpData.content)+'</div>'
    +'</div>';

  html+='</div>'; // /aiop-body

  el.innerHTML=html;
}
async function loadKeywordSentimentChart(){
  var el=document.getElementById('keywordSentimentChart');
  if(!el)return;

  var sp=document.getElementById('globalSpotSelect') ? document.getElementById('globalSpotSelect').value : '';
  var url='/api/keyword_sentiment_heatmap?top_n=60';
  if(sp) url+='&spot_name='+encodeURIComponent(sp);

  var data=await api(url);
  var c=mk('keywordSentimentChart');
  if(!c)return;

  if(!data||!data.length){
    c.clear();
    el.innerHTML='<div class="loading"><p style="color:var(--t3)">暂无关键词情感数据</p></div>';
    return;
  }

  var sorted=data.slice().sort(function(a,b){return (a.frequency||0)-(b.frequency||0)});
  var maxFreq=Math.max.apply(null,sorted.map(function(d){return d.frequency||0}).concat([1]));

  // 让相同坐标的点稍微错开
  function hashOffset(word,scale){
    var h=0;
    for(var i=0;i<word.length;i++) h=(h*31+word.charCodeAt(i))%9973;
    return ((h%200)-100)/100*scale;
  }

  var plotData=sorted.map(function(d,idx){
    var freq=d.frequency||0;
    var posRate=Number(d.positive_rate);
    if(isNaN(posRate)) posRate=70;  // 兜底
    var avgScore=Number(d.avg_score||3);
    var word=d.keyword||'';
    // Y 轴加点扰动，避免完全重叠
    var y=posRate+hashOffset(word+'y',1.8);
    y=Math.max(1,Math.min(99,y));
    // data 结构: [x索引, y好评率, 词名, 词频, 平均分, idx, 是否显示标签, 真实好评率]
    return [idx+1, y, word, freq, avgScore, idx, 0, posRate];
  });

  // 智能挑 ~7 个点显示标签（避免拥挤）
  var labelSlots=[];
  plotData.slice().sort(function(a,b){return b[3]-a[3]}).forEach(function(pt){
    var farEnough=labelSlots.every(function(o){
      return Math.abs(o[0]-pt[0])>=7 || Math.abs(o[1]-pt[1])>=12;
    });
    if(labelSlots.length<7 && farEnough){
      pt[6]=1;
      labelSlots.push(pt);
    }
  });

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{
      trigger:'item',
      formatter:function(p){
        return '<b>'+p.data[2]+'</b>'
          +'<br/>词频：'+p.data[3]
          +'<br/>好评率：'+p.data[7]+'%'
          +'<br/>平均情感分：'+p.data[4];
      },
      backgroundColor:tt.backgroundColor,
      borderColor:tt.borderColor,
      textStyle:tt.textStyle
    },
    grid:{left:'8%',right:'10%',top:'10%',bottom:'14%'},
    xAxis:{
      type:'value',
      name:'关键词（按词频排序）',
      min:0,
      max:plotData.length+1,
      nameTextStyle:{color:css('--t2')},
      axisLabel:{color:css('--t2'),formatter:function(v){return Number.isInteger(v)&&v>0?v:''}},
      splitLine:{lineStyle:{color:css('--border')}}
    },
    yAxis:{
      type:'value',
      name:'好评率 (%)',
      min:0,
      max:100,
      interval:20,
      nameTextStyle:{color:css('--t2')},
      axisLabel:{color:css('--t2'),formatter:'{value}%'},
      splitLine:{lineStyle:{color:css('--border')}}
    },
    visualMap:{
      show:true,
      right:8,
      top:20,
      min:0,
      max:100,
      dimension:7,                          // 用第 7 维（真实好评率）映射颜色
      text:['好评多','差评多'],
      textStyle:{color:css('--t2')},
      inRange:{color:['#ef4444','#fb923c','#fbbf24','#34d399','#10b981']},
      calculable:false
    },
    series:[{
      type:'scatter',
      data:plotData,
      symbolSize:function(d){
        return Math.min(46,Math.max(10,Math.sqrt(d[3]/maxFreq)*46));
      },
      itemStyle:{opacity:.88,shadowBlur:8,shadowColor:'rgba(0,0,0,.25)'},
      emphasis:{
        focus:'series',
        label:{
          show:true,
          formatter:function(p){return p.data[2]},
          position:'top',
          distance:8,
          color:css('--t1'),
          fontSize:15,
          fontWeight:'bold'
        }
      },
      label:{
        show:true,
        formatter:function(p){return p.data[6]?p.data[2]:''},
        position:'top',
        distance:8,
        color:css('--t1'),
        fontSize:12,
        fontWeight:'bold'
      },
      labelLayout:{hideOverlap:true,moveOverlap:'shiftY'},
      // 0-50% 之间画分隔线，提示"争议区"
      markLine:{
        silent:true,
        symbol:'none',
        lineStyle:{color:'#fbbf24',type:'dashed',width:1,opacity:.5},
        label:{formatter:'争议线 50%',color:css('--t3'),fontSize:10,position:'end'},
        data:[{yAxis:50}]
      }
    }]
  });
}
async function loadNegativeModel(scope,spotName){
  scope=scope||'overall';
  spotName=spotName||'';

  var chartId=scope==='detail'?'detailNegativeChart':'overallNegativeChart';
  var tableId=scope==='detail'?'detailNegativeTable':'overallNegativeTable';

  var chartEl=document.getElementById(chartId);
  var tableEl=document.getElementById(tableId);
  if(!chartEl)return;

  if(tableEl){
    tableEl.innerHTML='<div class="loading" style="padding:18px"><div class="spinner"></div>失望原因模型计算中...</div>';
  }

  var url='/api/negative_model?top_n=8';
  if(spotName) url+='&spot_name='+encodeURIComponent(spotName);

  var resp=await api(url);
  var c=mk(chartId);
  if(!c)return;

  var items=(resp&&resp.items)?resp.items:[];
  var summary=(resp&&resp.summary)?resp.summary:{};

  if(!items.length){
    c.clear();
    if(tableEl){
      tableEl.innerHTML='<div class="loading" style="padding:18px"><p style="color:var(--t3)">暂无足够数据进行回归诊断</p></div>';
    }
    return;
  }

  var negItems=items.filter(function(d){return d.impact>0});
  var showItems=(negItems.length?negItems:items).slice(0,8).reverse();

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{
      trigger:'axis',
      axisPointer:{type:'shadow'},
      backgroundColor:tt.backgroundColor,
      borderColor:tt.borderColor,
      textStyle:tt.textStyle,
      formatter:function(ps){
        var d=ps[0].data.raw;
        return '<b>'+d.factor+'</b><br/>类别：'+d.category+'<br/>β系数：'+d.coef+'<br/>出现率：'+d.occurrence_pct+'%<br/>影响分：'+d.impact+'<br/>建议：'+d.advice;
      }
    },
    grid:{left:'16%',right:'8%',top:'8%',bottom:'10%'},
    xAxis:{
      type:'value',
      name:'综合影响分',
      nameTextStyle:{color:css('--t2')},
      axisLabel:{color:css('--t2')},
      splitLine:{lineStyle:{color:css('--border')}}
    },
    yAxis:{
      type:'category',
      data:showItems.map(function(d){return d.factor}),
      axisLabel:{color:css('--t1'),fontSize:12}
    },
    series:[{
      type:'bar',
      barWidth:'52%',
      data:showItems.map(function(d){
        return{
          value:d.impact,
          raw:d,
          itemStyle:{
            color:new echarts.graphic.LinearGradient(0,0,1,0,[
              {offset:0,color:'#ef4444'},
              {offset:1,color:'#fb923c'}
            ]),
            borderRadius:[0,8,8,0]
          }
        };
      }),
      label:{
        show:true,
        position:'right',
        color:css('--orange'),
        fontWeight:'bold',
        formatter:function(p){return p.value;}
      }
    }]
  });
    // ===== 填充失望诊断右侧的 AI 优化建议（仅 detail 视图）=====
  if(scope==='detail'){
    var adviceEl=document.getElementById('diagAdviceList');
    if(adviceEl){
      var adviceItems=items.filter(function(d){return d.impact>0&&d.advice}).slice(0,5);
      if(adviceItems.length===0){
        adviceEl.innerHTML='<div style="text-align:center;padding:20px;color:var(--t3);font-size:12px">✓ 当前未检测到显著问题</div>';
      } else {
        var icons=['💰','👥','🏗️','🛎️','🎫','📍','🌳','⚙️'];
        adviceEl.innerHTML=adviceItems.map(function(d,i){
          return '<div class="diag-advice-item">'
            +'<div class="diag-advice-icon">'+icons[i%icons.length]+'</div>'
            +'<div style="flex:1"><div style="font-weight:600;color:var(--t1);margin-bottom:3px;font-size:12px">'+d.factor+'</div>'
            +'<div style="font-size:11px;color:var(--t2);line-height:1.5">'+d.advice+'</div>'
            +'</div></div>';
        }).join('');
      }
    }
  }
  if(tableEl){
    var title=scope==='detail'
      ?'样本：'+(summary.sample_size||0)+'条，当前均分：'+(summary.avg_score||'-')
      :'样本：'+(summary.sample_size||0)+'条，总体均分：'+(summary.avg_score||'-');

    tableEl.innerHTML=
      '<div style="font-size:12px;color:var(--t3);margin:10px 0 12px">'+title+'；综合影响分 = |β| × 出现率</div>'
      +'<div class="table-wrap"><table class="data-table"><thead><tr><th>优先级</th><th>槽点</th><th>β系数</th><th>出现率</th><th>影响分</th><th>建议</th></tr></thead><tbody>'
      +items.slice(0,6).map(function(d){
        return '<tr>'
          +'<td><span class="rank-badge '+(d.impact>0?'rk3':'rko')+'">'+d.priority+'</span></td>'
          +'<td><strong>'+d.factor+'</strong><div style="font-size:11px;color:var(--t3);margin-top:3px">'+d.keywords+'</div></td>'
          +'<td style="color:'+(d.coef<0?'var(--red)':'var(--green)')+';font-weight:700">'+d.coef+'</td>'
          +'<td>'+d.occurrence_pct+'%</td>'
          +'<td style="color:var(--orange);font-weight:700">'+d.impact+'</td>'
          +'<td style="color:var(--t2);line-height:1.5">'+d.advice+'</td>'
          +'</tr>';
      }).join('')
      +'</tbody></table></div>';
  }
    // ✨ 失望诊断渲染完后，同步真实声音高度
  if(scope==='detail'){
    setTimeout(syncVoiceHeight, 300);
  }
}
async function loadAIInsight(spot){
  var hl=document.getElementById('hiHighlights');
  var im=document.getElementById('hiImprovements');
  if(!hl||!im)return;

  var data=await api('/api/ai_insight?spot_name='+encodeURIComponent(spot));
  if(!data){
    if(hl) hl.innerHTML='<div class="hi-loading">加载失败</div>';
    if(im) im.innerHTML='<div class="hi-loading">加载失败</div>';
    return;
  }

  var highlights=data.highlights||[];
  var improvements=data.improvements||[];

  if(highlights.length){
    hl.innerHTML=highlights.map(function(t){
      return '<div><span style="color:#34d399;flex-shrink:0">✓</span><span>'+t+'</span></div>';
    }).join('');
  } else {
    hl.innerHTML='<div class="hi-loading">暂无亮点数据</div>';
  }

  if(improvements.length){
    im.innerHTML=improvements.map(function(t){
      return '<div><span style="color:#fbbf24;flex-shrink:0">⚠</span><span>'+t+'</span></div>';
    }).join('');
  } else {
    im.innerHTML='<div class="hi-loading">暂无待改进数据</div>';
  }
}

async function loadDBStatus(){
  // 更新时间
  var timeEl=document.getElementById('updateTime');
  if(timeEl){
    var now=new Date();
    timeEl.textContent=now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')+' '+String(now.getHours()).padStart(2,'0')+':'+String(now.getMinutes()).padStart(2,'0');
  }

  // 数据库状态（独立的span，不覆盖版权）
  try{
    var data=await api('/api/db_status');
    var dbEl=document.getElementById('dbStatusInfo');
    if(dbEl){
      if(data){
        var mode=data.connected?'🟢 MySQL':'🟡 CSV';
        var total=data.total?data.total.toLocaleString():'--';
        dbEl.innerHTML=mode+' · 数据量：<strong>'+total+'</strong> 条';
      } else {
        dbEl.innerHTML='🔴 数据库未连接';
      }
    }
  } catch(e){
    console.error('loadDBStatus error:',e);
  }
}

async function loadDetail(){
  var spot=document.getElementById('ds').value;
  if(!spot)return;
  document.getElementById('dr').innerHTML='<div class="loading"><div class="spinner"></div>分析中...</div>';
  var d=await api('/api/spot/'+encodeURIComponent(spot));
  if(!d){document.getElementById('dr').innerHTML='<div class="loading"><p>未找到</p></div>';return}

  var cv=d.competitiveness||{};
  var img=SPOT_IMAGES[spot]||'/static/景点照片/spot1.png';
  var intro=SPOT_INTRO[spot]||{type:'文化景点',desc:['暂无介绍']};
  var model3D=SPOT_3D_MODELS[spot];
  var stars='';
  var roundedScore=Math.round(d.avg_score);
  for(var si=0;si<5;si++) stars+='<span class="star'+(si<roundedScore?'':' off')+'">'+(si<roundedScore?'★':'☆')+'</span>';
  var typeIcon=intro.type==='自然景点'?'🌲':intro.type==='休闲娱乐'?'🎪':'🏛️';
  var meta=(typeof SPOT_META!=='undefined'&&SPOT_META[spot])?SPOT_META[spot]:{level:'AAAAA级',duration:'2-3小时',bestTime:'春秋季节',openTime:'08:00-22:00',address:'西安市'};

  var html='';

  // ========== 第一行：Hero 区（图+洞察合并卡 | 综合评分） ==========
  html+='<div class="detail-hero">';

  // 图+洞察 合并卡
  html+='<div class="hero-merge-card">';

  // 左半：图
  html+='<div class="hero-img-half">'
    +'<img class="hero-img" src="'+img+'" alt="'+spot+'" onerror="this.src=\'/static/景点照片/spot1.png\'">'
    +'<div class="hero-img-overlay">'
    +'<div class="hero-name-row">'
    +(model3D?'<button class="hero-name hero-name-3d" type="button" onclick="openSpot3DModel()" aria-label="点击查看'+spot+'的3D模型">'+spot+' <span aria-hidden="true">🧊</span></button>':'<span class="hero-name">'+spot+'</span>')
    +'<span class="hero-type-badge">'+typeIcon+' '+intro.type+'</span></div>'
    +(model3D?'<div class="hero-3d-hint">点击景点名称，查看可交互 3D 模型</div>':'')
    +'<div class="hero-addr">📍 '+meta.address+'</div>'
    +'<div class="hero-meta-row">'
    +'<div class="hero-meta-item"><div class="hmi-label">景区等级</div><div class="hmi-value">'+meta.level+'</div></div>'
    +'<div class="hero-meta-item"><div class="hmi-label">建议游玩时长</div><div class="hmi-value">'+meta.duration+'</div></div>'
    +'<div class="hero-meta-item"><div class="hmi-label">最佳游览时间</div><div class="hmi-value">'+meta.bestTime+'</div></div>'
    +'<div class="hero-meta-item"><div class="hmi-label">开放时间</div><div class="hmi-value">'+meta.openTime+'</div></div>'
    +'</div>'
    +'</div>'
    +'</div>';

  // 右半：AI洞察
  html+='<div class="hero-insight-half" id="heroInsight">'
    +'<div class="hi-head"><span class="hi-title">AI 智能洞察</span><span class="hi-spark">✨</span></div>'
    +'<div class="hi-desc">'+(intro.desc[0]||'暂无介绍')+'</div>'
    +'<div class="hi-twocol">'
    +'<div class="hi-col"><div class="hi-col-title pos">🌟 亮点总结</div><div class="hi-col-list" id="hiHighlights"><div class="hi-loading">分析中...</div></div></div>'
    +'<div class="hi-col"><div class="hi-col-title neg">⚠️ 待改进点</div><div class="hi-col-list" id="hiImprovements"><div class="hi-loading">分析中...</div></div></div>'
    +'</div>'
    +'</div>';

  html+='</div>'; // /hero-merge-card

  // 综合评分
    // 右：综合评分卡（水平条 + 排名）
  var posRate=d.positive_rate||0;
  var negRate=d.negative_rate||0;
  var neuRate=Math.max(0,(100-posRate-negRate)).toFixed(1);

  html+='<div class="hero-score-card">'
    +'<div class="hs-title">综合评分 <span class="hs-info">ⓘ</span></div>'
    +'<div class="hs-big-num">'+d.avg_score+' <span class="hs-big-denom">/ 5</span></div>'
    +'<div class="hs-stars">'+stars+'</div>'
    +'<div class="hs-base">基于 '+d.total_comments.toLocaleString()+' 条游客评价</div>'
    +'<div class="hs-bars">'
    +'<div class="hs-bar-row"><span class="hs-bar-label">好评</span><div class="hs-bar-track"><div class="hs-bar-fill pos" style="width:'+posRate+'%"></div></div><span class="hs-bar-val pos">'+posRate+'%</span></div>'
    +'<div class="hs-bar-row"><span class="hs-bar-label">中性</span><div class="hs-bar-track"><div class="hs-bar-fill neu" style="width:'+neuRate+'%"></div></div><span class="hs-bar-val neu">'+neuRate+'%</span></div>'
    +'<div class="hs-bar-row"><span class="hs-bar-label">差评</span><div class="hs-bar-track"><div class="hs-bar-fill neg" style="width:'+negRate+'%"></div></div><span class="hs-bar-val neg">'+negRate+'%</span></div>'
    +'</div>'
    +'<div class="hs-rank-row">'
    +'<div class="hs-rank-item"><span class="hs-rank-label">评论量排名</span><span class="hs-rank-val">'+(cv.comment_rank||'-')+'</span></div>'
    +'<div class="hs-rank-item"><span class="hs-rank-label">评分排名</span><span class="hs-rank-val">'+(cv.score_rank||'-')+'</span></div>'
    +'</div>'
    +'</div>';

  html+='</div>'; // /detail-hero

  // 模型弹窗默认不加载，点击景点名称后再打开
  if(model3D){
    html+='<div class="sketchfab-modal" id="spot3DModal" role="dialog" aria-modal="true" aria-hidden="true" aria-label="'+spot+' 3D 模型" hidden>'
      +'<div class="sketchfab-backdrop" onclick="closeSpot3DModel()"></div>'
      +'<div class="sketchfab-dialog">'
      +'<div class="sketchfab-toolbar"><div class="sketchfab-modal-title">'+spot+' 3D 模型</div>'
      +'<a class="sketchfab-source" href="'+model3D.url+'" target="_blank" rel="noopener noreferrer">模型来源：Sketchfab ↗</a>'
      +'<div class="sketchfab-actions"><button type="button" onclick="fullscreenSpot3DModel()" aria-label="全屏观看3D模型">⛶ 全屏</button><button type="button" class="sketchfab-close" onclick="closeSpot3DModel()" aria-label="关闭3D模型">✕</button></div></div>'
      +'<div class="sketchfab-frame-wrap"><iframe class="sketchfab-frame" data-model-id="'+model3D.id+'" title="'+spot+' 3D 模型（Sketchfab）" src="about:blank" allow="autoplay; fullscreen; xr-spatial-tracking" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe></div>'
      +'<div class="sketchfab-modal-hint">拖动旋转模型，滚轮缩放；点击“全屏”可全屏观看</div>'
      +'</div></div>';
  }

  // ========== 第二行：热度趋势 + 高频词云 ==========
    var trendDateHint = dataMaxDate ? '<span style="font-size:11px;color:var(--t3);margin-left:8px">📅 数据更新至 '+dataMaxDate+'</span>' : '';
    html+='<div class="detail-row-2-equal">';

    // 热度趋势
    html+='<div class="card">'
      +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(251,146,60,.1)">📈</span><span class="ch-title">热度趋势</span>'+trendDateHint+'</div></div>'
      +'<div class="time-control" style="margin-bottom:8px">'
      +'<div class="time-control-right" style="flex:1;justify-content:flex-start;gap:4px">'
      +'<input type="date" class="date-pick-input" id="trendDateStart" style="font-size:11px">'
      +'<input type="date" class="date-pick-input" id="trendDateEnd" style="font-size:11px">'
      +'<button class="date-pick-btn primary" onclick="applyTrendDate()" style="padding:4px 10px;font-size:11px">筛选</button>'
      +'</div></div>'
      +'<div class="chart-box" id="trendChart" style="height:340px"></div>'
      +'</div>';

    // 高频词云
    html+='<div class="card">'
      +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(167,139,250,.1)">☁️</span><span class="ch-title">高频词云</span></div></div>'
      +'<div class="chart-box" id="dwc" style="height:430px"></div>'
      +'</div>';

    html+='</div>'; // /detail-row-2-equal

    // ========== 第三行：能力雷达 + 游客画像 ==========
    html+='<div class="detail-row-2-equal">';

    // 景点能力雷达
    html+='<div class="card">'
      +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(181,152,212,.1)">🎯</span><span class="ch-title">能力雷达</span></div></div>'
      +'<div class="detail-radar-wrap">'
      +'<div class="chart-box" id="detailRadarChart" style="height:380px"></div>'
      +'<div class="radar-score-list" id="radarScoreList"></div>'
      +'</div>'
      +'</div>';

    // 游客画像
    html+='<div class="card">'
      +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(0,212,170,.1)">👥</span><span class="ch-title">游客画像</span></div></div>'
      +'<div class="portrait-row-2-wrap">'
      +'<div id="portraitDonut" class="portrait-donut" style="height:220px;width:100%"></div>'
      +'<div class="portrait-main-cluster" id="portraitMainCluster"></div>'
      +'<div class="portrait-side-info">'
      +'<div class="psi-row"><div class="psi-label">🎯 关注重点</div><div class="psi-content" id="portraitFocus"></div></div>'
      +'<div class="psi-row"><div class="psi-label">📱 信息渠道</div><div class="psi-content" id="portraitChannels"></div></div>'
      +'</div>'
      +'</div>'
      +'</div>';

    html+='</div>'; // /detail-row-2-equal

  // ========== 第三行：真实声音 + 失望诊断（1:2） ==========
  html+='<div class="detail-row-3">';

  // 左：真实声音
  html+='<div class="card detail-voice-card">'
    +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(52,211,153,.1)">💬</span><span class="ch-title">游客真实声音</span></div><span class="ch-badge">AI提炼</span></div>'
    +'<div id="voiceContent" class="voice-twocol-scroll">'
    +'<div class="voice-col"><div class="voice-col-title pos"> 好评精选</div><div id="voicePos" class="voice-list"><div class="hi-loading">加载中...</div></div></div>'
    +'<div class="voice-col"><div class="voice-col-title neg"> 差评精选</div><div id="voiceNeg" class="voice-list"><div class="hi-loading">加载中...</div></div></div>'
    +'</div>'
    +'</div>';

  // 右：失望诊断+AI建议
  html+='<div class="card detail-diag-card">'
    +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(239,68,68,.1)">⚠️</span><span class="ch-title">失望原因诊断</span></div><span class="ch-badge">线性回归</span></div>'
    +'<div class="diag-twocol">'
    +'<div class="diag-chart-col"><div class="chart-box" id="detailNegativeChart" style="width:100%;height:100%;min-height:300px"></div></div>'
    +'<div class="diag-advice-col"><div class="diag-advice-title">💡 AI 优化建议</div><div id="diagAdviceList" class="diag-advice-list"></div></div>'
    +'</div>'
    +'<div id="detailNegativeTable" style="display:none"></div>'
    +'</div>';

  html+='</div>'; // /detail-row-3

  // ========== AI差评智能回复 ==========
  html+='<div class="card">'
    +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(244,114,182,.1)">💬</span><span class="ch-title">AI差评智能回复</span></div><span class="ch-badge">客服助手</span></div>'
    +'<div class="reply-helper">'
    +'<div class="reply-input-area">'
    +'<textarea id="reviewText" class="reply-textarea" placeholder="粘贴一条游客差评内容...&#10;&#10;例如：&quot;华清宫的工作人员态度很差，排队两小时进去就看了一池水，门票还贵&quot;"></textarea>'
    +'<div class="reply-controls">'
    +'<label>评分</label>'
    +'<select id="reviewScore"><option value="1">1分(极差)</option><option value="2" selected>2分(差)</option><option value="3">3分(一般)</option></select>'
    +'<button class="reply-btn" id="genReplyBtn" onclick="genAIReply()">🤖 生成回复</button>'
    +'</div>'
    +'</div>'
    +'<div class="reply-result" id="replyResult"></div>'
    +'</div>'
    +'</div>';

  // ========== AI深度分析报告 ==========
  html+='<div class="card">'
    +'<div class="card-head"><div class="ch-left"><span class="ch-icon" style="background:rgba(167,139,250,.1)">🤖</span><span class="ch-title">AI深度分析报告</span></div>'
    +'<button class="btn btn-ai" onclick="loadAISpot()" style="padding:6px 14px;font-size:12px">🤖 生成报告</button></div>'
    +'<div id="aiReportBody"><div style="padding:30px;text-align:center;color:var(--t3)">点击右上角"生成报告"按钮，AI 将基于评论数据生成深度分析</div></div>'
    +'</div>';

  document.getElementById('dr').innerHTML=html;

    // 默认热度趋势：以数据最新日期为终点，往前一年
  function fmt(d){
    return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
  }

  var endDate, startDate;
  if(dataMaxDate){
    endDate = new Date(dataMaxDate);
  } else {
    endDate = new Date();
  }
  startDate = new Date(endDate);
  startDate.setFullYear(endDate.getFullYear() - 1);

  var s = document.getElementById('trendDateStart');
  var e = document.getElementById('trendDateEnd');
  if(s) s.value = fmt(startDate);
  if(e) e.value = fmt(endDate);
  setTimeout(function(){
    if(d.wordcloud&&d.wordcloud.length)mkW('dwc',d.wordcloud);
  },200);

  loadSpotTrend(spot);
  loadDetailAgeChart(spot);
  loadNegativeModel('detail',spot);
  loadAIKW(spot);
  loadAIInsight(spot);
  loadDetailRadar(spot);
}
// ===== 深度分析页 - 景点能力雷达 =====
async function loadDetailRadar(spotName){
  if(!spotName) return;

  var data = await api('/api/capability_radar?spots=' + encodeURIComponent(spotName));
  if(!data || !data.length) return;

  var spotData = data[0];
  var dimensions = ['服务质量', '卫生环境', '设施完善', '性价比', '文化体验', '人流管理'];

  // 渲染雷达图
  var c = mk('detailRadarChart');
  if(c){
    c.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        backgroundColor: tt.backgroundColor,
        borderColor: tt.borderColor,
        textStyle: tt.textStyle,
        formatter: function(p){
          var html = '<b>' + p.name + '</b><br/>';
          dimensions.forEach(function(d, i){
            html += d + ': ' + p.value[i] + '<br/>';
          });
          return html;
        }
      },
      radar: {
        indicator: dimensions.map(function(d){ return { name: d, max: 100 } }),
        center: ['50%', '52%'],
        radius: '68%',
        shape: 'polygon',
        splitNumber: 4,
        axisName: {
          color: css('--t1'),
          fontSize: 12,
          fontWeight: 600
        },
        splitLine: { lineStyle: { color: css('--border') } },
        splitArea: {
          areaStyle: {
            color: ['rgba(255,255,255,0)', 'rgba(181,152,212,.04)', 'rgba(255,255,255,0)', 'rgba(181,152,212,.04)']
          }
        },
        axisLine: { lineStyle: { color: css('--border') } }
      },
      series: [{
        type: 'radar',
        data: [{
          name: spotName,
          value: dimensions.map(function(d){ return spotData.scores[d] || 0 }),
          lineStyle: { color: '#b598d4', width: 2.5 },
          areaStyle: { color: '#b598d4', opacity: 0.2 },
          itemStyle: { color: '#b598d4' }
        }]
      }]
    });
  }

  // 渲染右侧得分列表
  var listEl = document.getElementById('radarScoreList');
  if(listEl){
    var avgScore = spotData.avg_score || 0;

    // 找最高和最低
    var sortedDims = dimensions.slice().sort(function(a, b){
      return (spotData.scores[b] || 0) - (spotData.scores[a] || 0);
    });
    var bestDim = sortedDims[0];
    var worstDim = sortedDims[sortedDims.length - 1];

    var html = '<div class="rsl-summary">';
    html += '<div class="rsl-avg">综合能力 <strong>' + avgScore + '</strong> 分</div>';
    html += '<div class="rsl-tags">';
    html += '<span class="rsl-tag best">✨ 强项：' + bestDim + ' (' + (spotData.scores[bestDim] || 0) + ')</span>';
    html += '<span class="rsl-tag worst">⚠️ 短板：' + worstDim + ' (' + (spotData.scores[worstDim] || 0) + ')</span>';
    html += '</div>';
    html += '</div>';

    html += '<div class="rsl-items">';
    dimensions.forEach(function(d){
      var score = spotData.scores[d] || 0;
      var level = score >= 80 ? '优秀' : (score >= 65 ? '良好' : (score >= 50 ? '中等' : '待提升'));
      var cls = score >= 80 ? 'high' : (score >= 65 ? 'mid' : 'low');
      html += '<div class="rsl-item">';
      html += '<div class="rsl-name">' + d + '</div>';
      html += '<div class="rsl-bar"><div class="rsl-bar-fill ' + cls + '" style="width:' + score + '%"></div></div>';
      html += '<div class="rsl-score">' + score + '</div>';
      html += '<div class="rsl-level ' + cls + '">' + level + '</div>';
      html += '</div>';
    });
    html += '</div>';

    listEl.innerHTML = html;
  }
}
// ============================================================
// ============ 完整排名页：双榜单 + 滑块控制 ============
// ============================================================

// 全局状态
var dualRankWeights = {mafengwo: 33, ctrip: 34, dianping: 33};
var dualRankCurrentTab = 'hot';  // 'hot' / 'quality'

// Tab 切换：热度榜 / 好评榜
function switchDualTab(target){
  dualRankCurrentTab = target;
  currentRankingMode = target;  // 同步全局状态

  // Tab 高亮
  var tabs = document.querySelectorAll('.dual-tab');
  tabs.forEach(function(t){ t.classList.remove('on') });
  var current = document.querySelector('.dual-tab[data-target="' + target + '"]');
  if(current) current.classList.add('on');

  // Pane 切换
  var hotPane = document.getElementById('dualHotPane');
  var qualityPane = document.getElementById('dualQualityPane');
  if(hotPane) hotPane.style.display = (target === 'hot' ? 'block' : 'none');
  if(qualityPane) qualityPane.style.display = (target === 'quality' ? 'block' : 'none');

  // 加载对应数据
  if(target === 'hot'){
    loadDualHotRanking();
  } else {
    loadDualQualityRanking();
  }

  // 轮播跟随切换
  var cardData = (target === 'quality') ? homeQualityData : homeHotData;
  if(cardData && cardData.length){
    renderFullRankings(cardData, window._lastOverview);
  }
}

// 加载热度榜（带权重）
async function loadDualHotRanking(){
  var w = dualRankWeights;
  var url = '/api/dual_rankings?type=hot'
    + '&mafengwo=' + w.mafengwo
    + '&ctrip=' + w.ctrip
    + '&dianping=' + w.dianping;
  var data = await api(url);
  if(!data) return;

  // 同步缓存
  data.forEach(function(d){ d.heat_index = d.heat_score });
  homeHotData = data;

  renderDualHotList(data);
}
// 加载好评榜
async function loadDualQualityRanking(){
  var data = await api('/api/dual_rankings?type=quality');
  if(!data) return;

  // 同步缓存
  homeQualityData = data;

  renderDualQualityList(data);
  loadHeatBar();
}
// 季节选择联动提示
document.addEventListener('change', function(e){
  if(e.target && e.target.id === 'planSeason'){
    var hint = document.getElementById('seasonHint');
    if(!hint) return;
    var val = e.target.value;
    if(val === '旺季'){
      hint.textContent = '⚠️ 旺季人流大，建议提前预约门票';
      hint.style.color = '#c97c5d';
    } else if(val === '淡季'){
      hint.textContent = '✓ 淡季游客少，性价比高';
      hint.style.color = '#6b8e6b';
    } else {
      hint.textContent = 'AI 将综合推荐最佳出行时间';
      hint.style.color = '';
    }
  }
});
// 渲染热度榜列表
function renderDualHotList(data){
  var tbody = document.getElementById('dualHotTbody');
  if(!tbody) return;
  var maxScore = data[0] ? data[0].heat_score : 100;
  tbody.innerHTML = data.map(function(item, i){
    var rk = i+1;
    var rkCls = rk<=3 ? 'rk'+rk : 'rko';
    var barW = (item.heat_score / maxScore * 100).toFixed(0);
    return '<tr onclick="goDetail(\''+item.spot_name+'\')">'
      +'<td><span class="rank-badge '+rkCls+'">'+rk+'</span></td>'
      +'<td><strong>'+item.spot_name+'</strong></td>'
      +'<td><span class="plat-tag plat-mfw">'+item.mafengwo.toLocaleString()+'</span></td>'
      +'<td><span class="plat-tag plat-ctp">'+item.ctrip.toLocaleString()+'</span></td>'
      +'<td><span class="plat-tag plat-dp">'+item.dianping.toLocaleString()+'</span></td>'
      +'<td><div style="display:flex;align-items:center;gap:8px">'
      +'<div class="heat-bar"><div class="heat-fill" style="width:'+barW+'%"></div></div>'
      +'<span style="color:var(--blue);font-weight:700;font-size:13px;min-width:40px">'+item.heat_score+'</span>'
      +'</div></td>'
      +'</tr>';
  }).join('');
}

// 渲染好评榜列表
function renderDualQualityList(data){
  var tbody = document.getElementById('dualQualityTbody');
  if(!tbody) return;
  var maxScore = data[0] ? data[0].quality_score : 100;

  tbody.innerHTML = data.map(function(item, i){
    var rk = i + 1;
    var rkCls = rk <= 3 ? 'rk' + rk : 'rko';
    var barW = (item.quality_score / maxScore * 100).toFixed(0);
    var scoreCls = item.avg_score >= 4 ? 's-high' : (item.avg_score >= 3 ? 's-mid' : 's-low');
    var negRate = item.negative_rate !== undefined ? item.negative_rate : 0;

    return '<tr onclick="goDetail(\'' + item.spot_name + '\')">'
      + '<td><span class="rank-badge ' + rkCls + '">' + rk + '</span></td>'
      + '<td><strong>' + item.spot_name + '</strong></td>'
      + '<td><span class="score-tag ' + scoreCls + '">' + item.avg_score + '</span></td>'
      + '<td style="color:var(--green);font-weight:600">' + item.positive_rate + '%</td>'
      + '<td>'
      + '<div class="neg-rate-cell" onmouseenter="loadNegTooltip(this,\'' + item.spot_name + '\')" onmouseleave="hideNegTooltip()">'
      + '<span class="neg-rate-val">' + negRate + '% <span class="neg-hint-icon">ⓘ</span></span>'
      + '</div></td>'
      + '<td>' + item.comment_count.toLocaleString() + '</td>'
      + '<td><div style="display:flex;align-items:center;gap:8px">'
      + '<div class="heat-bar"><div class="heat-fill" style="width:' + barW + '%;background:linear-gradient(90deg,#10b981,#34d399)"></div></div>'
      + '<span style="color:#10b981;font-weight:700;font-size:13px;min-width:40px">' + item.quality_score + '</span>'
      + '</div></td></tr>';
  }).join('');
}

// 滑块拖动事件
function onWeightSlide(platform, value){
  value = parseInt(value);
  dualRankWeights[platform] = value;

  // 另外两个平台
  var others = ['mafengwo','ctrip','dianping'].filter(function(p){ return p !== platform });
  var otherCurrent0 = dualRankWeights[others[0]];
  var otherCurrent1 = dualRankWeights[others[1]];
  var otherSum = otherCurrent0 + otherCurrent1;

  // 剩余空间
  var remaining = Math.max(0, 100 - value);

  if(otherSum === 0){
    // 两个都是0，平分
    dualRankWeights[others[0]] = Math.round(remaining / 2);
    dualRankWeights[others[1]] = remaining - dualRankWeights[others[0]];
  } else {
    // 按原比例缩放
    var ratio0 = otherCurrent0 / otherSum;
    dualRankWeights[others[0]] = Math.round(remaining * ratio0);
    dualRankWeights[others[1]] = remaining - dualRankWeights[others[0]];
  }

  // 确保非负
  if(dualRankWeights[others[0]] < 0) dualRankWeights[others[0]] = 0;
  if(dualRankWeights[others[1]] < 0) dualRankWeights[others[1]] = 0;

  // 总和校准
  var total = dualRankWeights.mafengwo + dualRankWeights.ctrip + dualRankWeights.dianping;
  if(total !== 100){
    dualRankWeights[others[1]] += (100 - total);
  }

  syncWeightUI();

  // 防抖刷新
  clearTimeout(window._weightDebounce);
  window._weightDebounce = setTimeout(function(){
    loadDualHotRanking();
    // 同步刷新首页热度榜
    if(currentRankingMode === 'hot'){
      api('/api/dual_rankings?type=hot&mafengwo=' + dualRankWeights.mafengwo
        + '&ctrip=' + dualRankWeights.ctrip
        + '&dianping=' + dualRankWeights.dianping).then(function(newData){
        if(newData){
          newData.forEach(function(d){ d.heat_index = d.heat_score });
          homeHotData = newData;
          renderCompactRankList(newData.slice(0, 5));
        }
      });
    }
  }, 300);
}

// 同步 3 个滑块和数字的显示
function syncWeightUI(){
  ['mafengwo','ctrip','dianping'].forEach(function(p){
    var slider = document.getElementById('slider_'+p);
    var label = document.getElementById('label_'+p);
    if(slider) slider.value = dualRankWeights[p];
    if(label) label.textContent = dualRankWeights[p] + '%';
  });
}

// 重置权重为均衡
function resetWeights(){
  dualRankWeights = {mafengwo: 33, ctrip: 34, dianping: 33};
  syncWeightUI();
  loadDualHotRanking();
}

// 初始化完整排名页
function initRankingsFullPage(){
  syncWeightUI();
  loadDualHotRanking();
}
// ===== 运营预警 Tooltip =====
function showAlertTooltip(el, comments){
  var tip = document.getElementById('alertGlobalTooltip');
  if(!tip){
    tip = document.createElement('div');
    tip.id = 'alertGlobalTooltip';
    document.body.appendChild(tip);
  }

  // 构建内容
  var html = '<div class="alert-tip-title">🔍 相关评论</div>';
  html += '<div class="alert-tip-list">';
  comments.slice(0, 5).forEach(function(c){
    var text = c.text || '';
    var keyword = c.keyword || '';
    // 高亮关键词
    if(keyword){
      var re = new RegExp('(' + keyword + ')', 'g');
      text = text.replace(re, '<mark>$1</mark>');
    }
    html += '<div class="alert-tip-item">';
    html += '<div class="alert-tip-dot"></div>';
    html += '<div class="alert-tip-text">' + text + '</div>';
    html += '</div>';
  });
  html += '</div>';
  tip.innerHTML = html;

  // 计算位置
  var rect = el.getBoundingClientRect();
  var tipW = 380;
  var left = rect.left;
  if(left + tipW > window.innerWidth - 10){
    left = window.innerWidth - tipW - 10;
  }
  if(left < 10) left = 10;

  var top = rect.bottom + 8;
  // 估算 tooltip 高度
  var estimatedH = Math.min(comments.length * 50 + 60, 320);
  if(top + estimatedH > window.innerHeight - 10){
    top = rect.top - estimatedH - 8;
    if(top < 10) top = 10;
  }

  tip.style.left = left + 'px';
  tip.style.top = top + 'px';
  tip.classList.add('show');
}

function hideAlertTooltip(){
  var tip = document.getElementById('alertGlobalTooltip');
  if(tip) tip.classList.remove('show');
}
async function init(){
  // 先取数据最新日期
  var dr = await api('/api/date_range');
  if(dr && dr.max){
    dataMaxDate = dr.max;
    console.log('数据最新日期:', dataMaxDate);
  }

  await loadRankings();
  var actionBar = document.getElementById('planActionBar');
  if(actionBar) actionBar.style.display = 'none';
  // 预加载西安 geojson
  if(!echarts.getMap||!echarts.getMap('xian')){
    var geoResp=await api('/api/xian_geojson');
    if(geoResp) echarts.registerMap('xian', geoResp);
  }

  setTimeout(function(){
    initPlanSpots();
    initGlobalSpotSelect();
    syncEngine();
    loadDBStatus();
    generateAllWC();
  }, 300);
}
init();
