import os
from PIL import Image, ImageDraw, ImageFont

# когда нибудь я спрячу этот токен
TOKEN = '7101800623:AAFlmBM0IRUAiRbGAGOx85Z4e6EE5IU4yec'
TEMP_DIR = 'temp'
os.makedirs(TEMP_DIR, exist_ok=True)

# эти тоже мб
RAPID_API_KEY = "c4ab1c58f5msh2b1e0f65b6f2548p16f6bbjsn1e698d6b9969"  
RAPID_API_HOST = "tiktok-download-without-watermark.p.rapidapi.com"
COINMARKETCAP_KEY = "652e153f-9bb3-435d-a9f5-1076ac6c428d"

# этапы диалога с юзером после команды /ddos
ASKING, COUNTING = 0, 1

# этапы диалога с юзером после команды /wpm
AWAITING_USER_INPUT = 2
AWAITING_USER_INPUT_ANTICHEAT = 3

# этапы диалога с юзером после команды /prank
AWAITING_USER_INPUT_PRANK = 4

# этапы диалога с юзером после команды /21
AWAITING_USER_INPUT_21 = 5

# этапы диалога с юзером после команды /2048
WAITING_FOR_2048_MOVE = 6

text1 = '''Космос — это бескрайний и таинственный мир, который привлекал внимание человечества с древнейших времен. Люди всегда стремились понять, что находится за пределами нашей планеты. Сначала они наблюдали звезды и планеты с помощью своих глаз, а затем начали разрабатывать инструменты для изучения Вселенной. Современные телескопы позволяют заглядывать в самые отдаленные уголки космоса. 
Мы можем наблюдать галактики, звезды, планеты и другие небесные объекты, находящиеся на расстоянии миллионов световых лет от Земли. Каждая новая находка расширяет наши знания о космосе и помогает лучше понять его структуру.Важным этапом в изучении космоса стало отправление космических аппаратов за пределы нашей планеты. Появление спутников и межпланетных зондов позволило людям не только наблюдать космические объекты издалека, но и исследовать их вблизи. 
Например, аппараты NASA смогли передать уникальные данные о поверхности Марса и других планет Солнечной системы. Кроме того, развитие технологий привело к созданию космических кораблей, на которых человек может отправиться в космос. Первым человеком, покорившим космос, стал Юрий Гагарин. Его полет в 1961 году ознаменовал начало новой эры в исследовании Вселенной. Сегодня международные космические станции позволяют астронавтам жить и работать на орбите Земли.
Космос также вдохновляет на создание множества теорий о происхождении Вселенной и ее будущем. Согласно современной науке, наша Вселенная возникла около 13,8 миллиарда лет назад в результате Большого взрыва. С тех пор она продолжает расширяться, и ученые до сих пор пытаются понять, каким образом это расширение происходит и к чему оно приведет. Одна из самых интересных загадок космоса — это черные дыры. 
Эти объекты обладают настолько сильным гравитационным притяжением, что даже свет не может покинуть их пределы. Черные дыры играют важную роль в формировании галактик и могут быть ключом к пониманию структуры Вселенной. Исследование космоса — это не только способ удовлетворить наше любопытство, но и возможность найти ответы на важнейшие вопросы, связанные с жизнью и существованием человечества. 
Возможно, в будущем мы сможем найти доказательства существования жизни на других планетах, колонизировать Марс или даже выйти за пределы Солнечной системы. Космос — это место, где наши мечты становятся реальностью, и каждый новый шаг в его изучении открывает перед нами бесконечные возможности для будущего.'''

text2 = '''Технологии стали неотъемлемой частью нашей повседневной жизни, кардинально изменив способы общения, работы и обучения. Всего несколько десятилетий назад трудно было представить, что мы сможем мгновенно связываться с людьми по всему миру, находясь за сотни тысяч километров друг от друга. Интернет, появившийся в конце 20 века, полностью трансформировал наше общество, сделав информацию доступной в любом уголке земного шара. Вместе с развитием интернет-технологий появились смартфоны, планшеты и компьютеры, которые сегодня стали для нас чем-то само собой разумеющимся. Мы можем получать новости в режиме реального времени, смотреть фильмы, обучаться новым навыкам, не выходя из дома, и работать удалённо, общаясь с коллегами через видеоконференции.
Однако стоит задуматься о том, как быстро эти технологии ворвались в нашу жизнь и изменили её. Компьютеры, которые в середине 20 века занимали целые комнаты и использовались лишь для сложнейших вычислений, сегодня легко умещаются в кармане и обладают мощностью, о которой раньше можно было только мечтать. Современные смартфоны выполняют миллиарды операций в секунду и позволяют нам использовать искусственный интеллект, который ещё недавно казался чем-то фантастическим. Искусственный интеллект стал активно применяться в таких сферах, как медицина, наука, искусство, образование и даже сельское хозяйство. Машины теперь способны анализировать огромное количество данных и принимать решения на их основе с точностью, которая недоступна человеку. Диагностика болезней, финансовые прогнозы, управление производственными процессами — всё это становится проще благодаря новым алгоритмам и вычислительным мощностям.
Однако с прогрессом приходят и вызовы. Рост зависимости от технологий ставит перед нами важные вопросы: как мы будем регулировать использование искусственного интеллекта? Какие меры необходимо предпринять для защиты данных и конфиденциальности пользователей? Кибербезопасность становится одной из главных тем в мире технологий. С увеличением числа устройств, подключённых к интернету, возрастает и количество потенциальных угроз, связанных с утечкой данных, мошенничеством и взломами. Защита данных становится приоритетом для компаний и государственных учреждений, так как атаки хакеров могут нарушить работу целых систем, начиная от банковских операций и заканчивая системами управления инфраструктурой городов. В ответ на это разрабатываются всё более сложные и продвинутые системы шифрования и защиты, которые должны обеспечить безопасность пользователей в цифровом мире.
Невозможно не отметить также, как сильно технологии влияют на наше восприятие мира и самих себя. Социальные сети стали основной платформой для общения, обмена идеями и новостями. Они позволяют людям из разных уголков планеты находить единомышленников, делиться своими мыслями и создавать целые сообщества. Но одновременно с этим социальные сети порождают новые вызовы, такие как кибербуллинг, дезинформация и чрезмерная зависимость от виртуального мира. Многих волнует вопрос о том, как цифровые технологии влияют на наше психическое здоровье, уровень стресса и концентрацию внимания. Мы живём в эпоху, когда информация доступна буквально на расстоянии одного клика, и это меняет наши когнитивные процессы, заставляя нас привыкать к многозадачности и быстрому переключению между задачами.
Также стоит отметить развитие робототехники и её влияние на промышленность и повседневную жизнь. Роботы уже давно используются на заводах и фабриках, где они выполняют рутинные и опасные задачи с невероятной точностью и скоростью. Однако в последние годы роботы всё активнее входят в нашу повседневную жизнь. Автономные роботы-пылесосы, дроны, доставляющие товары, и даже роботы-ассистенты в больницах и гостиницах — всё это стало реальностью. Развитие технологий в области робототехники открывает перед нами огромные перспективы, но также заставляет задуматься о будущем труда. Как изменится рынок труда, когда роботы начнут выполнять всё больше задач, которые раньше выполнялись людьми? Этот вопрос уже вызывает дискуссии среди экономистов и социальных аналитиков. Возможно, в будущем многие профессии, которые сегодня считаются обычными, исчезнут или трансформируются, создавая новые вызовы для работников.
Технологический прогресс также меняет подход к образованию. Онлайн-курсы, образовательные платформы и виртуальная реальность делают обучение доступным для миллионов людей по всему миру. Технологии позволяют получать знания в любой точке мира, независимо от места проживания или финансовых возможностей. Теперь любой человек, имеющий доступ к интернету, может пройти курсы от ведущих университетов мира, изучить программирование, дизайн или научиться новому языку. Это демократизирует образование и открывает новые горизонты для тех, кто ранее не имел возможности учиться в престижных образовательных учреждениях.
Мы находимся на пороге новых открытий, которые в ближайшие десятилетия могут полностью изменить наше представление о мире. Развитие квантовых компьютеров, которые способны решать задачи, недоступные обычным компьютерам, может привести к революции в таких областях, как фармацевтика, экология и материалы. Виртуальная и дополненная реальность, которая сегодня используется в основном для развлечений, в будущем может стать важным инструментом в медицине, образовании и архитектуре. Технологии продолжают удивлять нас своими возможностями, и хотя мы не можем точно предсказать, куда нас приведёт этот путь, одно можно сказать с уверенностью: будущее будет наполнено новыми открытиями и инновациями, которые изменят наш мир.'''

text3 = '''Путешествия всегда играли важную роль в жизни человека, начиная с древних времён, когда люди покидали свои дома в поисках новых земель, пропитания и ресурсов. В те времена, когда неизвестность была опасной и полной загадок, каждый шаг мог оказаться решающим. Исследователи и мореплаватели, такие как Христофор Колумб, Марко Поло и Фернан Магеллан, отправлялись в дальние путешествия, открывая новые континенты и торговые пути. Они преодолевали океаны, боролись с бурями, нехваткой пищи и пресной воды, неизвестными болезнями и, конечно же, страхом перед неизвестным. Но именно благодаря их смелости, настойчивости и жажде знаний мир расширился, и новые территории стали частью глобальной цивилизации. Открытие Америки, кругосветные плавания и поиски пути в Индию изменили ход истории и заложили основу для современных путешествий.
В наши дни путешествия стали более комфортными и безопасными. Самолёты, поезда, автомобили и корабли позволяют за считанные часы пересекать огромные расстояния, которые раньше занимали месяцы. Современные технологии значительно упростили процесс перемещения: теперь достаточно пары кликов, чтобы забронировать билет на другой конец света. Но, несмотря на это, дух открытий не исчез. Люди по-прежнему стремятся увидеть что-то новое, познать неизвестное и выйти за пределы повседневной рутины. Путешествия дарят уникальный опыт: возможность увидеть природные чудеса, познакомиться с культурами других народов, попробовать необычную еду и понять, насколько разнообразен и удивителен наш мир.
Однажды побывав в диких джунглях Амазонки или на заснеженных вершинах Гималаев, человек осознаёт, что мир гораздо больше и многограннее, чем можно представить, глядя на карту или экран компьютера. Живое общение с природой и её обитателями, встреча с людьми, чьи обычаи и традиции сильно отличаются от привычных, — всё это помогает переосмыслить свою жизнь и взгляды. Путешествия также учат терпению и гибкости, так как не всегда всё идёт по плану. Природа может преподнести сюрпризы, погода — измениться, и тогда приходится находить решения на ходу, что делает каждый такой опыт незабываемым.
Не стоит забывать и о том, как важны путешествия для научных исследований. Учёные, отправляющиеся в экспедиции, открывают новые виды животных и растений, изучают климатические изменения, проводят археологические раскопки. Каждый новый шаг в неизведанную область даёт человечеству больше знаний о планете, на которой мы живём. В частности, исследования полярных регионов Земли, океанских глубин и высокогорных районов позволяют нам лучше понимать, как меняется климат, как эволюционировали различные виды и как устроен наш мир на фундаментальном уровне. Это помогает находить решения для борьбы с экологическими проблемами и осознавать важность сохранения природного наследия для будущих поколений.
Современные технологии, такие как спутниковая навигация и беспилотные летательные аппараты, облегчают исследования, но ничто не может заменить непосредственного участия человека в процессе. Только тот, кто побывал на месте, может по-настоящему ощутить всю величественность природных явлений или историческую значимость археологических находок. Путешествия становятся неотъемлемой частью жизни каждого человека, желающего не только узнать больше о мире, но и открыть что-то новое в самом себе. Мы движемся вперёд, открывая всё новые горизонты, и каждое новое путешествие, будь то в соседний город или на другой континент, становится шагом к расширению нашего мировоззрения и осознанию того, как много ещё предстоит узнать.'''
 
all_texts = [text1, text2, text3]

image_text_map = {
    "https://cdn.discordapp.com/attachments/1231705311656546358/1297222788385345556/image.png?ex=6715245d&is=6713d2dd&hm=efb4a36b41de06bacb2ebfeca629617913089dd30b01f690c4417c08c09e3356&": "Сегодня ясное небо, и солнце светит особенно ярко, заливая город тёплым светом. Птицы поют на деревьях, наполняя воздух мелодичными звуками и добавляя ощущение спокойствия.",
    "https://cdn.discordapp.com/attachments/1231705311656546358/1297222632789377058/image.png?ex=67152438&is=6713d2b8&hm=ba65c4967a37332eb534e91269fe6ccf6e26418a7f47475db0c9d8fa1c34dcfa&": "Кошка тихо спала на подоконнике, наблюдая за миром с высоты, будто она хозяйка всего, что видит. Вечерний свет золотил её шерсть, создавая мягкие тени, которые придавали комнате особую атмосферу.",
    "https://cdn.discordapp.com/attachments/1231705311656546358/1297218873887555648/image.png?ex=671520b8&is=6713cf38&hm=59081a190eea0eebc9e706f2e9e1e3ba3c66e58703ea82520ebbf44b4a25cdfc&": "В лесу было тихо, лишь изредка доносился шорох листвы, и редкие лучи солнца пробивались сквозь кроны деревьев. Деревья стояли неподвижно, словно охраняли свои древние тайны, скрытые от посторонних глаз."
}

game_deck = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'Валет': 10, 'Дама': 10, 'Король': 10, 'Туз': 11}   

tiles = [2, 2, 2, 2, 2, 2, 2, 2, 2, 4]

board_2048 = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]

BOARD_SIZE = 400
CELL_SIZE = BOARD_SIZE // 4
FONT_SIZE = 40
BACKGROUND_COLOR = (205, 193, 180)
BORDER_COLOR = (160, 140, 120)

COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

FONT = ImageFont.truetype("arial.ttf", FONT_SIZE)

symbol_list = (
    ["🍒"] * 10 +  
    ["💎"] * 5 +   
    ["🔥"] * 3 +  
    ["🐉"] * 2 +   
    ["👑"] * 1     
)

photo_links = {
    "🍒": "https://cdn.discordapp.com/attachments/1231705311656546358/1321546613667135501/1f352.png?ex=676da1b1&is=676c5031&hm=7c84a25ff8a69d9e3bdab99b70016f822eb1ee4f8118aa471fcbbcbf3b3516e0&",
    "💎": "https://cdn.discordapp.com/attachments/1231705311656546358/1321546788334862387/1f48e.png?ex=676da1db&is=676c505b&hm=3d0ca9477363099801471fbdbd314d0f7a2c075bf578bb054747e402c45cab46&",
    "🔥": "https://cdn.discordapp.com/attachments/1231705311656546358/1321546840109486122/fire-emoji-402x512-8ma95d17.png?ex=676da1e7&is=676c5067&hm=a14a8ac66a9094a3bd65051b5072d07bf5ff099427075d16dc22543b00ea57c7&",
    "🐉": "https://cdn.discordapp.com/attachments/1231705311656546358/1321546890420158554/dragon-emoji-996x1024-t2d564c5.png?ex=676da1f3&is=676c5073&hm=02c205c78e918d88cb088bb3c3432fd3763c0985f4fb2ce7004224e227bb3b59&",
    "👑": "https://cdn.discordapp.com/attachments/1231705311656546358/1321546938708918372/crown-emoji-1024x920-upob12vs.png?ex=676da1ff&is=676c507f&hm=803343a566d69126873f6ef3aa07ac8361f2f4822bce3ac51f5a419b0c6d16e0&"
}