industry_chains = {
    '新能源汽车': {
        'description': '全球新能源汽车市场快速增长，带动上下游产业链发展',
        'trend': '上升',
        'drivers': ['政策支持', '技术进步', '成本下降', '环保意识提升'],
        'challenges': ['电池原料价格波动', '充电基础设施不足', '补贴退坡'],
        'investment_themes': ['电池技术升级', '智能化', '轻量化', '换电模式'],
        'subsectors': ['整车制造', '动力电池', '电机电控', '零部件', '充电设备'],
        'characteristics': ['高增长', '政策驱动', '技术密集'],
        'key_metrics': ['销量增长率', '市占率', '毛利率', '研发投入'],
        'risks': ['政策风险', '技术路线变更', '竞争加剧'],
        'chain': {
            '上游': [
                {'name': '锂矿', 'companies': ['赣锋锂业', '天齐锂业', '盛新锂能'], 'symbol_map': {'赣锋锂业': '002460.SZ', '天齐锂业': '002566.SZ', '盛新锂能': '002240.SZ'}},
                {'name': '钴矿', 'companies': ['华友钴业', '寒锐钴业'], 'symbol_map': {'华友钴业': '603799.SS', '寒锐钴业': '300618.SZ'}},
                {'name': '镍矿', 'companies': ['青岛中程', '盛屯矿业'], 'symbol_map': {'青岛中程': '300208.SZ', '盛屯矿业': '600711.SS'}},
                {'name': '稀土', 'companies': ['北方稀土', '中国铝业'], 'symbol_map': {'北方稀土': '600111.SS', '中国铝业': '601600.SS'}},
                {'name': '铜箔', 'companies': ['诺德股份', '嘉元科技'], 'symbol_map': {'诺德股份': '600110.SS', '嘉元科技': '688388.SS'}},
                {'name': '隔膜', 'companies': ['恩捷股份', '星源材质'], 'symbol_map': {'恩捷股份': '002812.SZ', '星源材质': '300568.SZ'}},
                {'name': '电解液', 'companies': ['天赐材料', '新宙邦'], 'symbol_map': {'天赐材料': '002709.SZ', '新宙邦': '300037.SZ'}}
            ],
            '中游': [
                {'name': '动力电池', 'companies': ['宁德时代', '比亚迪', '国轩高科', '亿纬锂能'], 'symbol_map': {'宁德时代': '300750.SZ', '比亚迪': '002594.SZ', '国轩高科': '002074.SZ', '亿纬锂能': '300014.SZ'}},
                {'name': '电机电控', 'companies': ['汇川技术', '英威腾', '精进电动'], 'symbol_map': {'汇川技术': '300124.SZ', '英威腾': '002334.SZ'}},
                {'name': '电池管理系统', 'companies': ['均胜电子', '德赛西威', '欣旺达'], 'symbol_map': {'均胜电子': '600699.SS', '德赛西威': '002920.SZ', '欣旺达': '300207.SZ'}},
                {'name': '热管理', 'companies': ['三花智控', '银轮股份'], 'symbol_map': {'三花智控': '002050.SZ', '银轮股份': '002126.SZ'}}
            ],
            '下游': [
                {'name': '整车制造', 'companies': ['比亚迪', '特斯拉', '蔚来', '小鹏', '理想'], 'symbol_map': {'比亚迪': '002594.SZ', '特斯拉': 'TSLA', '蔚来': 'NIO', '小鹏': 'XPEV', '理想': 'LI'}},
                {'name': '充电设备', 'companies': ['特锐德', '星星充电', '万马股份'], 'symbol_map': {'特锐德': '300001.SZ', '万马股份': '002276.SZ'}},
                {'name': '换电服务', 'companies': ['蔚来', '奥动新能源', '协鑫能科'], 'symbol_map': {'蔚来': 'NIO', '协鑫能科': '002015.SZ'}}
            ],
            '潜力股': [
                {'name': '容百科技', 'symbol': '688005.SS', 'reason': '高镍正极材料龙头，技术领先', 'potential': '高'},
                {'name': '当升科技', 'symbol': '300073.SZ', 'reason': '正极材料技术领先，客户优质', 'potential': '高'},
                {'name': '中创新航', 'symbol': '03931.HK', 'reason': '二线电池厂商崛起，增长迅速', 'potential': '高'},
                {'name': '科达利', 'symbol': '002850.SZ', 'reason': '锂电池结构件龙头', 'potential': '中高'},
                {'name': '先导智能', 'symbol': '300450.SZ', 'reason': '锂电设备龙头，受益于扩产潮', 'potential': '中高'},
                {'name': '利元亨', 'symbol': '688499.SS', 'reason': '锂电设备新星，技术过硬', 'potential': '中高'}
            ]
        }
    },
    '光伏': {
        'description': '光伏产业成本持续下降，成为最具竞争力的清洁能源',
        'trend': '上升',
        'drivers': ['碳中和目标', '成本下降', '技术进步', '全球装机增长'],
        'challenges': ['产能过剩', '价格竞争', '政策补贴退坡'],
        'investment_themes': ['N型技术', 'TOPCon', 'HJT', '钙钛矿'],
        'subsectors': ['硅料', '硅片', '电池片', '组件', '逆变器'],
        'characteristics': ['成本驱动', '技术迭代快', '全球化'],
        'key_metrics': ['装机量', '转换效率', '成本下降幅度', '毛利率'],
        'risks': ['产能过剩', '价格战', '贸易摩擦'],
        'chain': {
            '上游': [
                {'name': '硅料', 'companies': ['通威股份', '大全能源', '协鑫科技'], 'symbol_map': {'通威股份': '600438.SS', '大全能源': '688303.SS', '协鑫科技': '03800.HK'}},
                {'name': '硅片', 'companies': ['隆基绿能', '中环股份', '晶科能源'], 'symbol_map': {'隆基绿能': '601012.SS', '中环股份': '002129.SZ', '晶科能源': '688223.SS'}},
                {'name': '银浆', 'companies': ['帝科股份', '苏州固锝'], 'symbol_map': {'帝科股份': '300842.SZ', '苏州固锝': '002079.SZ'}}
            ],
            '中游': [
                {'name': '电池片', 'companies': ['通威股份', '爱旭股份', '晶科能源'], 'symbol_map': {'通威股份': '600438.SS', '爱旭股份': '600732.SS', '晶科能源': '688223.SS'}},
                {'name': '组件', 'companies': ['晶科能源', '晶澳科技', '天合光能'], 'symbol_map': {'晶科能源': '688223.SS', '晶澳科技': '002459.SZ', '天合光能': '688599.SS'}},
                {'name': '逆变器', 'companies': ['阳光电源', '锦浪科技', '固德威'], 'symbol_map': {'阳光电源': '300274.SZ', '锦浪科技': '300763.SZ', '固德威': '688390.SS'}}
            ],
            '下游': [
                {'name': 'EPC', 'companies': ['中国电建', '特变电工', '东方日升'], 'symbol_map': {'中国电建': '601669.SS', '特变电工': '600089.SS', '东方日升': '300118.SZ'}},
                {'name': '储能', 'companies': ['阳光电源', '派能科技', '宁德时代'], 'symbol_map': {'阳光电源': '300274.SZ', '派能科技': '688063.SS', '宁德时代': '300750.SZ'}},
                {'name': '运营', 'companies': ['龙源电力', '华能国际', '大唐发电'], 'symbol_map': {'龙源电力': '001289.SZ', '华能国际': '600011.SS', '大唐发电': '601991.SS'}}
            ],
            '潜力股': [
                {'name': '钧达股份', 'symbol': '002865.SZ', 'reason': '转型TOPCon电池，业绩爆发', 'potential': '高'},
                {'name': '沐邦高科', 'symbol': '603398.SS', 'reason': '转型光伏，钙钛矿布局', 'potential': '高'},
                {'name': '迈为股份', 'symbol': '300751.SZ', 'reason': 'HJT设备龙头', 'potential': '中高'},
                {'name': '捷佳伟创', 'symbol': '300724.SZ', 'reason': '光伏设备全产业链布局', 'potential': '中高'},
                {'name': '金辰股份', 'symbol': '603396.SS', 'reason': 'TOPCon设备领先', 'potential': '中高'}
            ]
        }
    },
    '人工智能': {
        'description': 'AI技术快速发展，赋能各行各业',
        'trend': '上升',
        'drivers': ['大模型突破', '算力需求爆发', '应用场景扩展'],
        'challenges': ['算力瓶颈', '数据安全', '监管政策'],
        'investment_themes': ['大模型', '算力芯片', '数据中心', 'AI应用'],
        'subsectors': ['算力硬件', '软件平台', '垂直应用'],
        'characteristics': ['技术密集', '高投入', '快速迭代'],
        'key_metrics': ['研发投入', '模型性能', '应用落地'],
        'risks': ['技术路线风险', '估值过高', '竞争激烈'],
        'chain': {
            '上游': [
                {'name': 'GPU芯片', 'companies': ['英伟达', 'AMD', '寒武纪'], 'symbol_map': {'英伟达': 'NVDA', 'AMD': 'AMD', '寒武纪': '688256.SS'}},
                {'name': 'AI芯片', 'companies': ['海光信息', '景嘉微', '华为'], 'symbol_map': {'海光信息': '688041.SS', '景嘉微': '300474.SZ'}},
                {'name': '光模块', 'companies': ['中际旭创', '新易盛', '天孚通信'], 'symbol_map': {'中际旭创': '300308.SZ', '新易盛': '300502.SZ', '天孚通信': '300394.SZ'}},
                {'name': '服务器', 'companies': ['浪潮信息', '中科曙光', '新华三'], 'symbol_map': {'浪潮信息': '000977.SZ', '中科曙光': '603019.SS'}}
            ],
            '中游': [
                {'name': '大模型', 'companies': ['百度', '阿里', '腾讯', '字节'], 'symbol_map': {'百度': 'BIDU', '阿里': 'BABA', '腾讯': '00700.HK', '字节': 'private'}},
                {'name': 'AI平台', 'companies': ['科大讯飞', '商汤', '云从科技'], 'symbol_map': {'科大讯飞': '002230.SZ', '商汤': '0020.HK', '云从科技': '688327.SS'}},
                {'name': '数据服务', 'companies': ['海天瑞声', '中文在线', '人民网'], 'symbol_map': {'海天瑞声': '688787.SS', '中文在线': '300364.SZ', '人民网': '603000.SS'}}
            ],
            '下游': [
                {'name': 'AI应用', 'companies': ['金山办公', '万兴科技', '同花顺'], 'symbol_map': {'金山办公': '688111.SS', '万兴科技': '300624.SZ', '同花顺': '300033.SZ'}},
                {'name': '智能驾驶', 'companies': ['德赛西威', '中科创达', '四维图新'], 'symbol_map': {'德赛西威': '002920.SZ', '中科创达': '300496.SZ', '四维图新': '002405.SZ'}},
                {'name': '智能制造', 'companies': ['汇川技术', '机器人', '拓斯达'], 'symbol_map': {'汇川技术': '300124.SZ', '机器人': '300024.SZ', '拓斯达': '300607.SZ'}}
            ],
            '潜力股': [
                {'name': '鸿博股份', 'symbol': '002229.SZ', 'reason': '英伟达合作，算力租赁业务爆发', 'potential': '高'},
                {'name': '工业富联', 'symbol': '601138.SS', 'reason': 'AI服务器代工龙头', 'potential': '高'},
                {'name': '浪潮信息', 'symbol': '000977.SZ', 'reason': 'AI服务器龙头，订单饱满', 'potential': '高'},
                {'name': '中际旭创', 'symbol': '300308.SZ', 'reason': '800G光模块龙头', 'potential': '中高'},
                {'name': '科大讯飞', 'symbol': '002230.SZ', 'reason': '国内AI龙头，多模态突破', 'potential': '中高'}
            ]
        }
    },
    '半导体': {
        'description': '国产替代加速，半导体产业链自主可控',
        'trend': '上升',
        'drivers': ['国产替代', 'AI需求', '政策支持'],
        'challenges': ['技术壁垒', '设备依赖', '人才短缺'],
        'investment_themes': ['设备材料', '芯片设计', '先进封装', 'CPO', 'PCB'],
        'subsectors': ['设计', '制造', '封测', '设备', '材料', 'CPO', 'PCB'],
        'characteristics': ['资本密集', '技术壁垒高', '长周期'],
        'key_metrics': ['技术节点', '产能利用率', '毛利率'],
        'risks': ['技术落后', '制裁风险', '产能过剩'],
        'chain': {
            '上游': [
                {'name': '半导体设备', 'companies': ['北方华创', '中微公司', '精测电子'], 'symbol_map': {'北方华创': '002371.SZ', '中微公司': '688012.SS', '精测电子': '300567.SZ'}},
                {'name': '半导体材料', 'companies': ['沪硅产业', '中环股份', '江丰电子'], 'symbol_map': {'沪硅产业': '688126.SS', '中环股份': '002129.SZ', '江丰电子': '300666.SZ'}},
                {'name': '光刻胶', 'companies': ['南大光电', '容大感光', '晶瑞股份'], 'symbol_map': {'南大光电': '300346.SZ', '容大感光': '300576.SZ', '晶瑞股份': '300655.SZ'}}
            ],
            '中游': [
                {'name': '芯片设计', 'companies': ['海思', '紫光展锐', '卓胜微', '圣邦股份', '寒武纪'], 'symbol_map': {'卓胜微': '300782.SZ', '圣邦股份': '300661.SZ', '寒武纪': '688256.SS'}},
                {'name': '晶圆制造', 'companies': ['中芯国际', '华虹半导体', '华润微'], 'symbol_map': {'中芯国际': '688981.SS', '华虹半导体': '688347.SS', '华润微': '688396.SS'}},
                {'name': '封装测试', 'companies': ['长电科技', '通富微电', '华天科技'], 'symbol_map': {'长电科技': '600584.SS', '通富微电': '002156.SZ', '华天科技': '002185.SZ'}},
                {'name': 'CPO', 'companies': ['中际旭创', '新易盛', '天孚通信', '光迅科技'], 'symbol_map': {'中际旭创': '300308.SZ', '新易盛': '300502.SZ', '天孚通信': '300394.SZ', '光迅科技': '002281.SZ'}},
                {'name': 'PCB', 'companies': ['深南电路', '沪电股份', '生益科技', '景旺电子'], 'symbol_map': {'深南电路': '002916.SZ', '沪电股份': '002463.SZ', '生益科技': '600183.SS', '景旺电子': '603228.SS'}}
            ],
            '下游': [
                {'name': '消费电子', 'companies': ['苹果', '华为', '小米', 'OPPO'], 'symbol_map': {'苹果': 'AAPL', '华为': 'private', '小米': '01810.HK', 'OPPO': 'private'}},
                {'name': '汽车电子', 'companies': ['德赛西威', '均胜电子', '华阳集团'], 'symbol_map': {'德赛西威': '002920.SZ', '均胜电子': '600699.SS', '华阳集团': '002906.SZ'}},
                {'name': '工业控制', 'companies': ['汇川技术', '信捷电气', '禾川科技'], 'symbol_map': {'汇川技术': '300124.SZ', '信捷电气': '603416.SS', '禾川科技': '688320.SS'}}
            ],
            '潜力股': [
                {'name': '北方华创', 'symbol': '002371.SZ', 'reason': '半导体设备龙头，国产替代核心', 'potential': '高'},
                {'name': '中微公司', 'symbol': '688012.SS', 'reason': '刻蚀设备领先', 'potential': '高'},
                {'name': '中际旭创', 'symbol': '300308.SZ', 'reason': 'CPO龙头，800G光模块需求爆发', 'potential': '高'},
                {'name': '深南电路', 'symbol': '002916.SZ', 'reason': 'PCB龙头，受益AI服务器需求', 'potential': '高'},
                {'name': '寒武纪', 'symbol': '688256.SS', 'reason': 'AI芯片设计，国产替代', 'potential': '中高'},
                {'name': '沪硅产业', 'symbol': '688126.SS', 'reason': '大硅片国产替代', 'potential': '中高'}
            ]
        }
    },
    '医药': {
        'description': '老龄化加剧，创新药和医疗服务需求增长',
        'trend': '上升',
        'drivers': ['老龄化', '创新药研发', '消费升级'],
        'challenges': ['集采压力', '研发失败', '医保控费'],
        'investment_themes': ['创新药', 'CXO', '医疗器械', '医疗服务', '中药创新'],
        'subsectors': ['创新药', '仿制药', 'CXO', '医疗器械', '中药', '医疗服务'],
        'characteristics': ['研发周期长', '高风险高回报', '政策敏感'],
        'key_metrics': ['研发管线', '临床试验进展', '毛利率'],
        'risks': ['集采', '研发失败', '政策变化'],
        'chain': {
            '上游': [
                {'name': '原料药', 'companies': ['华海药业', '九州药业', '天宇股份'], 'symbol_map': {'华海药业': '600521.SS', '九州药业': '603456.SS', '天宇股份': '300702.SZ'}},
                {'name': '医药中间体', 'companies': ['凯莱英', '博腾股份', '九洲药业'], 'symbol_map': {'凯莱英': '002821.SZ', '博腾股份': '300363.SZ', '九洲药业': '603456.SS'}},
                {'name': '药用辅料', 'companies': ['山河药辅', '尔康制药', '黄山胶囊'], 'symbol_map': {'山河药辅': '300452.SZ', '尔康制药': '300267.SZ', '黄山胶囊': '002817.SZ'}}
            ],
            '中游': [
                {'name': '创新药', 'companies': ['恒瑞医药', '百济神州', '信达生物', '君实生物', '科伦药业', '石药集团'], 'symbol_map': {'恒瑞医药': '600276.SS', '百济神州': '688235.SS', '信达生物': '01801.HK', '君实生物': '688180.SS', '科伦药业': '002422.SZ'}},
                {'name': 'CXO', 'companies': ['药明康德', '康龙化成', '泰格医药', '凯莱英'], 'symbol_map': {'药明康德': '603259.SS', '康龙化成': '300759.SZ', '泰格医药': '300347.SZ', '凯莱英': '002821.SZ'}},
                {'name': '医疗器械', 'companies': ['迈瑞医疗', '乐普医疗', '微创医疗', '联影医疗'], 'symbol_map': {'迈瑞医疗': '300760.SZ', '乐普医疗': '300003.SZ', '微创医疗': '00853.HK', '联影医疗': '688271.SS'}},
                {'name': '中药', 'companies': ['片仔癀', '云南白药', '同仁堂', '华润三九'], 'symbol_map': {'片仔癀': '600436.SS', '云南白药': '000538.SZ', '同仁堂': '600085.SS', '华润三九': '000999.SZ'}}
            ],
            '下游': [
                {'name': '医院', 'companies': ['爱尔眼科', '通策医疗', '国际医学'], 'symbol_map': {'爱尔眼科': '300015.SZ', '通策医疗': '600763.SS', '国际医学': '000516.SZ'}},
                {'name': '药店', 'companies': ['益丰药房', '大参林', '老百姓', '一心堂'], 'symbol_map': {'益丰药房': '603939.SS', '大参林': '603233.SS', '老百姓': '603883.SS', '一心堂': '002727.SZ'}},
                {'name': '互联网医疗', 'companies': ['平安好医生', '阿里健康', '京东健康'], 'symbol_map': {'平安好医生': '01833.HK', '阿里健康': '00241.HK', '京东健康': '06618.HK'}}
            ],
            '潜力股': [
                {'name': '药明康德', 'symbol': '603259.SS', 'reason': 'CXO龙头，全球竞争力', 'potential': '高'},
                {'name': '迈瑞医疗', 'symbol': '300760.SZ', 'reason': '医疗器械龙头，多元化布局', 'potential': '高'},
                {'name': '百济神州', 'symbol': '688235.SS', 'reason': '创新药龙头，全球化研发', 'potential': '高'},
                {'name': '联影医疗', 'symbol': '688271.SS', 'reason': '高端医疗设备国产替代', 'potential': '高'},
                {'name': '爱尔眼科', 'symbol': '300015.SZ', 'reason': '眼科医疗服务龙头', 'potential': '中高'},
                {'name': '康龙化成', 'symbol': '300759.SZ', 'reason': 'CXO二线龙头，增长快', 'potential': '中高'}
            ]
        }
    },
    '消费': {
        'description': '消费复苏，品牌化和高端化趋势明显，家电出口受益于海外需求',
        'trend': '上升',
        'drivers': ['消费复苏', '品牌升级', '国货崛起', '海外市场拓展'],
        'challenges': ['消费疲软', '竞争激烈', '成本上升'],
        'investment_themes': ['高端消费', '国货品牌', '必选消费', '家电出口'],
        'subsectors': ['食品饮料', '家电', '服装', '零售'],
        'characteristics': ['品牌溢价', '渠道重要', '周期性'],
        'key_metrics': ['品牌力', '渠道覆盖', '毛利率', '出口增长率'],
        'risks': ['消费疲软', '成本压力', '食品安全'],
        'chain': {
            '上游': [
                {'name': '农产品', 'companies': ['牧原股份', '温氏股份', '新希望'], 'symbol_map': {'牧原股份': '002714.SZ', '温氏股份': '300498.SZ', '新希望': '000876.SZ'}},
                {'name': '食品原料', 'companies': ['海天味业', '中粮糖业', '保龄宝'], 'symbol_map': {'海天味业': '603288.SS', '中粮糖业': '600737.SS', '保龄宝': '002286.SZ'}},
                {'name': '包装材料', 'companies': ['裕同科技', '合兴包装', '宝钢包装'], 'symbol_map': {'裕同科技': '002831.SZ', '合兴包装': '002228.SZ', '宝钢包装': '601968.SS'}}
            ],
            '中游': [
                {'name': '白酒', 'companies': ['贵州茅台', '五粮液', '泸州老窖', '洋河股份'], 'symbol_map': {'贵州茅台': '600519.SS', '五粮液': '000858.SZ', '泸州老窖': '000568.SZ', '洋河股份': '002304.SZ'}},
                {'name': '食品', 'companies': ['伊利股份', '蒙牛乳业', '农夫山泉'], 'symbol_map': {'伊利股份': '600887.SS', '蒙牛乳业': '02319.HK', '农夫山泉': '09633.HK'}},
                {'name': '家电', 'companies': ['美的集团', '格力电器', '海尔智家'], 'symbol_map': {'美的集团': '000333.SZ', '格力电器': '000651.SZ', '海尔智家': '600690.SS'}}
            ],
            '下游': [
                {'name': '电商平台', 'companies': ['阿里巴巴', '京东', '拼多多'], 'symbol_map': {'阿里巴巴': 'BABA', '京东': 'JD', '拼多多': 'PDD'}},
                {'name': '线下零售', 'companies': ['永辉超市', '步步高', '红旗连锁'], 'symbol_map': {'永辉超市': '601933.SS', '步步高': '002251.SZ', '红旗连锁': '002697.SZ'}},
                {'name': '品牌零售', 'companies': ['李宁', '安踏', '波司登'], 'symbol_map': {'李宁': '02331.HK', '安踏': '02020.HK', '波司登': '03998.HK'}}
            ],
            '潜力股': [
                {'name': '美的集团', 'symbol': '000333.SZ', 'reason': '欧洲高温推动空调出口激增，海外收入创新高', 'potential': '高'},
                {'name': '格力电器', 'symbol': '000651.SZ', 'reason': '加码海外市场布局，欧洲战略成效显著', 'potential': '高'},
                {'name': '海尔智家', 'symbol': '600690.SS', 'reason': '欧洲市场份额持续提升，全球化布局完善', 'potential': '中高'},
                {'name': '舍得酒业', 'symbol': '600702.SS', 'reason': '老酒概念，次高端崛起', 'potential': '中高'},
                {'name': '今世缘', 'symbol': '603369.SS', 'reason': '国缘系列增长强劲', 'potential': '中高'}
            ]
        }
    }
}

def get_industry_chains():
    return list(industry_chains.keys())

def get_industry_data(industry_name):
    return industry_chains.get(industry_name, None)

def find_potential_stocks(industry_name=None):
    if industry_name:
        industry = industry_chains.get(industry_name)
        if industry:
            return industry['chain']['潜力股']
        return []
    
    all_potential = []
    for industry_name, industry_data in industry_chains.items():
        for stock in industry_data['chain']['潜力股']:
            stock['industry'] = industry_name
            all_potential.append(stock)
    
    all_potential.sort(key=lambda x: {'高': 3, '中高': 2, '中': 1}[x['potential']], reverse=True)
    return all_potential

def analyze_chain(industry_name):
    industry = industry_chains.get(industry_name)
    if not industry:
        return None
    
    analysis = {
        'name': industry_name,
        'description': industry['description'],
        'trend': industry['trend'],
        'drivers': industry['drivers'],
        'challenges': industry['challenges'],
        'investment_themes': industry['investment_themes'],
        'chain_overview': {
            '上游': [item['name'] for item in industry['chain']['上游']],
            '中游': [item['name'] for item in industry['chain']['中游']],
            '下游': [item['name'] for item in industry['chain']['下游']]
        },
        'potential_stocks': industry['chain']['潜力股']
    }
    
    return analysis
